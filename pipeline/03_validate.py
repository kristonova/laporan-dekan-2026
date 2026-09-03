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
    # Added with the 2022-2025 Posbindu backfill.
    "hpu_posbindu_tahunan.json",
    # Added with the student roster (six intake cohorts, 2021-2026).
    "students_summary.json", "students_by_programme.json", "students_by_province.json",
    "students_by_pathway.json", "students_background.json", "students_cohort_outcome.json",
    "students_ipk.json", "students_access.json",
}
PRIVATE_KEYS = {
    "name", "nama", "name_backup", "nidn", "nip", "nika", "nim", "niu", "leader", "member", "authors",
    "first_author", "last_author", "corresponding_author", "scopus_id", "sinta_id", "google_scholar_id",
    "combined_table", "people",
    # Personal fields introduced by the academic, tracer, and Posbindu sources.
    "nama_peserta", "nama_lengkap", "nama_mahasiswa", "tanggal_lahir", "email", "telp", "telepon",
    "pic", "nama_pic", "alamat", "berat_badan", "tinggi_badan", "sistolik", "diastolik",
    "tekanan_darah", "gula_darah", "kolesterol", "asam_urat", "imt", "lingkar_perut",
    # Personal columns carried by the student roster workbooks.
    "wali", "nama_wali", "alamat_wali", "no_hp_wali", "alamat_ktp", "alamat_domisili",
    "email_ugm", "no_hp", "golongan_darah", "nim_mahasiswa",
}
# Counts below this are withheld in the student aggregates; see SMALL_CELL in
# 02_aggregate.py. The threshold is re-asserted here so a future change to the
# aggregation cannot quietly publish a one-person cell.
SMALL_CELL = 3
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


def walk_values(value, path="root"):
    """Yield (path, key, value) for every scalar under a JSON payload."""
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(child, (dict, list)):
                yield from walk_values(child, f"{path}.{key}")
            else:
                yield f"{path}.{key}", str(key).lower(), child
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_values(child, f"{path}[{index}]")


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
    # Tied to what the loader actually read, not to a literal that a legitimate
    # data refresh would turn into a false failure.
    assert posbindu["peserta_terdaftar"] == manifest["posbindu_participants"]["rows_after_deduplication"]
    # Five sessions in 2026. The sheet labelled "Jan 26" duplicates Juli and must
    # not add a sixth; the real 30 January session comes from the consolidated
    # sheet, which is the only place it was recorded.
    assert [row["tanggal"] for row in posbindu["sesi"]] == [
        "2026-01-30", "2026-02-27", "2026-05-29", "2026-07-03", "2026-08-28"
    ]
    # The published universe is teaching and support staff only.
    assert posbindu["kunjungan"] == sum(row["peserta"] for row in posbindu["sesi"])
    assert {row["kriteria"] for row in posbindu["kunjungan_per_kriteria"]} == {"Dosen", "Tendik"}
    # Everything filtered out is still counted, so the universe stays legible.
    assert posbindu["kunjungan"] + sum(posbindu["dikecualikan"].values()) == manifest["posbindu_visits"]["rows_after_deduplication"]

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

    # --- Posbindu 2022-2026 -------------------------------------------------
    yearly = load_json("hpu_posbindu_tahunan.json")
    assert yearly["tahun"] == [2022, 2023, 2024, 2025, 2026]
    # 2025 exists only in the registry; losing it would silently reopen the gap
    # the backfill was built to close.
    assert all(row["kunjungan"] > 0 for row in yearly["sumber_per_tahun"])
    assert {row["kunci"] for row in yearly["lapisan"]} == {"staf", "semua"}

    layers = {row["kunci"]: row for row in yearly["lapisan"]}
    # The staff layer is a subset of the whole cohort, and the 2026 slice of it
    # must still agree with the session-level file built from the same source.
    assert layers["staf"]["kunjungan"] < layers["semua"]["kunjungan"]
    staff_2026 = next(row for row in layers["staf"]["partisipasi"] if row["tahun"] == 2026)
    assert staff_2026["kunjungan"] == posbindu["kunjungan"]

    history_rows = manifest["posbindu_history"]["rows_after_deduplication"]
    dated = sum(row["kunjungan"] for row in yearly["sumber_per_tahun"])
    # Every visit is either placed in a year or counted as undateable; none is
    # quietly dropped between the loader and the page.
    assert dated + yearly["tanpa_tahun"] == history_rows + manifest["posbindu_visits"]["rows_after_deduplication"]

    for layer in yearly["lapisan"]:
        for measure in layer["indikator"]:
            for point in measure["seri"]:
                assert set(point["pita"]) <= allowed, f"Pita tak dikenal pada {measure['indikator']}"
                assert sum(point["pita"].values()) == point["kunjungan"]
                # A reading that exists but cannot be banded for want of a sex is
                # counted as measured, never as assessed. The reverse is a bug.
                assert point["dinilai"] <= point["terukur"] <= point["kunjungan"], (
                    f"{measure['indikator']} {point['tahun']}: dinilai/terukur/kunjungan tidak konsisten"
                )
                if not measure["berbasis_gender"]:
                    assert point["dinilai"] == point["terukur"], (
                        f"{measure['indikator']} tidak bergantung gender tetapi kehilangan penilaian"
                    )

    # Repeat attendance can only shrink as the number of visits rises.
    reach = [row["orang"] for row in yearly["retensi"]]
    assert reach == sorted(reach, reverse=True) and reach[0] > 0

    students = load_json("students_summary.json")
    student_years = {row["angkatan"]: row for row in students["per_tahun"]}
    assert students["total"] == sum(row["total"] for row in students["per_tahun"])

    # Every published count is either withheld or at least SMALL_CELL people.
    small_cells: list[tuple[str, str, int]] = []
    for path in sorted(DERIVED_DIR.glob("students_*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for location, key, value in walk_values(payload):
            if key == "n" and isinstance(value, int) and 0 < value < SMALL_CELL:
                small_cells.append((path.name, location, value))
    assert not small_cells, f"Sel di bawah {SMALL_CELL} orang lolos: {small_cells[:4]}"

    # The roster and PROFIL MABA count the same registrations from two systems.
    # They agree exactly on four cohorts; 2025 differs by four students and that
    # gap is published on /data rather than reconciled away here.
    registrations = Counter()
    for row in load_json("admissions_by_year.json"):
        registrations[row["tahun"]] += row["registrasi"]
    reconciliation = {}
    for year, expected in sorted(registrations.items()):
        row = student_years.get(year)
        if row is None:
            continue
        difference = row["sarjana"] - expected
        reconciliation[year] = difference
        assert abs(difference) <= 5, (
            f"Registrasi {year} berbeda {difference} antara daftar mahasiswa "
            f"({row['sarjana']}) dan PROFIL MABA ({expected})"
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
            "mahasiswa_tercatat": students["total"],
            "mahasiswa_sarjana": students["sarjana"],
        },
        "rekonsiliasi_registrasi": reconciliation,
    }
    (LOADED_DIR.parent / "validation_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
