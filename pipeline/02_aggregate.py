#!/usr/bin/env python3
"""Build browser-ready aggregates. The browser never receives person-level source rows."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import pandas as pd

from utils import CLEAN_DIR, PUBLIC_DATA_DIR, TCK_DIR, number, records, split_pipe, write_json


ISO3 = {
    "Japan": "JPN", "South Korea": "KOR", "Malaysia": "MYS", "Germany": "DEU", "Taiwan": "TWN",
    "Austria": "AUT", "India": "IND", "Australia": "AUS", "United States": "USA", "Singapore": "SGP",
    "United Kingdom": "GBR", "China": "CHN", "Thailand": "THA", "France": "FRA", "Netherlands": "NLD",
    "Italy": "ITA", "Pakistan": "PAK", "Qatar": "QAT", "Hong Kong": "HKG", "Indonesia": "IDN",
}


def output(filename: str, rows: list[dict] | dict) -> None:
    write_json(filename, rows)
    if isinstance(rows, list):
        csv_path = PUBLIC_DATA_DIR / filename.replace(".json", ".csv")
        frame = pd.DataFrame(rows)
        for column in frame.columns:
            if frame[column].map(lambda value: isinstance(value, (list, dict))).any():
                frame[column] = frame[column].map(lambda value: json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict)) else value)
        frame.to_csv(csv_path, index=False)


def tck_outputs() -> list[dict]:
    tck = pd.read_csv(CLEAN_DIR / "tck_2026_indikator.csv", dtype={"no": "string"})
    numeric_columns = [column for column in tck.columns if column.startswith("target_") or column.startswith("capaian_") or column.startswith("rasio_")]
    for column in numeric_columns:
        tck[column] = pd.to_numeric(tck[column], errors="coerce")
    joined = records(tck)
    target_columns = ["no", "pilar", "indikator", "satuan", "target_tw1", "target_tw2", "target_tw3", "target_tw4", "tag", "program_renstra", "arah"]
    actual_columns = ["no", "capaian_tw1", "capaian_tw2", "capaian_tw3", "rasio_tw3", "rasio_thd_target_tahunan", "status_tw3", "status_thd_tahunan", "sumber_data"]
    output("tck_2026_joined.json", joined)
    output("tck_2026_targets.json", records(tck[target_columns]))
    output("tck_2026_actuals.json", records(tck[actual_columns]))
    (PUBLIC_DATA_DIR / "tck_2026_indikator.csv").write_text(tck.to_csv(index=False), encoding="utf-8")
    budget = json.loads((TCK_DIR / "tck_2026_anggaran.json").read_text(encoding="utf-8"))
    write_json("tck_2026_anggaran.json", budget)
    return joined


def main() -> None:
    tck_outputs()

    citations = pd.read_csv(CLEAN_DIR / "citations.csv")
    citations["year"] = pd.to_numeric(citations["year"], errors="coerce").astype("Int64")
    citation_year = citations.groupby("year", dropna=True)["number_of_citation"].sum().reset_index(name="citations")
    citation_year["year"] = citation_year["year"].astype(int)
    citation_year["citations"] = citation_year["citations"].round().astype(int)
    citation_year["is_partial"] = citation_year["year"].eq(2025)
    citation_rows = records(citation_year.sort_values("year"))
    output("citations_by_year.json", citation_rows)

    publications = pd.read_csv(CLEAN_DIR / "publications.csv", low_memory=False)
    publications["year"] = pd.to_numeric(publications["year"], errors="coerce").astype("Int64")
    publication_group = publications.groupby(["year", "department"], dropna=False).agg(
        count=("Id", "size"),
        mapping=("mapping", lambda values: ",".join(sorted(set(values.dropna().astype(str))))),
    ).reset_index()
    publication_group["year"] = publication_group["year"].astype(int)
    publication_group["is_partial"] = publication_group["year"].eq(2025)
    publication_rows = records(publication_group.sort_values(["year", "department"]))
    output("publications_by_year_dept.json", publication_rows)

    topic_rows: list[dict] = []
    topic_source = publications.dropna(subset=["topic_cluster"])
    for cluster, group in topic_source.groupby("topic_cluster"):
        departments = Counter(group["department"].fillna("Belum terpetakan").astype(str))
        dominant = departments.most_common(1)[0][0] if departments else "Belum terpetakan"
        topic_names = group["topic_name"].dropna().astype(str)
        top_topic = topic_names.value_counts().index[0] if not topic_names.empty else str(cluster)
        samples = group["title"].dropna().astype(str).drop_duplicates().head(3).tolist()
        topic_rows.append({
            "cluster": str(cluster), "topic": top_topic, "dept": dominant, "n": int(len(group)), "sample": samples,
            "dept_counts": dict(departments),
        })
    topic_rows.sort(key=lambda row: (-row["n"], row["cluster"]))
    output("topics.json", topic_rows)

    country_year: Counter[tuple[str, int]] = Counter()
    for _, row in publications.dropna(subset=["country_region", "year"]).iterrows():
        year = int(row["year"])
        countries = set(split_pipe(row["country_region"]))
        for country in countries:
            if country != "Indonesia":
                country_year[(country, year)] += 1
    country_totals: Counter[str] = Counter()
    for (country, _), count in country_year.items():
        country_totals[country] += count
    country_rows = [
        {
            "country": country,
            "iso3": ISO3.get(country, ""),
            "n": int(total),
            "years": [{"year": year, "n": int(country_year[(country, year)])} for year in sorted({key_year for key_country, key_year in country_year if key_country == country})],
        }
        for country, total in country_totals.most_common()
    ]
    output("collab_countries.json", country_rows)

    lecturers = pd.read_csv(CLEAN_DIR / "lecturers.csv")
    lecturer_group = lecturers.groupby(["position", "department"], dropna=False).size().reset_index(name="n")
    output("lecturers_positions.json", records(lecturer_group.sort_values(["position", "department"])))

    sinta = pd.read_csv(CLEAN_DIR / "sinta.csv")
    sinta_group = sinta.dropna(subset=["score"]).groupby("department")["score"].agg(
        total="sum",
        median=lambda values: values.quantile(0.5, interpolation="higher"),
        n="size",
    ).reset_index()
    sinta_group[["total", "median"]] = sinta_group[["total", "median"]].round(2)
    output("sinta_by_dept.json", records(sinta_group.sort_values("total", ascending=False)))

    research = pd.read_csv(CLEAN_DIR / "research.csv")
    research["year"] = pd.to_numeric(research["year"], errors="coerce").astype("Int64")
    funding_total = research.dropna(subset=["year"]).groupby("year").agg(amount=("total_funding", "sum"), n=("total_funding", "size")).reset_index()
    funding_total["type"] = "Total"
    funding_type = research.dropna(subset=["year"]).groupby(["year", "funding_type"]).agg(amount=("total_funding", "sum"), n=("total_funding", "size")).reset_index().rename(columns={"funding_type": "type"})
    funding = pd.concat([funding_total, funding_type], ignore_index=True)
    funding["year"] = funding["year"].astype(int)
    funding["amount"] = funding["amount"].round(2)
    funding["is_partial"] = funding["year"].eq(2025)
    output("funding_by_year.json", records(funding.sort_values(["year", "type"])))

    student_pattern = r"melibatkan mahasiswa program s|melibatkan mahasiswa sarjana"
    student_research = research[research["tck"].fillna("").str.contains(student_pattern, case=False, regex=True)]
    student_by_year = student_research.dropna(subset=["year"]).groupby("year").size().reset_index(name="n")
    student_by_year["year"] = student_by_year["year"].astype(int)
    output("student_research_by_year.json", records(student_by_year.sort_values("year")))

    outreach = pd.read_csv(CLEAN_DIR / "community_service.csv", low_memory=False)
    outreach["year"] = pd.to_numeric(outreach["year"], errors="coerce").astype("Int64")
    point_group = outreach.groupby(["year", "regency", "province", "location_status"], dropna=False).size().reset_index(name="n")
    points = []
    for row in point_group.to_dict(orient="records"):
        year = row.get("year")
        points.append({
            "year": None if pd.isna(year) else int(year),
            "lat": None,
            "lng": None,
            "regency": "" if pd.isna(row.get("regency")) else str(row.get("regency")),
            "province": "" if pd.isna(row.get("province")) else str(row.get("province")),
            "n": int(row["n"]),
            "location_status": row.get("location_status"),
            "coordinate_source": None,
        })
    points.sort(key=lambda row: (row["year"] or 9999, row["province"], row["regency"]))
    output("outreach_points.json", points)
    outreach_year = outreach.dropna(subset=["year"]).groupby("year").size().reset_index(name="n")
    outreach_year["year"] = outreach_year["year"].astype(int)
    output("outreach_by_year.json", records(outreach_year.sort_values("year")))

    sdg_lookup = pd.read_csv(CLEAN_DIR / "sdg_lookup.csv")
    research_sdg: dict[int, int] = {}
    sdg_labels: dict[int, str] = {}
    for _, row in sdg_lookup.iterrows():
        match = re.search(r"SDG\s*(\d+)", str(row.get("sdg_name", "")), re.I)
        if match:
            index = int(match.group(1))
            research_sdg[index] = int(number(row.get("research")))
            sdg_labels[index] = str(row.get("sdg_name")).split(":", 1)[-1].strip()
    publication_sdg: Counter[int] = Counter()
    for value in publications["sdgs"].dropna():
        for match in set(re.findall(r"SDG\s*(\d+)", str(value), re.I)):
            publication_sdg[int(match)] += 1
    sdg_rows = [
        {"sdg": index, "label": sdg_labels.get(index, f"SDG {index}"), "research_n": research_sdg.get(index, 0), "publication_n": publication_sdg.get(index, 0)}
        for index in range(1, 18)
    ]
    output("sdg_matrix.json", sdg_rows)

    journals = pd.read_csv(CLEAN_DIR / "journals.csv")
    journal_group = journals.groupby(["journal", "year"], dropna=False).size().reset_index(name="n")
    journal_rows = []
    for row in journal_group.to_dict(orient="records"):
        journal_rows.append({"journal": row["journal"], "year": None if pd.isna(row["year"]) else int(row["year"]), "n": int(row["n"])})
    output("journals.json", journal_rows)

    media = pd.read_csv(CLEAN_DIR / "media.csv")
    media_group = media.dropna(subset=["year"]).groupby("year").size().reset_index(name="n")
    media_group["year"] = media_group["year"].astype(int)
    output("media_by_year.json", records(media_group.sort_values("year")))

    staff = pd.read_csv(CLEAN_DIR / "academic_staff.csv")
    programmes = pd.read_csv(CLEAN_DIR / "study_programmes.csv")
    departments = pd.read_csv(CLEAN_DIR / "departments.csv")
    laboratories = pd.read_csv(CLEAN_DIR / "laboratories.csv")
    institution = {
        "lecturers": int(len(lecturers)), "academic_staff": int(len(staff)), "departments": 4,
        "study_programmes": int(len(programmes)), "laboratories": int(len(laboratories)),
        "lecturer_doctoral": int(lecturers["doctoral"].astype(str).str.lower().eq("true").sum()),
        "lecturer_certified": int(lecturers["certified"].astype(str).str.lower().eq("true").sum()),
    }
    write_json("institution_snapshot.json", institution)

    years_2021_2025 = set(range(2021, 2026))
    funding_5y = float(research[research["year"].isin(years_2021_2025)]["total_funding"].sum())
    research_5y = int(research[research["year"].isin(years_2021_2025)].shape[0])
    outreach_5y = int(outreach[outreach["year"].isin(years_2021_2025)].shape[0])
    publications_5y = int(publications[publications["year"].isin(years_2021_2025)].shape[0])
    citations_5y = int(citations[citations["year"].isin(years_2021_2025)]["number_of_citation"].sum())
    outreach_period = outreach[outreach["year"].isin(years_2021_2025)]
    mappable_outreach = int(
        (
            outreach_period["location_status"].eq("recorded")
            & outreach_period["province"].fillna("").ne("")
            & outreach_period["location_scope"].ne("multi")
        ).sum()
    )
    raw_location_labels = int(outreach_period.loc[outreach_period["regency"].fillna("").ne(""), "regency"].nunique())
    value_model = {
        "period": "2021–2025",
        "metrics": {
            "funding_rp": funding_5y, "research_n": research_5y, "outreach_n": outreach_5y,
            "publications_n": publications_5y, "citations_n": citations_5y,
            "mappable_outreach_n": mappable_outreach,
            "raw_location_labels_n": raw_location_labels,
        },
        "nodes": [
            {"id": "funding", "label": "Dana riset", "value": funding_5y},
            {"id": "activities", "label": "Riset dan pengabdian", "value": research_5y + outreach_5y},
            {"id": "publications", "label": "Publikasi", "value": publications_5y},
            {"id": "impact", "label": "Sitasi dan jangkauan", "value": citations_5y + mappable_outreach},
        ],
        "links": [
            {"source": "funding", "target": "activities", "value": 1},
            {"source": "activities", "target": "publications", "value": 1},
            {"source": "publications", "target": "impact", "value": 1},
        ],
    }
    write_json("value_model.json", value_model)
    print(f"Generated {len(list((Path(__file__).resolve().parents[1] / 'src/data/derived').glob('*.json')))} derived JSON files.")


if __name__ == "__main__":
    main()
