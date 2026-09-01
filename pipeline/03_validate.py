#!/usr/bin/env python3
"""Fail loudly on incomplete multipart loads, implausible totals, schema drift, or privacy leaks."""

from __future__ import annotations

import json
import re
from collections import Counter

import pandas as pd

from utils import CLEAN_DIR, DERIVED_DIR, LOADED_DIR, MAPPINGS_DIR


EXPECTED_FILES = {
    "citations_by_year.json", "publications_by_year_dept.json", "topics.json", "collab_countries.json",
    "lecturers_positions.json", "sinta_by_dept.json", "funding_by_year.json", "outreach_points.json",
    "sdg_matrix.json", "journals.json", "tck_2026_targets.json", "tck_2026_actuals.json",
    "tck_2026_anggaran.json", "tck_2026_joined.json", "value_model.json", "institution_snapshot.json",
    # Added with the 31 August 2026 refresh.
    "snapshot.json", "tck_2026_by_dept.json",
    "partnerships_by_year.json", "partnership_partners.json", "partnership_points.json",
    "partnership_coverage.json", "admissions_by_year.json", "active_students.json",
    "graduates_profile.json", "graduates_by_programme.json", "student_achievements.json",
    "scholarships.json", "accreditation.json", "exchange_students.json",
    "tracer_waiting_time.json", "tracer_sectors.json", "tracer_summary.json", "hpu_posbindu.json",
}
PRIVATE_KEYS = {
    "name", "nama", "name_backup", "nidn", "nip", "nika", "nim", "niu", "leader", "member", "authors",
    "first_author", "last_author", "corresponding_author", "scopus_id", "sinta_id", "google_scholar_id",
    "combined_table", "people",
    # Personal fields introduced by the academic, tracer, and Posbindu sources.
    "nama_peserta", "nama_lengkap", "nama_mahasiswa", "tanggal_lahir", "email", "telp", "telepon",
    "pic", "nama_pic", "alamat", "berat_badan", "tinggi_badan", "sistolik", "diastolik",
    "tekanan_darah", "gula_darah", "kolesterol", "asam_urat", "imt", "lingkar_perut",
}
# Percentage indicators whose TW3 cell holds a headcount instead of a percentage.
EXPECTED_UNIT_MISMATCH = {"5b", "8b1", "8b2", "8b3"}


def load_json(name: str):
    return json.loads((DERIVED_DIR / name).read_text(encoding="utf-8"))


def walk_keys(value, path="root"):
    if isinstance(value, dict):
        for key, child in value.items():
            yield path, str(key).lower()
            yield from walk_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_keys(child, f"{path}[{index}]")


def main() -> None:
    manifest = json.loads((LOADED_DIR / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["citations"]["rows_loaded"] == 25_300
    assert manifest["publications"]["rows_loaded"] == 2_726
    assert manifest["people"]["rows_loaded"] == 4_813

    missing_outputs = EXPECTED_FILES - {path.name for path in DERIVED_DIR.glob("*.json")}
    assert not missing_outputs, f"Output wajib hilang: {sorted(missing_outputs)}"

    citations = load_json("citations_by_year.json")
    citation_lookup = {int(row["year"]): int(row["citations"]) for row in citations}
    assert citation_lookup[2019] == 4_129
    assert citation_lookup[2021] == 7_175
    assert citation_lookup[2024] == 12_629
    assert sum(citation_lookup.values()) == 70_905
    assert sum(value for year, value in citation_lookup.items() if 2021 <= year <= 2025) == 46_930

    publications = pd.read_csv(CLEAN_DIR / "publications.csv")
    assert len(publications) == 2_726
    assert publications["year"].between(2020, 2025).all()
    assert int(publications["year"].between(2021, 2025).sum()) == 2_353

    funding = load_json("funding_by_year.json")
    funding_total = {int(row["year"]): float(row["amount"]) for row in funding if row["type"] == "Total"}
    assert round(funding_total[2021] / 1_000_000_000, 2) == 3.30
    assert round(funding_total[2024] / 1_000_000_000, 2) == 74.91

    outreach = pd.read_csv(CLEAN_DIR / "community_service.csv")
    assert len(outreach) == 1_610
    assert int(outreach["location_status"].eq("missing").sum()) == 619
    outreach_counts = outreach.groupby("year").size().to_dict()
    for year, expected in {2021: 109, 2022: 214, 2023: 279, 2024: 434, 2025: 445}.items():
        assert int(outreach_counts[year]) == expected, (year, outreach_counts.get(year), expected)

    sinta = load_json("sinta_by_dept.json")
    sinta_lookup = {row["department"]: row for row in sinta}
    assert sum(int(row["n"]) for row in sinta) == 205
    assert sum(float(row["total"]) for row in sinta) == 236_250
    assert sinta_lookup["Kimia"]["median"] == 1_765
    assert sinta_lookup["Matematika"]["median"] == 317

    institution = load_json("institution_snapshot.json")
    assert institution["lecturer_doctoral"] == 138

    collaborations = load_json("collab_countries.json")
    assert len(collaborations) == 61
    assert all(row["country"] != "Indonesia" for row in collaborations)

    value_model = load_json("value_model.json")
    assert value_model["metrics"]["mappable_outreach_n"] == 921
    assert value_model["metrics"]["raw_location_labels_n"] == 126

    # --- TCK 2026 (official workbook, 31 August 2026) ---
    tck = load_json("tck_2026_joined.json")
    assert len(tck) == 42
    by_no = {str(row["no"]): row for row in tck}
    statuses = Counter(row["status_kuartal"] for row in tck)
    assert set(statuses) <= {"tercapai", "mendekati", "tertinggal", "meleset"}
    assert sum(statuses.values()) == 42

    # Cross-checks against figures readable straight off the workbook.
    assert by_no["1a"]["capaian_tw3"] == 353
    assert by_no["9"]["capaian_tw3"] == 168
    assert by_no["30"]["capaian_tw3"] == 54
    assert round(by_no["1c"]["capaian_tw3"], 2) == 38.36, "1c harus dalam miliar rupiah"

    # Indicator 27 counts down: fewer teaching-only lecturers is better.
    assert by_no["27"]["arah"] == "turun" and by_no["27"]["status_kuartal"] == "tercapai"

    # Percentage indicators without a denominator must not publish a TW3 percentage.
    mismatched = {str(row["no"]) for row in tck if row["unit_mismatch"]}
    assert mismatched == EXPECTED_UNIT_MISMATCH, f"unit_mismatch tak terduga: {sorted(mismatched)}"
    for no in EXPECTED_UNIT_MISMATCH:
        row = by_no[no]
        assert row["capaian_tw3"] is None, f"{no}: capaian TW3 seharusnya kosong"
        assert row["capaian_tw3_cacah"] is not None, f"{no}: cacah TW3 hilang"
        assert row["kuartal_dinilai"] == "tw2", f"{no}: penilaian seharusnya jatuh ke TW2"

    # Quarterly actuals are cumulative for rising indicators. Violations are real
    # in the source, so they are reported rather than raised.
    quarter_anomalies = []
    for row in tck:
        if row.get("arah") == "turun":
            continue
        values = [row[f"capaian_tw{index}"] for index in (1, 2, 3)]
        values = [value for value in values if value is not None]
        if any(after < before for before, after in zip(values, values[1:])):
            quarter_anomalies.append({"no": str(row["no"]), "capaian": values})
    assert {row["no"] for row in quarter_anomalies} == {"1a", "15", "32"}, quarter_anomalies

    departments = load_json("tck_2026_by_dept.json")
    assert len(departments) == 30

    # --- Datasets added with this refresh ---
    partnerships = load_json("partnerships_by_year.json")
    assert sum(row["n"] for row in partnerships) == 263
    coverage = load_json("partnership_coverage.json")
    assert coverage["total"] == 263
    assert coverage["terpetakan"] + coverage["internasional"] + coverage["lokasi_kosong"] == 263

    admissions = load_json("admissions_by_year.json")
    assert sum(row["registrasi"] for row in admissions if row["tahun"] == 2026) == 844
    assert sum(row["peminat"] for row in admissions if row["tahun"] == 2022) == 13_657

    active = load_json("active_students.json")
    assert sum(row["mahasiswa"] for row in active) == 3_147

    achievements = load_json("student_achievements.json")
    assert sum(row["prestasi"] for row in achievements) == 1_600

    scholarships = load_json("scholarships.json")
    assert scholarships["total"] == 684

    accreditation = load_json("accreditation.json")
    assert accreditation["prodi_nasional"] == 18
    assert accreditation["prodi_unggul"] == by_no["3"]["capaian_tw3"] == 15
    assert accreditation["prodi_internasional"] == by_no["2a"]["capaian_tw3"] + by_no["2b"]["capaian_tw3"] == 15

    tracer = load_json("tracer_summary.json")
    assert tracer["responden"] == 573
    # The source workbook computes these itself; both must survive our pipeline.
    source_summary = manifest["tracer_waiting"]["summary_sumber"]
    assert round(tracer["rerata_bulan"], 2) == round(source_summary["rata_rata_bulan"], 2)
    assert tracer["dalam_6_bulan"] == 536

    posbindu = load_json("hpu_posbindu.json")
    assert posbindu["peserta_terdaftar"] == 651
    # Five sessions in 2026. The sheet labelled "Jan 26" duplicates Juli and must
    # not add a sixth; the real 30 January session comes from the consolidated
    # sheet, which is the only place it was recorded.
    assert [row["tanggal"] for row in posbindu["sesi"]] == [
        "2026-01-30", "2026-02-27", "2026-05-29", "2026-07-03", "2026-08-28"
    ]
    # The published universe is teaching and support staff only.
    assert posbindu["kunjungan"] == sum(row["peserta"] for row in posbindu["sesi"]) == 131
    assert {row["kriteria"] for row in posbindu["kunjungan_per_kriteria"]} == {"Dosen", "Tendik"}
    # Everything filtered out is still counted, so the universe stays legible.
    assert posbindu["kunjungan"] + sum(posbindu["dikecualikan"].values()) == 391

    # Every band must come from mappings/posbindu_risiko.csv. An unmapped source
    # label would otherwise fall through to "Tidak diperiksa" and read as a gap.
    bands = pd.read_csv(MAPPINGS_DIR / "posbindu_risiko.csv")
    mapped = {(str(row.indikator), str(row.nilai_sumber)): str(row.pita) for row in bands.itertuples()}
    allowed = set(mapped.values()) | {"Tidak diperiksa"}
    for measure in posbindu["profil_risiko"]:
        assert set(measure["pita"]) <= allowed, f"Pita tak dikenal pada {measure['indikator']}"
        assert sum(measure["pita"].values()) == posbindu["kunjungan"]

    # An interpretation column that slid left leaves numbers where labels belong.
    # This guard is permanent: the 3 July 2026 session arrived that way once.
    for session in posbindu["sesi"]:
        for key, distribution in session.items():
            if not key.startswith("distribusi_"):
                continue
            column = key.removeprefix("distribusi_")
            for label in distribution:
                assert not re.fullmatch(r"-?\d+(\.\d+)?", str(label)), (
                    f"Nilai numerik pada {key} sesi {session['tanggal']}: {label!r}. "
                    "Kolom interpretasi sumber kemungkinan bergeser."
                )
                assert (column, str(label)) in mapped or label == "Tidak diperiksa", (
                    f"Kategori {label!r} pada {key} belum ada di posbindu_risiko.csv"
                )

    for path in DERIVED_DIR.glob("*.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        leaks = [(location, key) for location, key in walk_keys(payload) if key in PRIVATE_KEYS]
        assert not leaks, f"Kunci privat di {path.name}: {leaks[:4]}"

    report = {
        "status": "lulus",
        "snapshot": load_json("snapshot.json"),
        "multipart": {name: manifest[name]["rows_loaded"] for name in ("citations", "publications", "people")},
        "derived_files": len(list(DERIVED_DIR.glob("*.json"))),
        "tck_indicators": len(tck),
        "tck_status": dict(statuses),
        "tck_unit_mismatch": sorted(mismatched),
        "anomali_kuartal": quarter_anomalies,
        "verified_anchors": {
            "citations_all_time": sum(citation_lookup.values()),
            "citations_2021_2025": sum(value for year, value in citation_lookup.items() if 2021 <= year <= 2025),
            "funding_2024_rp": funding_total[2024],
            "outreach_missing_location": int(outreach["location_status"].eq("missing").sum()),
            "kerja_sama_2021_2026": coverage["total"],
            "mahasiswa_aktif_s1": sum(row["mahasiswa"] for row in active),
            "responden_tracer": tracer["responden"],
            "kunjungan_posbindu": posbindu["kunjungan"],
        },
    }
    (LOADED_DIR.parent / "validation_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
