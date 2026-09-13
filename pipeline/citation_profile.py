"""Citation stock from the dedicated full-history SciVal publication export.

The citation column counts citations accumulated by each publication at the
snapshot date. It cannot reconstruct citations received in a calendar year.
The older 2020-2026 export still owns the report's other publication measures.
"""

from __future__ import annotations

import csv
from itertools import islice

import pandas as pd

from utils import SCIVAL_DIR


SOURCE_FILE = "Publications_in_Faculty_of_Mathematics_and_Natural_Sciences_UGM_1996_-_2027.csv"
UPDATED_LABEL = "6 September 2026"
EXPORTED_LABEL = "12 September 2026"
HEADER_ROW = 18
EXPECTED_PUBLICATIONS = 5_139
PERIOD_START, PERIOD_END = 2021, 2025
PUBLICATION_YEAR_START, PUBLICATION_YEAR_END = 1996, 2027
CURRENT_YEAR = 2026
MISSING_CITATION_POLICY = "reject_missing_or_invalid"
CITATION_DEFINITION = "Sitasi kumulatif yang diterima publikasi hingga 6 September 2026."
PERIOD_CITATION_DEFINITION = (
    "Sitasi kumulatif yang diterima karya terbit 2021–2025 hingga 6 September 2026; "
    "bukan jumlah sitasi yang diterima selama tahun kalender 2021–2025."
)
CITATION_BINS = [
    ("Belum disitasi", 0, 0),
    ("1–9 sitasi", 1, 9),
    ("10–49 sitasi", 10, 49),
    ("50–99 sitasi", 50, 99),
    ("≥100 sitasi", 100, None),
]


def clean_citation_publications(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate the three required fields, retaining every dated publication.

    A missing citation count is unknown, never an uncited publication. Stop on
    a blank, dash, invalid, negative, or fractional metric rather than assigning
    it to the zero-citation bin. Publication year 2027 is preserved as supplied.
    """
    result = frame[["eid", "year", "citations"]].copy()
    result["eid"] = result["eid"].astype("string").str.strip()
    if result["eid"].isna().any() or not result["eid"].str.fullmatch(r"2-s2\.0-\d+").all():
        raise AssertionError("Ekspor sitasi SciVal memuat EID kosong atau tidak valid")
    for column in ("year", "citations"):
        numeric = pd.to_numeric(result[column], errors="coerce")
        if numeric.isna().any() or not (numeric.ge(0) & numeric.mod(1).eq(0)).all():
            raise AssertionError(f"Ekspor sitasi SciVal: {column} harus berupa bilangan bulat nonnegatif; nilai kosong tidak diisi nol")
        result[column] = numeric.astype("int64")
    if not result["year"].between(PUBLICATION_YEAR_START, PUBLICATION_YEAR_END).all():
        raise AssertionError("Tahun publikasi di luar cakupan ekspor sitasi 1996–2027")

    # Identical repeats collapse by EID; conflicting observations have no
    # reliable priority in this one-file snapshot and must fail for review.
    unique_values = result.groupby("eid")[["year", "citations"]].nunique()
    if unique_values.gt(1).any().any():
        raise AssertionError("EID berulang dengan tahun atau sitasi yang berbeda")
    return result.sort_values("eid", kind="stable").drop_duplicates("eid", keep="first").reset_index(drop=True)


def load_citation_publications() -> tuple[pd.DataFrame, int]:
    """Read only publication identifiers, publication years, and citation counts."""
    path = SCIVAL_DIR / SOURCE_FILE
    with path.open(encoding="utf-8-sig", newline="") as handle:
        metadata = {row[0]: row[1] for row in islice(csv.reader(handle), HEADER_ROW) if len(row) == 2}
    assert metadata.get("Data source") == "Scopus", "Sumber ekspor sitasi berubah"
    assert metadata.get("Date last updated") == UPDATED_LABEL, "Tanggal pemutakhiran ekspor sitasi berubah"
    assert metadata.get("Date exported") == EXPORTED_LABEL, "Tanggal ekspor sitasi berubah"
    # SciVal ends with a copyright footer. usecols prevents loading author
    # names, author IDs, titles, or any unrelated person-level fields.
    frame = pd.read_csv(
        path, skiprows=HEADER_ROW, skipfooter=1, engine="python",
        usecols=["EID", "Year", "Citations"],
    ).rename(columns={"EID": "eid", "Year": "year", "Citations": "citations"})
    assert len(frame) == EXPECTED_PUBLICATIONS, "Jumlah baris ekspor sitasi berubah"
    cleaned = clean_citation_publications(frame)
    assert len(cleaned) == EXPECTED_PUBLICATIONS, "Jumlah EID unik ekspor sitasi berubah"
    return cleaned, len(frame) - len(cleaned)


def aggregate_citation_profile(frame: pd.DataFrame) -> tuple[dict, list[dict]]:
    """Partition the full collection by accumulated citations per publication."""
    source = clean_citation_publications(frame)
    total = len(source)
    bins = []
    for label, minimum, maximum in CITATION_BINS:
        mask = source["citations"].ge(minimum)
        if maximum is not None:
            mask &= source["citations"].le(maximum)
        group = source[mask]
        bins.append({
            "label": label,
            "publications": len(group),
            "share": round(len(group) / total * 100, 1),
            "citations": int(group["citations"].sum()),
        })
    cited = int(source["citations"].gt(0).sum())
    period = source[source["year"].between(PERIOD_START, PERIOD_END)]
    profile = {
        "source_file": SOURCE_FILE,
        "updated_label": UPDATED_LABEL,
        "exported_label": EXPORTED_LABEL,
        "publication_year_start": PUBLICATION_YEAR_START,
        "publication_year_end": PUBLICATION_YEAR_END,
        "publications": total,
        "citations": int(source["citations"].sum()),
        "cited_publications": cited,
        "cited_share": round(cited / total * 100, 1),
        "highly_cited_publications": int(source["citations"].ge(100).sum()),
        "highly_cited_threshold": 100,
        "period_start": PERIOD_START,
        "period_end": PERIOD_END,
        "period_publications": len(period),
        "period_citations": int(period["citations"].sum()),
        "current_year": CURRENT_YEAR,
        "current_publications": int(source["year"].eq(CURRENT_YEAR).sum()),
        "future_publications": int(source["year"].gt(CURRENT_YEAR).sum()),
        "future_year_policy": "Tahun publikasi mengikuti sumber; termasuk tahun 2027 dalam seluruh koleksi, di luar periode 2021–2025.",
        "missing_citation_policy": MISSING_CITATION_POLICY,
        "citation_definition": CITATION_DEFINITION,
        "period_citation_definition": PERIOD_CITATION_DEFINITION,
        "bins": bins,
    }
    assert sum(row["publications"] for row in bins) == total
    assert sum(row["citations"] for row in bins) == profile["citations"]
    return profile, bins
