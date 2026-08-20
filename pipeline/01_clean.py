#!/usr/bin/env python3
"""Normalize known quality issues and remove person-level fields before aggregation."""

from __future__ import annotations

import re
from collections import Counter

import pandas as pd

from utils import CLEAN_DIR, LOADED_DIR, MAPPINGS_DIR, ensure_directories, safe_year, split_pipe, year_from_date


def normalize_identifier(value: object) -> str:
    text = str(value or "").strip()
    return text[:-2] if text.endswith(".0") else text


def position_group(value: object) -> str:
    text = str(value or "").lower()
    if "guru besar" in text or "profesor" in text:
        return "Guru Besar"
    if "lektor kepala" in text:
        return "Lektor Kepala"
    if "asisten ahli" in text:
        return "Asisten Ahli"
    if re.search(r"\blektor\b", text):
        return "Lektor"
    if "tenaga pengajar" in text:
        return "Tenaga Pengajar"
    return "Belum terisi"


def sinta_score(value: object) -> float | None:
    """Restore Indonesian thousands separators lost during CSV type inference.

    SINTA scores are integers. The source uses a dot as a grouping separator
    (``1.745`` and ``1.55`` mean 1,745 and 155). The load stage turns plain
    integers into values ending in ``.0``; those stay integers, while every
    non-zero decimal separator is removed.
    """
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(parsed):
        return None
    if parsed.is_integer():
        return parsed
    return float(str(value).replace(".", ""))


def clean_publications(lecturers: pd.DataFrame) -> None:
    publication = pd.read_csv(LOADED_DIR / "publications.csv", low_memory=False)
    scopus_department: dict[str, str] = {}
    for _, row in lecturers.iterrows():
        department = str(row.get("department") or "").strip()
        if not department:
            continue
        for identifier in split_pipe(row.get("scopus_id")):
            scopus_department[normalize_identifier(identifier)] = department

    def assign_department(row: pd.Series) -> pd.Series:
        direct = str(row.get("department") or "").strip()
        if direct and direct.lower() != "nan":
            return pd.Series([direct, "source"])
        candidates = [scopus_department.get(normalize_identifier(identifier)) for identifier in split_pipe(row.get("scopus_authors_ids"))]
        counts = Counter(value for value in candidates if value)
        if counts:
            ranked = counts.most_common()
            if len(ranked) == 1 or ranked[0][1] > ranked[1][1]:
                return pd.Series([ranked[0][0], "scopus_id_majority"])
        return pd.Series(["Belum terpetakan", "unmapped"])

    publication[["department_clean", "mapping"]] = publication.apply(assign_department, axis=1)
    publication["year"] = safe_year(publication["year"], 1990, 2030)
    keep = [
        "Id", "title", "year", "publication_type", "country_region", "sdgs", "topic_cluster", "topic_name",
        "department_clean", "mapping",
    ]
    publication[keep].rename(columns={"department_clean": "department"}).to_csv(CLEAN_DIR / "publications.csv", index=False)


def main() -> None:
    ensure_directories()
    province_map = pd.read_csv(MAPPINGS_DIR / "provinsi_bps.csv", dtype=str).fillna("")
    province_lookup = province_map.set_index("raw")[["canonical", "bps_code", "scope"]].to_dict(orient="index")

    citations = pd.read_csv(LOADED_DIR / "citations.csv", low_memory=False)
    citations["year"] = safe_year(citations["year"], 1900, 2030)
    citations["number_of_citation"] = pd.to_numeric(citations["number_of_citation"], errors="coerce").fillna(0).clip(lower=0)
    citations[["Id", "year", "number_of_citation"]].dropna(subset=["year"]).to_csv(CLEAN_DIR / "citations.csv", index=False)

    lecturers = pd.read_csv(LOADED_DIR / "lecturers.csv", low_memory=False)
    clean_publications(lecturers)
    lecturer_clean = pd.DataFrame({
        "department": lecturers["department"].fillna("Belum terpetakan").replace("", "Belum terpetakan"),
        "position": lecturers["functional_position"].map(position_group),
        "doctoral": lecturers["degree"].fillna("").str.contains(r"(?:\bDr\.|Ph\.?D|D\.Eng|Doktor)", regex=True, case=False),
        "certified": pd.to_numeric(lecturers["certification"], errors="coerce").fillna(0).gt(0),
    })
    lecturer_clean.to_csv(CLEAN_DIR / "lecturers.csv", index=False)

    research = pd.read_csv(LOADED_DIR / "research.csv", low_memory=False)
    research_clean = pd.DataFrame({
        "year": safe_year(research["year"], 1990, 2030),
        "funding_type": research["funding_type"].fillna("Belum terklasifikasi").replace("", "Belum terklasifikasi"),
        "total_funding": pd.to_numeric(research["total_funding"], errors="coerce").fillna(0).clip(lower=0),
        "sdg_keyword": research["sdg_keyword"].fillna(""),
        "tck": research["tck"].fillna(""),
    })
    research_clean.to_csv(CLEAN_DIR / "research.csv", index=False)

    outreach = pd.read_csv(LOADED_DIR / "community_service.csv", low_memory=False)
    outreach_year = year_from_date(outreach["date_start"], 2000, 2030)
    raw_province = outreach["province"].fillna("").astype(str).str.strip()
    mapped = raw_province.map(lambda value: province_lookup.get(value, {}))
    outreach_clean = pd.DataFrame({
        "year": outreach_year,
        "regency": outreach["regency"].fillna("").astype(str).str.strip(),
        "province_raw": raw_province,
        "province": mapped.map(lambda value: value.get("canonical", "") if isinstance(value, dict) else ""),
        "bps_code": mapped.map(lambda value: value.get("bps_code", "") if isinstance(value, dict) else ""),
        "location_scope": mapped.map(lambda value: value.get("scope", "") if isinstance(value, dict) else ""),
        "country": outreach["country"].fillna("").astype(str).str.strip(),
        "data_source": outreach["data_source"].fillna("Tidak diketahui").astype(str).str.strip(),
    })
    outreach_clean["location_status"] = "recorded"
    outreach_clean.loc[(outreach_clean["regency"] == "") & (outreach_clean["province_raw"] == ""), "location_status"] = "missing"
    outreach_clean.loc[outreach_clean["location_scope"] == "online", "location_status"] = "online"
    outreach_clean.loc[outreach_clean["location_scope"] == "foreign", "location_status"] = "foreign"
    outreach_clean.to_csv(CLEAN_DIR / "community_service.csv", index=False)

    sinta = pd.read_csv(LOADED_DIR / "sinta.csv", low_memory=False)
    sinta_clean = pd.DataFrame({
        "department": sinta["department (from lecturer)"].fillna("Belum terpetakan").replace("", "Belum terpetakan"),
        "score": sinta["sinta_score_overall"].map(sinta_score),
        "snapshot": sinta["acquired_date"].fillna(""),
    })
    sinta_clean.to_csv(CLEAN_DIR / "sinta.csv", index=False)

    journals = pd.read_csv(LOADED_DIR / "journals.csv", low_memory=False)
    journal_clean = pd.DataFrame({
        "journal": journals["journal_name"].fillna("Belum terklasifikasi").replace("", "Belum terklasifikasi"),
        "year": year_from_date(journals["date"], 1900, 2030),
    })
    journal_clean.to_csv(CLEAN_DIR / "journals.csv", index=False)

    sdg_lookup = pd.read_csv(LOADED_DIR / "sdg_lookup.csv", low_memory=False)
    sdg_lookup.to_csv(CLEAN_DIR / "sdg_lookup.csv", index=False)

    staff = pd.read_csv(LOADED_DIR / "academic_staff.csv", low_memory=False)
    pd.DataFrame({"department": staff["department"].fillna("Belum terpetakan").replace("", "Belum terpetakan")}).to_csv(CLEAN_DIR / "academic_staff.csv", index=False)

    media = pd.read_csv(LOADED_DIR / "media.csv", low_memory=False)
    pd.DataFrame({
        "year": year_from_date(media["date"], 1900, 2030),
        "media": media["media_name"].fillna("Belum terklasifikasi").replace("", "Belum terklasifikasi"),
    }).to_csv(CLEAN_DIR / "media.csv", index=False)

    for name in ("study_programmes", "departments", "laboratories", "tck_2026_indikator"):
        pd.read_csv(LOADED_DIR / f"{name}.csv", low_memory=False).to_csv(CLEAN_DIR / f"{name}.csv", index=False)

    print("Cleaned sources written without person-level identifiers.")


if __name__ == "__main__":
    main()
