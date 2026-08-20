#!/usr/bin/env python3
"""Load every source part once, deduplicate deterministically, and record provenance."""

from __future__ import annotations

import json

import pandas as pd

from utils import LOADED_DIR, MAPPINGS_DIR, TCK_DIR, deduplicate, ensure_directories, read_parts


DATASETS = {
    "citations": "citation_exported_*.csv",
    "publications": "publication_scival_exported_*.csv",
    "people": "people_exported_*.csv",
    "research": "research_exported_*.csv",
    "community_service": "community_service_exported_*.csv",
    "lecturers": "lecturer_exported_*.csv",
    "academic_staff": "academic_staff_exported_*.csv",
    "sinta": "sinta_score_exported_*.csv",
    "journals": "internal_journal_exported_*.csv",
    "sdg_lookup": "sdg_exported_*.csv",
    "study_programmes": "study_programme_exported_*.csv",
    "departments": "department_exported_*.csv",
    "laboratories": "laboratory_exported_*.csv",
    "media": "media_exposure_exported_*.csv",
}

EXPECTED_MULTIPART = {"citations": 25_300, "publications": 2_726, "people": 4_813}


def main() -> None:
    ensure_directories()
    manifest: dict[str, dict] = {}

    for name, pattern in DATASETS.items():
        frame, files = read_parts(pattern)
        loaded_rows = len(frame)
        clean = deduplicate(frame)
        clean.to_csv(LOADED_DIR / f"{name}.csv", index=False)
        manifest[name] = {
            "files": [path.name for path in files],
            "rows_loaded": loaded_rows,
            "rows_after_deduplication": len(clean),
            "duplicate_rows_removed": loaded_rows - len(clean),
        }
        if name in EXPECTED_MULTIPART and loaded_rows != EXPECTED_MULTIPART[name]:
            raise AssertionError(f"{name}: {loaded_rows} baris; seharusnya {EXPECTED_MULTIPART[name]}")

    tck = pd.read_csv(TCK_DIR / "tck_2026_indikator.csv", dtype={"no": "string"})
    if len(tck) != 42:
        raise AssertionError(f"TCK memuat {len(tck)} baris; seharusnya 42")
    tck.to_csv(LOADED_DIR / "tck_2026_indikator.csv", index=False)
    tck[["no", "pilar"]].to_csv(MAPPINGS_DIR / "tck_pillar.csv", index=False)
    manifest["tck_2026"] = {
        "files": ["tck_2026_indikator.csv", "tck_2026_targets.json", "tck_2026_actuals.json", "tck_2026_anggaran.json"],
        "rows_loaded": len(tck),
        "rows_after_deduplication": len(tck),
        "duplicate_rows_removed": 0,
    }

    (LOADED_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Loaded {len(DATASETS)} historical datasets and 42 TCK indicators.")


if __name__ == "__main__":
    main()
