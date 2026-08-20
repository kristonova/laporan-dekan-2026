#!/usr/bin/env python3
"""Fail loudly on incomplete multipart loads, implausible totals, schema drift, or privacy leaks."""

from __future__ import annotations

import json
from collections import Counter

import pandas as pd

from utils import CLEAN_DIR, DERIVED_DIR, LOADED_DIR


EXPECTED_FILES = {
    "citations_by_year.json", "publications_by_year_dept.json", "topics.json", "collab_countries.json",
    "lecturers_positions.json", "sinta_by_dept.json", "funding_by_year.json", "outreach_points.json",
    "sdg_matrix.json", "journals.json", "tck_2026_targets.json", "tck_2026_actuals.json",
    "tck_2026_anggaran.json", "tck_2026_joined.json", "value_model.json", "institution_snapshot.json",
}
PRIVATE_KEYS = {
    "name", "nama", "name_backup", "nidn", "nip", "nika", "nim", "leader", "member", "authors",
    "first_author", "last_author", "corresponding_author", "scopus_id", "sinta_id", "google_scholar_id",
    "combined_table", "people",
}


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

    tck = load_json("tck_2026_joined.json")
    assert len(tck) == 42
    statuses = Counter(row["status_tw3"] for row in tck)
    assert statuses == Counter({"tercapai": 24, "mendekati": 4, "tertinggal": 7, "meleset": 7})
    assert sum(row["status_thd_tahunan"] == "tercapai" for row in tck) == 15
    allowed_non_monotonic = {"32", "5b"}
    for row in tck:
        values = [float(row[f"capaian_tw{index}"]) for index in (1, 2, 3)]
        if any(after < before for before, after in zip(values, values[1:])):
            assert str(row["no"]) in allowed_non_monotonic, f"Capaian tidak kumulatif: {row['no']} {values}"
    indicator_27 = next(row for row in tck if str(row["no"]) == "27")
    assert indicator_27["arah"] == "turun" and indicator_27["status_tw3"] == "tercapai"

    for path in DERIVED_DIR.glob("*.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        leaks = [(location, key) for location, key in walk_keys(payload) if key in PRIVATE_KEYS]
        assert not leaks, f"Kunci privat di {path.name}: {leaks[:4]}"

    report = {
        "status": "lulus",
        "multipart": {name: manifest[name]["rows_loaded"] for name in ("citations", "publications", "people")},
        "derived_files": len(list(DERIVED_DIR.glob("*.json"))),
        "tck_indicators": len(tck),
        "tck_status": dict(statuses),
        "verified_anchors": {
            "citations_all_time": sum(citation_lookup.values()),
            "citations_2021_2025": sum(value for year, value in citation_lookup.items() if 2021 <= year <= 2025),
            "funding_2024_rp": funding_total[2024],
            "outreach_missing_location": int(outreach["location_status"].eq("missing").sum()),
        },
    }
    (LOADED_DIR.parent / "validation_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
