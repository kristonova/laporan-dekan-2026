#!/usr/bin/env python3
"""Load every source part once, deduplicate deterministically, and record provenance."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

from utils import (
    ACADEMIC_DIR,
    DEKAN_2026_DIR,
    HEALTH_DIR,
    LOADED_DIR,
    MAPPINGS_DIR,
    PARTNERSHIP_DIR,
    SCIVAL_DIR,
    SDM_DIR,
    TCK_2026_DIR,
    cell,
    deduplicate,
    digits_only,
    ensure_directories,
    excel_date,
    numeric_cell,
    read_parts,
    read_workbook,
    text_cell,
    workbook_sheets,
)


DATASETS = {
    "citations": "citation_exported_*.csv",
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

EXPECTED_MULTIPART = {"citations": 25_300, "people": 4_813}

SCIVAL_PUBLICATIONS = "Publications_in_Faculty_of_Mathematics_and_Natural_Sciences_UGM_2020_-_2026.csv"
SCIVAL_SUBJECT_AREAS = "Publications_by_Subject_Area.csv"
# Every SciVal report opens with a metadata block of a different height and
# closes with one Elsevier copyright line, so the header row is named per file
# rather than guessed. Row counts are asserted for the same reason the
# multipart exports are: a re-export under a different filter must fail loudly.
SCIVAL_HEADER_ROW = {SCIVAL_PUBLICATIONS: 17, SCIVAL_SUBJECT_AREAS: 13}
SCIVAL_EXPECTED_ROWS = {SCIVAL_PUBLICATIONS: 3_069, SCIVAL_SUBJECT_AREAS: 258}
# All_Topics_by_Scholarly_Output.csv is supplied too but not read: every
# prominence percentile it carries is already on each publication row, and
# nothing in the report needs its worldwide publication-share columns.

# The direct export renames every column and drops the curated department the
# P2M mirror carried. Columns are mapped back onto that mirror's snake_case
# schema so 01_clean.py and 02_aggregate.py keep reading the same names.
# Author names and the per-role author IDs are deliberately never read; only
# the combined Scopus ID list is, and 01_clean.py drops even that before
# anything reaches the published aggregates.
SCIVAL_PUBLICATION_COLUMNS = {
    "Title": "title",
    "EID": "eid",
    "Year": "year",
    "Full date": "date",
    "Number of Authors": "number_of_authors",
    "Scopus Author Ids": "scopus_authors_ids",
    "Scopus Source title": "scopus_source_title",
    "Publisher": "publisher",
    "Source type": "source_type",
    "Publication type": "publication_type",
    "Language": "language",
    "ISSN": "issn",
    "DOI": "doi",
    "Citations": "citations",
    "Field-Weighted Citation Impact": "fwci",
    "Views": "views",
    "SNIP (publication year)": "snip",
    "SJR (publication year)": "sjr",
    "CiteScore (publication year)": "citescore",
    "CiteScore percentile (publication year) *": "citescore_percentile",
    "Open Access": "open_access",
    "Institutions": "institutions",
    "Number of Institutions": "number_of_institutions",
    "Sector": "sector",
    "Country/Region": "country_region",
    "Number of Countries/Regions": "number_of_country_region",
    "All Science Journal Classification (ASJC) field name": "subject_area",
    "Sustainable Development Goals (2025)": "sdgs",
    "Topic Cluster name": "topic_cluster",
    "Topic Cluster number": "topic_cluster_number",
    "Topic Cluster Prominence Percentile": "topic_cluster_prominence",
    "Topic name": "topic_name",
    "Topic number": "topic_number",
    "Topic Prominence Percentile": "topic_prominence",
    "Publication link to Topic strength": "publication_link_to_topic_strength",
}


def read_scival(filename: str) -> pd.DataFrame:
    """Read one SciVal report without its metadata header or copyright footer.

    SciVal writes a bare ``-`` wherever a metric is unavailable. Those become NA
    here so no downstream caller has to special-case the string; left in, ``-``
    reads as a real country in the collaboration counts.
    """
    path = SCIVAL_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Berkas SciVal tidak ditemukan: {path}")
    frame = pd.read_csv(path, skiprows=SCIVAL_HEADER_ROW[filename], low_memory=False)
    first = frame.columns[0]
    frame = frame[~frame[first].astype(str).str.contains("Elsevier B.V.", na=False)]
    frame = frame.replace(r"^\s*-\s*$", pd.NA, regex=True)
    expected = SCIVAL_EXPECTED_ROWS[filename]
    if len(frame) != expected:
        raise AssertionError(f"{filename}: {len(frame)} baris; seharusnya {expected}")
    return frame.reset_index(drop=True)


def load_scival_publications() -> pd.DataFrame:
    frame = read_scival(SCIVAL_PUBLICATIONS)
    missing = [column for column in SCIVAL_PUBLICATION_COLUMNS if column not in frame.columns]
    if missing:
        raise AssertionError(f"Kolom SciVal hilang dari ekspor publikasi: {missing}")
    return frame[list(SCIVAL_PUBLICATION_COLUMNS)].rename(columns=SCIVAL_PUBLICATION_COLUMNS)


def load_department_lookup() -> tuple[pd.DataFrame, list[str]]:
    """Carry the faculty-curated department forward past the SciVal refresh.

    The direct SciVal export has no department column at all. The older
    publication_scival_exported_* mirror carried one on 1,682 of its rows,
    assigned by the faculty rather than inferred. Those pairs become the first
    mapping layer in 01_clean.py, ahead of the Scopus-ID majority fallback, so a
    fresher publication list does not cost the report its hand-checked
    attribution.
    """
    frame, files = read_parts("publication_scival_exported_*.csv")
    pairs = frame.dropna(subset=["eid", "department"])[["eid", "department"]]
    pairs = pairs.drop_duplicates(subset=["eid"], keep="last").reset_index(drop=True)
    return pairs, [path.name for path in files]


TCK_WORKBOOK = TCK_2026_DIR / "TCK 2026.xlsx"
# Positional columns of the TCK sheet. Its header spans two merged rows, so the
# sheet is read raw and sliced here rather than through pandas header inference.
TCK_COLUMNS = {
    "target_tahunan": 3, "dike": 4, "df": 5, "dm": 6, "dk": 7, "fakultas": 8,
    "target_tw1": 9, "capaian_tw1": 10, "target_tw2": 12, "capaian_tw2": 13,
    "target_tw3": 15, "capaian_tw3": 16, "target_tw4": 18, "capaian_tw4": 19,
}
TCK_FIRST_ROW = 3
TCK_ROW_COUNT = 42


def load_tck() -> pd.DataFrame:
    """Read the 42 official indicators from the SIMASTER workbook.

    The workbook carries only numbers; satuan, arah, program_renstra,
    penanggung_jawab, tag, and sumber_data live in the curated tck_meta.csv so a
    refreshed export never drops that context.
    """
    sheet = read_workbook(TCK_WORKBOOK, "TCK")
    body = sheet.iloc[TCK_FIRST_ROW : TCK_FIRST_ROW + TCK_ROW_COUNT]
    if len(body) != TCK_ROW_COUNT:
        raise AssertionError(f"Sheet TCK memuat {len(body)} baris indikator; seharusnya {TCK_ROW_COUNT}")

    pillars = pd.read_csv(MAPPINGS_DIR / "tck_pillar.csv", dtype={"no": "string"})
    meta = pd.read_csv(MAPPINGS_DIR / "tck_meta.csv", dtype={"no": "string"})
    if len(pillars) != TCK_ROW_COUNT or len(meta) != TCK_ROW_COUNT:
        raise AssertionError("tck_pillar.csv dan tck_meta.csv harus memuat 42 baris")

    rows: list[dict] = []
    for offset, (_, source) in enumerate(body.iterrows()):
        record: dict = {"no": pillars.iloc[offset]["no"], "label_sheet": text_cell(source, 2)}
        for name, index in TCK_COLUMNS.items():
            record[name] = numeric_cell(source, index)
        record["status_sistem"] = text_cell(source, 22)
        rows.append(record)

    frame = pd.DataFrame(rows)
    frame = frame.merge(meta, on="no", how="left").merge(pillars, on="no", how="left")
    if frame["indikator"].isna().any() or frame["pilar"].isna().any():
        missing = frame.loc[frame["indikator"].isna() | frame["pilar"].isna(), "no"].tolist()
        raise AssertionError(f"Metadata TCK hilang untuk indikator: {missing}")
    return frame


PARTNERSHIP_COLUMNS = {
    "judul": 1, "mitra": 2, "kabupaten": 4, "provinsi": 5, "jenis_mitra": 6,
    "unit_inisiator": 9, "prodi": 10, "negara": 12, "tipe_dokumen": 13, "bidang": 19,
}
PARTNERSHIP_DATES = {"tanggal_tanda_tangan": 14, "mulai": 15, "selesai": 16}
PARTNERSHIP_NOMINAL = 20


def load_partnerships() -> pd.DataFrame:
    """Flatten the LENTERA workbook into one row per cooperation document.

    Per-year sheets repeat an agreement across several rows when it covers more
    than one study programme or field; only the first carries a number in the No
    column, so continuation rows are folded back into the record above them.
    Contact columns (PIC name, email, phone) are never read.
    """
    candidates = sorted(PARTNERSHIP_DIR.glob("*DATA LENTERA*.xlsx"))
    if not candidates:
        raise FileNotFoundError(f"Tidak ada workbook LENTERA di {PARTNERSHIP_DIR}")
    workbook = candidates[-1]

    records: list[dict] = []
    for sheet in workbook_sheets(workbook):
        if not re.fullmatch(r"20\d{2}", sheet):
            continue
        grid = read_workbook(workbook, sheet)
        header = next((index for index, row in grid.iterrows() if text_cell(row, 0) == "No"), None)
        if header is None:
            raise AssertionError(f"Sheet {sheet}: baris header No tidak ditemukan")

        current: dict | None = None
        for _, row in grid.iloc[header + 1 :].iterrows():
            marker = text_cell(row, 0)
            if marker:
                current = {"tahun_sheet": int(sheet)}
                for name, index in PARTNERSHIP_COLUMNS.items():
                    current[name] = text_cell(row, index)
                for name, index in PARTNERSHIP_DATES.items():
                    parsed = excel_date(row.iloc[index] if index < len(row) else None)
                    current[name] = None if parsed is None else parsed.date().isoformat()
                current["nominal"] = numeric_cell(row, PARTNERSHIP_NOMINAL) or 0.0
                records.append(current)
            elif current is not None:
                # Continuation row: only prodi and bidang carry extra values.
                for name in ("prodi", "bidang"):
                    extra = text_cell(row, PARTNERSHIP_COLUMNS[name])
                    if extra and extra not in current[name]:
                        current[name] = f"{current[name]}, {extra}" if current[name] else extra

    return pd.DataFrame(records)


REVENUE_WORKBOOK = "Penerimaan dan DPI Kerjasama Fakultas MIPA 2021-2026.xlsx"
# Two layouts share these sheets: 2022 and 2023 label the activity "Nama
# Kegiatan" and carry no partner column, while 2024 onward add "Mitra" and
# rename it "Judul Kegiatan". Columns are therefore resolved by header label,
# never by position.
REVENUE_FIELDS = {
    "mitra": ("Mitra",),
    "kegiatan": ("Judul Kegiatan", "Nama Kegiatan"),
    "departemen": ("Departemen",),
    "tahun_kontrak": ("Tahun",),
    "billing": ("Billing",),
    "nominal_kontrak": ("Nominal Kontrak",),
    "dpi": ("DPI FMIPA",),
}
# The workbook writes Geofisika as a bracketed variant of Fisika and abbreviates
# Ilmu Komputer dan Elektronika; both are folded onto the canonical names so the
# revenue split lines up with every other department chart in the report.
REVENUE_DEPARTMENTS = {
    "Fisika": "Fisika",
    "Fisika (Geofisika)": "Fisika",
    "IKE": "Ilmu Komputer dan Elektronika",
    "Kimia": "Kimia",
    "Matematika": "Matematika",
}


def load_partnership_revenue() -> pd.DataFrame:
    """Contract value and the institutional development fee it returns to the faculty.

    This is billing-based cooperation revenue, a different measure from the
    research grant totals in research_exported_*.csv, and the two must never be
    summed. Four large rows carry no department at all — two 2024 rows sharing
    one billing number, plus one row each in 2025 and 2026 — and they are kept
    as "Tidak berdepartemen" rather than dropped or attributed by guesswork.
    Multi-year contracts ("2024-2025") are counted in the sheet they were filed
    under; the Tahun cell is preserved so that choice stays auditable.
    """
    path = DEKAN_2026_DIR / REVENUE_WORKBOOK
    rows: list[dict] = []
    for sheet in workbook_sheets(path):
        if not re.fullmatch(r"20\d{2}", sheet):
            continue
        grid = read_workbook(path, sheet)
        header_row = next((index for index, row in grid.iterrows() if text_cell(row, 0) == "No"), None)
        if header_row is None:
            raise AssertionError(f"{REVENUE_WORKBOOK} sheet {sheet}: baris header 'No' tidak ditemukan")
        header = grid.iloc[header_row]
        labels = {text_cell(header, index): index for index in range(grid.shape[1])}
        columns: dict[str, int | None] = {}
        for name, candidates in REVENUE_FIELDS.items():
            columns[name] = next((labels[label] for label in candidates if label in labels), None)
        for name in ("departemen", "nominal_kontrak", "dpi"):
            if columns[name] is None:
                raise AssertionError(f"{REVENUE_WORKBOOK} sheet {sheet}: kolom {name} hilang")

        for _, row in grid.iloc[header_row + 1 :].iterrows():
            # The sheet closes with a TOTAL line that has no number in column 0.
            if numeric_cell(row, 0) is None:
                continue
            raw_department = text_cell(row, columns["departemen"])
            if raw_department and raw_department not in REVENUE_DEPARTMENTS:
                raise AssertionError(f"{REVENUE_WORKBOOK} sheet {sheet}: departemen tak dikenal {raw_department!r}")
            rows.append({
                "tahun": int(sheet),
                "tahun_kontrak": text_cell(row, columns["tahun_kontrak"]) if columns["tahun_kontrak"] is not None else "",
                "mitra": text_cell(row, columns["mitra"]) if columns["mitra"] is not None else "",
                "kegiatan": text_cell(row, columns["kegiatan"]) if columns["kegiatan"] is not None else "",
                "departemen": REVENUE_DEPARTMENTS.get(raw_department, "Tidak berdepartemen"),
                "billing": text_cell(row, columns["billing"]) if columns["billing"] is not None else "",
                "nominal_kontrak": numeric_cell(row, columns["nominal_kontrak"]) or 0.0,
                "dpi": numeric_cell(row, columns["dpi"]) or 0.0,
            })
    return pd.DataFrame(rows)


SCHOOL_MOU_WORKBOOK = "Daftar Peserta MoU FMIPA UGM_No PKS FMIPA UGM.xlsx"


def load_school_mou() -> pd.DataFrame:
    """Schools that signed a memorandum with the faculty in July 2026.

    Only the school name leaves this function. The workbook also lists every
    attending teacher by name and position and names the faculty staff who
    hosted them; none of that is needed to count a partnership, so it is never
    read. The three sheets are the three signing days and overlap heavily — the
    same school appears on more than one — so the day is kept and the union is
    taken downstream rather than the rows being summed.
    """
    path = PARTNERSHIP_DIR / SCHOOL_MOU_WORKBOOK
    rows: list[dict] = []
    for sheet in workbook_sheets(path):
        grid = read_workbook(path, sheet)
        header_row = next(
            (index for index, row in grid.iterrows() if text_cell(row, 1) == "Nama Sekolah"), None
        )
        if header_row is None:
            raise AssertionError(f"{SCHOOL_MOU_WORKBOOK} sheet {sheet}: baris header 'Nama Sekolah' tidak ditemukan")
        for _, row in grid.iloc[header_row + 1 :].iterrows():
            school = re.sub(r"\s+", " ", text_cell(row, 1)).strip()
            if len(school) < 4:
                continue
            rows.append({"sesi": sheet, "sekolah": school})
    if not rows:
        raise AssertionError(f"{SCHOOL_MOU_WORKBOOK}: tidak ada baris sekolah yang terbaca")
    return pd.DataFrame(rows)


def load_admissions() -> pd.DataFrame:
    """Applicant / admitted / registered counts per undergraduate programme."""
    grid = read_workbook(ACADEMIC_DIR / "PROFIL MABA.xlsx", "sarjana")
    years = [
        (int(text_cell(grid.iloc[1], index)), index)
        for index in range(2, grid.shape[1], 3)
        if text_cell(grid.iloc[1], index).isdigit()
    ]
    rows: list[dict] = []
    department = ""
    for _, row in grid.iloc[3:].iterrows():
        first = text_cell(row, 0)
        if first.upper().startswith("JUMLAH"):
            break
        if first:
            department = first
        programme = text_cell(row, 1)
        if not programme:
            continue
        for year, index in years:
            rows.append({
                "departemen": department,
                "prodi": programme,
                "tahun": year,
                "peminat": numeric_cell(row, index),
                "diterima": numeric_cell(row, index + 1),
                "registrasi": numeric_cell(row, index + 2),
            })
    return pd.DataFrame(rows)


def load_active_students() -> pd.DataFrame:
    """Registered undergraduates by programme and entry cohort."""
    grid = read_workbook(ACADEMIC_DIR / "7. Profil Mahasiswa S1.xlsx", "registrasi mahasiswa")
    header = grid.iloc[4]
    years = [
        (int(text_cell(header, index)), index)
        for index in range(2, grid.shape[1])
        if text_cell(header, index).isdigit()
    ]
    rows: list[dict] = []
    department = ""
    for _, row in grid.iloc[5:].iterrows():
        first = text_cell(row, 0)
        if first.replace(" ", "").upper().startswith("JUMLAH"):
            break
        if first:
            department = first
        programme = re.sub(r"^\d+\.\s*", "", text_cell(row, 1))
        if not programme:
            continue
        for year, index in years:
            rows.append({
                "departemen": department,
                "prodi": programme,
                "angkatan": year,
                "mahasiswa": numeric_cell(row, index) or 0,
            })
    return pd.DataFrame(rows)



# One workbook per intake cohort. Every sheet repeats the same 34 columns with a
# title row, a blank row, and then the header, so the header is located by label
# rather than by position — a column reordered upstream must fail loudly here
# instead of silently shifting the data.
ROSTER_DIR = ACADEMIC_DIR / "daftar mahasiswa"
ROSTER_HEADER_ROW = 2
# Source column -> exported name. Everything absent from this map is dropped at
# load time and never reaches disk. That is deliberate: the workbooks carry
# names, student numbers, phone numbers, home addresses, and guardian details,
# while this report only ever publishes counts. Dropping the columns here means
# no later stage can leak what it never received.
ROSTER_COLUMNS = {
    "Angkatan": "angkatan",
    "Program Studi": "program_studi",
    "Jalur Masuk": "jalur_masuk",
    "Sub Angkatan": "sub_angkatan",
    "Kurikulum": "kurikulum",
    "Jenis Kelamin": "jenis_kelamin",
    "Agama": "agama",
    "Sekolah Asal": "sekolah_asal",
    "Kabupaten Sekolah": "kabupaten_sekolah",
    "Propinsi Sekolah": "propinsi_sekolah",
    "Kabupaten KTP": "kabupaten_ktp",
    "Propinsi KTP": "propinsi_ktp",
    "Pekerjaan Wali": "pekerjaan_wali",
    "Asal 3T": "asal_3t",
    "IPK": "ipk",
    "SKS Kumulatif": "sks_kumulatif",
    "Status Akhir": "status_akhir",
}
# Read but never exported: it only marks which rows are real students.
ROSTER_ROW_KEY = "NIM"


# A roster file is named either for its cohort ("Daftar mahasiswa 2026") or for
# the day it was exported ("Daftar mahasiswa 20260907"), and the second form is
# a re-export of the first, not another cohort. The 7 September 2026 file, for
# instance, holds the same 865 students as the 2026 file with the guardian
# occupation column filled in further. Loading both would count that intake
# twice, so only the newest export per cohort is read.
ROSTER_FILE_PATTERN = re.compile(r"^Daftar mahasiswa (?P<cohort>20\d{2})(?P<stamp>\d{4})?$")


def select_roster_files(paths: list[Path]) -> list[Path]:
    """Keep the most recent export of each intake cohort."""
    if not paths:
        raise FileNotFoundError(f"Tidak ada berkas daftar mahasiswa di {ROSTER_DIR}")
    newest: dict[int, tuple[str, Path]] = {}
    for path in paths:
        match = ROSTER_FILE_PATTERN.match(path.stem)
        if match is None:
            raise ValueError(f"Nama berkas daftar mahasiswa tidak dikenali: {path.name}")
        cohort = int(match.group("cohort"))
        # An undated file is the original; any dated one supersedes it.
        stamp = match.group("stamp") or "0000"
        if cohort not in newest or stamp > newest[cohort][0]:
            newest[cohort] = (stamp, path)
    return [path for _, (_, path) in sorted(newest.items())]



def load_student_roster() -> tuple[pd.DataFrame, list[str]]:
    """Per-cohort student rosters, stripped of every personal column at load.

    Returns the frame plus the file names that produced it, because this is the
    one loader that reads a whole directory instead of a single workbook.
    """
    paths = select_roster_files(sorted(ROSTER_DIR.glob("Daftar mahasiswa *.xlsx")))

    frames: list[pd.DataFrame] = []
    for path in paths:
        grid = read_workbook(path, "Daftar Mahasiswa")
        header = grid.iloc[ROSTER_HEADER_ROW]
        positions = {text_cell(header, index): index for index in range(grid.shape[1])}
        missing = [label for label in (*ROSTER_COLUMNS, ROSTER_ROW_KEY) if label not in positions]
        if missing:
            raise ValueError(f"{path.name}: kolom hilang {missing}")

        body = grid.iloc[ROSTER_HEADER_ROW + 1:]
        rows = [
            {name: cell(row, positions[label]) for label, name in ROSTER_COLUMNS.items()}
            for _, row in body.iterrows()
            if text_cell(row, positions[ROSTER_ROW_KEY])
        ]
        # Columns are pinned and typed as object: the 2021 and 2022 cohorts have
        # no school-of-origin data at all, and an all-NA column would otherwise
        # change dtype during the concat below.
        frame = pd.DataFrame(rows, columns=list(ROSTER_COLUMNS.values()), dtype=object)
        frame["berkas"] = path.stem
        frames.append(frame)

    roster = pd.concat(frames, ignore_index=True)
    leaked = sorted(set(roster.columns) - set(ROSTER_COLUMNS.values()) - {"berkas"})
    assert not leaked, f"Kolom tak terduga lolos dari daftar mahasiswa: {leaked}"
    return roster, [path.name for path in paths]

# sheet name, header row index, and the per-cohort summary columns that only
# appear on the first row of each academic-year block.
GRADUATE_SHEETS = {
    "Sarjana": ("SARJANA", 3, {"ipk_rerata": 7, "lama_studi": 8, "cumlaude": 9}),
    "Magister": ("MAGISTER", 0, {"ipk_rerata": 5, "lama_studi": 6, "toefl": 7}),
    "Doktor": ("DOKTOR", 1, {"ipk_rerata": 5, "lama_studi": 6, "toefl": 7}),
}


def load_graduates() -> pd.DataFrame:
    """Graduate counts and cohort quality metrics per level and academic year."""
    path = ACADEMIC_DIR / "PROFIL LULUSAN.xlsx"
    rows: list[dict] = []
    for level, (sheet, header_row, extras) in GRADUATE_SHEETS.items():
        grid = read_workbook(path, sheet)
        year = ""
        academic_year = ""
        totals: dict = {}
        for _, row in grid.iloc[header_row + 1 :].iterrows():
            if text_cell(row, 0):
                year = text_cell(row, 0)
                academic_year = text_cell(row, 1)
                totals = {name: numeric_cell(row, index) for name, index in extras.items()}
                totals["total_lulusan"] = numeric_cell(row, 4)
                totals["lama_studi"] = text_cell(row, extras["lama_studi"])
            programme = text_cell(row, 2)
            if not programme or not year:
                continue
            rows.append({
                "jenjang": level,
                "tahun": int(float(year)),
                "tahun_ajaran": academic_year,
                "prodi": programme,
                "lulusan": numeric_cell(row, 3) or 0,
                **totals,
            })

    frame = pd.DataFrame(rows)
    block = frame.groupby(["jenjang", "tahun"]).agg(lulusan=("lulusan", "sum"), total=("total_lulusan", "max"))
    empty = block[(block["lulusan"] == 0) & block["total"].isna()].index
    frame = frame[~frame.set_index(["jenjang", "tahun"]).index.isin(empty)].reset_index(drop=True)
    return pd.concat([frame, load_postgraduate_graduates()], ignore_index=True)


# The two postgraduate workbooks delivered in September 2026 for academic year
# 2025/2026 — the year PROFIL LULUSAN.xlsx left blank. Each holds four stacked
# blocks in a fixed order, every block a "Periode Wisuda" label row, a row of
# programme names, and the four graduation periods of the year.
POSTGRADUATE_FILES = {
    "Magister": ("Profil Lulusan Magister.xls", "Magister"),
    "Doktor": ("Profil Lulusan Doktor.xls", "Doktor"),
}
POSTGRADUATE_BLOCKS = ("ipk_rerata", "lama_studi", "toefl", "lulusan")
POSTGRADUATE_YEAR = 2026
POSTGRADUATE_ACADEMIC_YEAR = "2025/2026"


def read_postgraduate_blocks(filename: str, sheet: str) -> dict[str, dict[str, list[float | None]]]:
    """Pull the four metric blocks out of one postgraduate workbook.

    Blocks are located by their "Periode Wisuda" label rather than by a fixed
    offset: the two workbooks have different programme counts and therefore
    different block heights, and a future year may add a programme.
    """
    grid = read_workbook(DEKAN_2026_DIR / filename, sheet)
    starts = [index for index, row in grid.iterrows() if text_cell(row, 0) == "Periode Wisuda"]
    if len(starts) != len(POSTGRADUATE_BLOCKS):
        raise AssertionError(f"{filename}: {len(starts)} blok 'Periode Wisuda'; seharusnya {len(POSTGRADUATE_BLOCKS)}")

    blocks: dict[str, dict[str, list[float | None]]] = {}
    for name, start in zip(POSTGRADUATE_BLOCKS, starts):
        programmes = [
            (text_cell(grid.iloc[start + 1], index), index)
            for index in range(2, grid.shape[1])
            if text_cell(grid.iloc[start + 1], index)
        ]
        if not programmes:
            raise AssertionError(f"{filename}: blok {name} tidak memuat nama program studi")
        values: dict[str, list[float | None]] = {programme: [] for programme, _ in programmes}
        # Four graduation periods; the Rerata/Total row that follows them is
        # recomputed here instead, weighted by graduates rather than by period.
        for offset in range(2, 6):
            row = grid.iloc[start + offset]
            for programme, index in programmes:
                values[programme].append(numeric_cell(row, index))
        blocks[name] = values
    return blocks


def load_postgraduate_graduates() -> pd.DataFrame:
    """Magister and Doktor graduates for 2025/2026, per programme.

    Faculty-level IPK, study length, and TOEFL are weighted by the number of
    graduates in each period. The workbooks carry their own "Rerata" row, but it
    averages the four periods unweighted, so a period with two graduates counts
    as much as one with thirty-six.
    """
    rows: list[dict] = []
    for level, (filename, sheet) in POSTGRADUATE_FILES.items():
        blocks = read_postgraduate_blocks(filename, sheet)
        counts = blocks["lulusan"]
        total = sum(value for values in counts.values() for value in values if value)

        weighted: dict[str, float | None] = {}
        for metric in ("ipk_rerata", "lama_studi", "toefl"):
            numerator = 0.0
            denominator = 0.0
            for programme, values in blocks[metric].items():
                for value, count in zip(values, counts[programme]):
                    if value is None or not count:
                        continue
                    numerator += value * count
                    denominator += count
            weighted[metric] = None if denominator == 0 else numerator / denominator

        for programme, values in counts.items():
            graduates = sum(value for value in values if value)
            rows.append({
                "jenjang": level,
                "tahun": POSTGRADUATE_YEAR,
                "tahun_ajaran": POSTGRADUATE_ACADEMIC_YEAR,
                "prodi": programme,
                "lulusan": graduates,
                "ipk_rerata": None if weighted["ipk_rerata"] is None else round(weighted["ipk_rerata"], 2),
                # Kept as text because PROFIL LULUSAN.xlsx writes this column as
                # text for every other year ("4 th 7 bln" for Sarjana).
                "lama_studi": "" if weighted["lama_studi"] is None else f"{weighted['lama_studi']:.2f}",
                "toefl": None if weighted["toefl"] is None else round(weighted["toefl"], 1),
                "total_lulusan": float(total),
            })
    return pd.DataFrame(rows)


def load_achievements() -> pd.DataFrame:
    """Student competition results by department, level, and year."""
    grid = read_workbook(ACADEMIC_DIR / "PRESTASI MAHASISWA.xlsx", "Sheet1")
    header = grid.iloc[4]
    years = [
        (int(text_cell(header, index)), index)
        for index in range(2, grid.shape[1])
        if text_cell(header, index).isdigit()
    ]
    rows: list[dict] = []
    department = ""
    for _, row in grid.iloc[5:].iterrows():
        if text_cell(row, 0):
            department = text_cell(row, 0)
        tier = text_cell(row, 1)
        if not tier or not department:
            continue
        for year, index in years:
            rows.append({
                "departemen": department,
                "tingkat": tier,
                "tahun": year,
                "prestasi": numeric_cell(row, index) or 0,
            })
    return pd.DataFrame(rows)


def load_scholarships() -> pd.DataFrame:
    """Scholarship recipients per scheme and undergraduate programme."""
    # Only the Rekapitulasi sheet is read. The workbook's second sheet holds a
    # per-student row with name, NIU, and NIM, which has no business leaving the
    # source directory.
    grid = read_workbook(DEKAN_2026_DIR / "PENERIMA BEASISWA.xlsx", "Rekapitulasi")
    programmes = [(text_cell(grid.iloc[4], index), index) for index in range(2, 10)]
    rows: list[dict] = []
    for _, row in grid.iloc[5:].iterrows():
        scheme = text_cell(row, 1)
        if not scheme or text_cell(row, 0).upper().startswith("JUMLAH"):
            continue
        for programme, index in programmes:
            rows.append({"beasiswa": scheme, "prodi": programme, "penerima": numeric_cell(row, index) or 0})
    return pd.DataFrame(rows)


PERIOD_PATTERN = re.compile(r"^\d{4}\s*-\s*\d{4}$")


def load_accreditation() -> pd.DataFrame:
    """National and international accreditation status per study programme.

    The September 2026 workbook replaced the older one and changed both sheets:
    the national sheet lost its trailing Rekap block, and the international
    sheet became one flat list instead of SARJANA/PASCASARJANA sections split
    by their own recap tables. A real entry is still identified the same way —
    a numbered row carrying a YYYY-YYYY validity period — so the Rekap rows the
    old layout appended cannot slip in if the faculty restores them.
    """
    path = DEKAN_2026_DIR / "AKREDITASI PRODI MIPA.xlsx"
    rows: list[dict] = []

    national = read_workbook(path, "AKREDITASI NASIONAL")
    for _, row in national.iterrows():
        if not text_cell(row, 0).isdigit() or not PERIOD_PATTERN.match(text_cell(row, 4)):
            continue
        rows.append({
            "lingkup": "Nasional",
            "jenjang_grup": "",
            "departemen": text_cell(row, 1),
            "prodi": text_cell(row, 2),
            "lembaga": text_cell(row, 3),
            "periode": text_cell(row, 4),
            "nilai": text_cell(row, 5),
        })

    international = read_workbook(path, "AKREDITASI INTERNASIONAL")
    for _, row in international.iterrows():
        first = text_cell(row, 0)
        if first.lower() == "rekap":
            break
        if not first.isdigit() or not PERIOD_PATTERN.match(text_cell(row, 3)):
            continue
        prodi = text_cell(row, 1)
        rows.append({
            "lingkup": "Internasional",
            "jenjang_grup": "Sarjana" if prodi.upper().startswith("S1") else "Pascasarjana",
            "departemen": "",
            "prodi": prodi,
            "lembaga": text_cell(row, 2),
            "periode": text_cell(row, 3),
            "nilai": "",
        })

    frame = pd.DataFrame(rows)
    national_rows = frame[frame["lingkup"] == "Nasional"]
    if len(national_rows) != 18:
        raise AssertionError(f"Akreditasi nasional memuat {len(national_rows)} prodi; seharusnya 18")
    if int((frame["lingkup"] == "Internasional").sum()) != 15:
        raise AssertionError("Akreditasi internasional seharusnya memuat 15 prodi")
    return frame


DEPARTMENTS = {"Fisika", "Kimia", "Matematika", "Ilmu Komputer dan Elektronika"}

# The SIMASTER personnel workbooks. All three share one layout: a blank first
# row, the header on row 1, and data from row 2 — so the header row is located
# by its "No." label instead of assumed, and a re-export that gains a title row
# fails loudly here rather than silently shifting every column.
SDM_LECTURERS_FILE = "Data Dosen - 3 Sept 2026.xlsx"
SDM_STAFF_FILE = "Data Tendik - 3 Sept 2026.xlsx"
SDM_PROFESSORS_FILE = "Data Guru Besar - 3 Sept 2026.xlsx"
SDM_CERTIFICATION_FILE = "Rekap Dosen bersertifikasi.xlsx"

# Names, NIP/NIKA, NIDN, and NUPTK stay out of the loaded frames entirely.
# Nothing downstream joins these workbooks on a person — each one already
# carries the department beside the attribute — so unlike the old two-source
# merge there is no reason for an identifier to exist even in work/loaded/.
SDM_LECTURER_COLUMNS = {
    "golongan": 6, "jabatan_fungsional": 9, "tmt_jabatan": 10,
    "jabatan_struktural": 11, "pendidikan": 13, "kategori": 14, "departemen": 15,
}
SDM_STAFF_COLUMNS = {
    "golongan": 6, "jabatan_fungsional": 9, "jabatan_struktural": 11,
    "pendidikan": 13, "kategori": 14, "departemen": 15,
}


def sdm_header_row(grid: pd.DataFrame, label: str) -> int:
    row = next((index for index, values in grid.iterrows() if text_cell(values, 0) == "No."), None)
    if row is None:
        raise AssertionError(f"{label}: baris header 'No.' tidak ditemukan")
    return int(row)


def read_sdm_roster(filename: str, sheet: str, columns: dict[str, int], expected_category: str) -> pd.DataFrame:
    """Read one SIMASTER roster, keeping only non-identifying attributes.

    Every workbook ends where the numbered rows end; a row without a number in
    column 0 is a footnote or a rekap line, never a person.
    """
    grid = read_workbook(SDM_DIR / filename, sheet)
    header = sdm_header_row(grid, filename)
    rows: list[dict] = []
    for _, row in grid.iloc[header + 1 :].iterrows():
        if numeric_cell(row, 0) is None:
            continue
        record = {name: text_cell(row, index) for name, index in columns.items()}
        if record["departemen"] not in DEPARTMENTS and record["departemen"] != "Kantor Administrasi Fakultas":
            raise AssertionError(f"{filename}: departemen tak dikenal {record['departemen']!r}")
        if record["kategori"] != expected_category:
            raise AssertionError(f"{filename}: kategori pegawai {record['kategori']!r}, seharusnya {expected_category!r}")
        if "tmt_jabatan" in record:
            parsed = excel_date(cell(row, columns["tmt_jabatan"]))
            record["tmt_jabatan"] = None if parsed is None else parsed.date().isoformat()
        rows.append(record)
    return pd.DataFrame(rows)


def load_sdm_lecturers() -> pd.DataFrame:
    """The 207-strong lecturer roster: jabatan fungsional, golongan, and degree."""
    frame = read_sdm_roster(SDM_LECTURERS_FILE, "data Dosen", SDM_LECTURER_COLUMNS, "Dosen")
    if not set(frame["departemen"]) <= DEPARTMENTS:
        raise AssertionError("Roster dosen memuat unit non-departemen")
    return frame


def load_sdm_staff() -> pd.DataFrame:
    """Tenaga kependidikan, including the faculty administration office."""
    return read_sdm_roster(SDM_STAFF_FILE, "Data tendik", SDM_STAFF_COLUMNS, "Tenaga Kependidikan")


def load_sdm_professors() -> pd.DataFrame:
    """Guru Besar with the TMT that dates each appointment.

    The workbook's last column is annotated "Periode Dekanat 2021-2026" by the
    faculty itself, so splitting the roster on that period is the source's own
    framing rather than one imposed here.
    """
    grid = read_workbook(SDM_DIR / SDM_PROFESSORS_FILE, "data Dosen")
    header = sdm_header_row(grid, SDM_PROFESSORS_FILE)
    rows: list[dict] = []
    for _, row in grid.iloc[header + 1 :].iterrows():
        if numeric_cell(row, 0) is None:
            continue
        tmt = excel_date(cell(row, 4))
        department = text_cell(row, 5)
        if department not in DEPARTMENTS:
            raise AssertionError(f"{SDM_PROFESSORS_FILE}: departemen tak dikenal {department!r}")
        rows.append({
            "jabatan_fungsional": text_cell(row, 3),
            "tmt_jabatan": None if tmt is None else tmt.date().isoformat(),
            "tahun_tmt": None if tmt is None else int(tmt.year),
            "departemen": department,
        })
    return pd.DataFrame(rows)


# Departments are abbreviated differently in the certification recap than in
# every other SIMASTER sheet; the mapping is spelled out rather than guessed.
SDM_CERTIFICATION_DEPARTMENTS = {
    "ILKOM": "Ilmu Komputer dan Elektronika",
    "Fisika": "Fisika",
    "Kimia": "Kimia",
    "Matematika": "Matematika",
}


def load_sdm_certification() -> pd.DataFrame:
    """Serdos status per lecturer, reduced to department plus a boolean.

    Uncertified rows carry the sentence "Belum tersertifikasi dosen" in the
    certificate-number column instead of a number, so that is what separates
    the two states. NUPTK and the certificate number are dropped on read.
    """
    grid = read_workbook(SDM_DIR / SDM_CERTIFICATION_FILE, "MIPA")
    header = next((index for index, row in grid.iterrows() if text_cell(row, 0) == "NO."), None)
    if header is None:
        raise AssertionError(f"{SDM_CERTIFICATION_FILE}: baris header 'NO.' tidak ditemukan")
    rows: list[dict] = []
    for _, row in grid.iloc[header + 1 :].iterrows():
        if numeric_cell(row, 0) is None:
            continue
        raw = text_cell(row, 4)
        department = SDM_CERTIFICATION_DEPARTMENTS.get(raw)
        if department is None:
            raise AssertionError(f"{SDM_CERTIFICATION_FILE}: departemen tak dikenal {raw!r}")
        rows.append({
            "departemen": department,
            "tersertifikasi": not text_cell(row, 3).lower().startswith("belum"),
        })
    return pd.DataFrame(rows)


def load_exchange() -> pd.DataFrame:
    """Outbound student mobility; personal identifiers are dropped on read."""
    grid = read_workbook(ACADEMIC_DIR / "mahasiswa Exchange.xlsx", "Sheet1")
    rows: list[dict] = []
    for _, row in grid.iloc[1:].iterrows():
        destination = text_cell(row, 5)
        if not destination:
            continue
        start = excel_date(row.iloc[7] if 7 < len(row) else None)
        letter = excel_date(row.iloc[9] if 9 < len(row) else None)
        reference = start or letter
        rows.append({
            "departemen": text_cell(row, 2),
            "prodi": text_cell(row, 3),
            "acara": text_cell(row, 4),
            "universitas": destination,
            "negara": text_cell(row, 6),
            "tahun": None if reference is None else reference.year,
        })
    return pd.DataFrame(rows)


def load_tracer() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Tracer-study waiting time and employment sector, without respondent names.

    Both exports end with two summary rows the faculty computed itself; those are
    captured as cross-check figures rather than mixed into the respondent rows.
    """
    waiting_path = ACADEMIC_DIR / "25,26.Waktu tunggu.xls"
    grid = read_workbook(waiting_path, workbook_sheets(waiting_path)[0])
    waiting: list[dict] = []
    summary: dict = {}
    for _, row in grid.iloc[5:].iterrows():
        label = text_cell(row, 0).lower()
        if label.startswith("rata - rata") or label.startswith("rata-rata"):
            summary["rata_rata_bulan"] = numeric_cell(row, 4)
            continue
        if label.startswith("prosentase") or label.startswith("persentase"):
            summary["persen_bekerja"] = numeric_cell(row, 4)
            continue
        year = text_cell(row, 4)
        months = numeric_cell(row, 3)
        if not year.isdigit() or months is None:
            continue
        waiting.append({"prodi": text_cell(row, 2), "tahun": int(year), "bulan": months})

    sector_path = ACADEMIC_DIR / "27,29.bidang kerja.xls"
    grid = read_workbook(sector_path, workbook_sheets(sector_path)[0])
    sectors: list[dict] = []
    for _, row in grid.iloc[4:].iterrows():
        year = text_cell(row, 5)
        field = text_cell(row, 3)
        if not year.isdigit() or not field:
            continue
        sectors.append({"prodi": text_cell(row, 2), "tahun": int(year), "bidang_raw": field})

    return pd.DataFrame(waiting), pd.DataFrame(sectors), summary


POSBINDU_COLUMNS = {
    "tanggal": 1, "nama": 2, "gender": 4, "imt": 8, "lingkar_perut": 10,
    "tekanan_darah": 13, "asam_urat": 15, "kolesterol": 17, "gula_darah": 19, "rujukan": 20,
}

# The consolidated sheet carries the same fields plus a Kriteria column between
# the birth date and the gender, which shifts everything after it one to the right.
POSBINDU_SUMMARY_SHEET = "Jan , Agus 26"
POSBINDU_SUMMARY_COLUMNS = {
    "tanggal": 2, "nama": 3, "kriteria": 5, "gender": 6, "imt": 10, "lingkar_perut": 12,
    "tekanan_darah": 15, "asam_urat": 17, "kolesterol": 19, "gula_darah": 21, "rujukan": 22,
}

# Academic titles carried by the name, stripped before it is used as a join key.
POSBINDU_TITLE = re.compile(
    r"^(prof|dr|drs|dra|ir|apt|ph\.?d|a\.?md|amd|b\.?sc|m\.?sc|m\.?eng|"
    r"s\.?si|m\.?si|m\.?s|s\.?t|m\.?t|s\.?e|s\.?h|s\.?ip|s\.?sos|s\.?pd|m\.?pd|"
    r"s\.?kom|m\.?kom|s\.?farm|msi|ssi)$"
)


def _posbindu_key(name: str) -> str:
    """Normalise a participant name so the two sheets can be matched.

    Titles, punctuation and casing differ between the per-month sheets and the
    consolidated one. The result is a join key only: it is used inside this
    module and never written to a file (PRD section 11.3).
    """
    text = re.sub(r"[.,]", " ", str(name or "").lower())
    return " ".join(part for part in text.split() if part and not POSBINDU_TITLE.match(part))


def _looks_numeric(value: str) -> bool:
    return bool(re.fullmatch(r"-?\d+(\.\d+)?", str(value or "").strip()))


def load_posbindu() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Posbindu screening results, reduced to anonymous per-visit categories.

    Two layers of the same workbook are read. Measurements come from the
    per-month sheets, whose column layout is intact. Participant category comes
    from the consolidated sheet, which is the only place it is recorded, joined
    on (date, name). The name serves as that key and never leaves this function.

    Two traps in the source are handled explicitly:

    * The sheet labelled "Jan 26" is a verbatim copy of Juli 26 (both dated
      3 July 2026), so visits are keyed and deduplicated. The genuine 30 January
      session survives only in the consolidated sheet and is read from there.
    * On the consolidated sheet the 3 July session is missing its "Interpretasi
      Asam Urat" column, which shifts every later column one to the left. Such a
      session must not be read for measurements, so it is detected and refused
      rather than silently mis-parsed.
    """
    recap = HEALTH_DIR / "hasil-posbindu-melati-mipa rekap 2026.xlsx"

    def read_rows(sheet: str, columns: dict[str, int], first_row: int) -> list[dict]:
        grid = read_workbook(recap, sheet)
        rows: list[dict] = []
        for _, row in grid.iloc[first_row:].iterrows():
            index = columns["tanggal"]
            date = excel_date(row.iloc[index] if index < len(row) else None)
            name = text_cell(row, columns["nama"])
            if date is None or not name:
                continue
            rows.append({
                "tanggal": date.date().isoformat(),
                "_key": _posbindu_key(name),
                **{
                    field: text_cell(row, column)
                    for field, column in columns.items()
                    if field not in {"tanggal", "nama"}
                },
            })
        return rows

    # --- consolidated sheet: participant category, and the January session ----
    summary_grid = read_workbook(recap, POSBINDU_SUMMARY_SHEET)
    summary_header = next(
        (index for index, row in summary_grid.iterrows() if text_cell(row, 0) == "No kendali"),
        None,
    )
    if summary_header is None:
        raise SystemExit(f"Sheet {POSBINDU_SUMMARY_SHEET!r} tidak lagi memiliki header 'No kendali'.")
    summary_rows = read_rows(POSBINDU_SUMMARY_SHEET, POSBINDU_SUMMARY_COLUMNS, summary_header + 1)

    category = {
        (row["tanggal"], row["_key"]): row["kriteria"]
        for row in summary_rows
        if row["kriteria"]
    }

    # An interpretation column holding numbers means the session lost a column
    # and everything after it slid left. Record which sessions to refuse.
    drifted: set[str] = set()
    for date in sorted({row["tanggal"] for row in summary_rows}):
        cells = [row["asam_urat"] for row in summary_rows if row["tanggal"] == date and row["asam_urat"]]
        if len(cells) > 2 and sum(map(_looks_numeric, cells)) > len(cells) / 2:
            drifted.add(date)

    # --- per-month sheets: the measurements -----------------------------------
    seen: set[tuple[str, str]] = set()
    visits: list[dict] = []
    for sheet in workbook_sheets(recap):
        if sheet == POSBINDU_SUMMARY_SHEET:
            continue
        grid = read_workbook(recap, sheet)
        header = next((index for index, row in grid.iterrows() if text_cell(row, 0) == "Posbindu"), None)
        if header is None:
            continue
        for row in read_rows(sheet, POSBINDU_COLUMNS, header + 1):
            key = (row["tanggal"], row["_key"])
            if key in seen:
                continue
            seen.add(key)
            visits.append(row)

    # Sessions the per-month sheets never carried, taken from the consolidated one.
    # Snapshot the covered dates first: appending below must not shrink the set
    # and strand the rest of a session after its first row.
    monthly_dates = {visit["tanggal"] for visit in visits}
    for row in summary_rows:
        key = (row["tanggal"], row["_key"])
        if key in seen or row["tanggal"] in monthly_dates:
            continue
        if row["tanggal"] in drifted:
            raise SystemExit(
                f"Sesi Posbindu {row['tanggal']} hanya ada di sheet konsolidasi dan kolomnya "
                "bergeser; perbaiki sumber sebelum sesi ini dapat dipakai."
            )
        seen.add(key)
        visits.append(row)

    for visit in visits:
        visit["kriteria"] = category.get((visit["tanggal"], visit.pop("_key")), "")

    registry = read_workbook(HEALTH_DIR / "Data Posbindu.xlsx", "Sheet1")
    participants: list[dict] = []
    for _, row in registry.iloc[1:].iterrows():
        if not text_cell(row, 1):
            continue
        participants.append({
            "kriteria": text_cell(row, 5) or "Tidak diketahui",
            "gender": text_cell(row, 4),
        })

    return pd.DataFrame(visits), pd.DataFrame(participants)


# --- Posbindu 2022-2025: the years the 2026 workbook does not reach ---------

# The digitisation workbook is authoritative wherever it has a session: it
# carries an exact date and a transcription audit. The registry is the only
# record of the months it never covered, and the only record of 2025 at all.
POSBINDU_HISTORY_FILE = "Rekap_Digitasi_Posbindu_Melati_FMIPA_UGM_2022_2024.xlsx"
POSBINDU_HISTORY_SHEET = "Data Konsolidasi"
POSBINDU_REGISTRY_FILE = "Data Posbindu.xlsx"

# Registry dates survived Excel only as month precision (the day is always 01),
# and 208 of them not even that. Anything before the programme began is noise.
POSBINDU_FIRST_YEAR = 2022
# 2026 belongs to the recap workbook, which still has real session dates.
POSBINDU_LAST_HISTORY_YEAR = 2025

POSBINDU_MEASURE_COLUMNS = {
    "bb": "BB (kg)", "tb": "TB (cm)", "lp": "LP (cm)",
    "sistolik": "Sistolik (mmHg)", "diastolik": "Diastolik (mmHg)",
    "gula_darah": "GDS (mg/dL)", "asam_urat": "Asam Urat (mg/dL)",
    "kolesterol": "Kolesterol (mg/dL)",
}

POSBINDU_SEX = {"Laki-laki": "Pria", "Perempuan": "Wanita"}


def _posbindu_number(value: object) -> float | str:
    """A measurement cell as a number, or "" when blank or unreadable.

    Analog transcription leaves dashes, stray text and Indonesian decimal
    commas behind; none of those may become a silent zero.
    """
    text = str(value if value is not None else "").strip().replace(",", ".")
    if not text or text in {"-", "nan", "NaT"}:
        return ""
    try:
        number = float(text)
    except ValueError:
        return ""
    return "" if pd.isna(number) else number


def load_posbindu_history() -> tuple[pd.DataFrame, dict]:
    """Posbindu screening 2022-2025, reduced to anonymous per-visit measurements.

    Two sources with different strengths are stitched on the month, the finest
    precision they share:

    * The digitisation workbook holds 12 sessions between October 2022 and July
      2024, with exact dates and a per-row transcription-quality flag.
    * The registry holds one row per person and up to five examinations each.
      Its dates survived only as month precision, so it is admitted for the
      months the digitisation never covered -- every 2025 session, and the
      September-December sessions of 2023 and 2024 that were never digitised.

    Admitting the registry by month rather than by row means the two sources can
    never describe the same session, so nothing is counted twice and no fuzzy
    name match has to be trusted. Names are used only to carry sex across from
    the registry and are dropped before the frame is built (PRD section 11.3).
    """
    digitised = read_workbook(HEALTH_DIR / POSBINDU_HISTORY_FILE, POSBINDU_HISTORY_SHEET, header=0)
    registry = read_workbook(HEALTH_DIR / POSBINDU_REGISTRY_FILE, "Sheet1", header=0)

    # Both sheets carry one plain header row, unlike the merged headers
    # elsewhere in this module, so pandas may name the columns here.
    imt_column = next((name for name in digitised.columns if str(name).startswith("IMT Hitung")), None)
    if imt_column is None:
        raise SystemExit(f"Kolom 'IMT Hitung' hilang dari {POSBINDU_HISTORY_FILE}.")

    # Sex is recorded only in the registry; the digitisation sheet never had it.
    sex_by_name: dict[str, str] = {}
    for _, row in registry.iterrows():
        key = _posbindu_key(row.get("Nama Lengkap"))
        sex = POSBINDU_SEX.get(str(row.get("Jenis Kelamin") or "").strip(), "")
        if key and sex:
            sex_by_name[key] = sex

    rows: list[dict] = []
    digitised_months: set[str] = set()

    for _, row in digitised.iterrows():
        date = excel_date(row.get("Tanggal"))
        if date is None:
            continue
        digitised_months.add(date.strftime("%Y-%m"))
        rows.append({
            "tahun": date.year,
            "bulan": date.strftime("%Y-%m"),
            "sumber": "digitasi",
            "presisi": "sesi",
            "kriteria": str(row.get("Status Standar") or "").strip(),
            "jenis_kelamin": sex_by_name.get(_posbindu_key(row.get("Nama")), ""),
            "kualitas": str(row.get("Kualitas Transkripsi") or "").strip(),
            "peserta_ref": "",
            "urutan_kunjungan": "",
            "imt": _posbindu_number(row.get(imt_column)),
            **{field: _posbindu_number(row.get(column)) for field, column in POSBINDU_MEASURE_COLUMNS.items()},
        })

    # --- registry, unpivoted from five examination blocks to one row each -----
    skipped = {"bulan_sudah_didigitasi": 0, "di_luar_rentang": 0}
    undated = 0

    for position, (_, row) in enumerate(registry.iterrows()):
        if not str(row.get("Nama Lengkap") or "").strip():
            continue
        sex = POSBINDU_SEX.get(str(row.get("Jenis Kelamin") or "").strip(), "")
        kriteria = str(row.get("Kriteria") or "").strip()
        for visit in range(1, 6):
            measures = {
                "bb": _posbindu_number(row.get(f"BB{visit}")),
                "tb": _posbindu_number(row.get(f"TB{visit}")),
                "lp": _posbindu_number(row.get(f"LP{visit}")),
                "gula_darah": _posbindu_number(row.get(f"GDS{visit}")),
                "kolesterol": _posbindu_number(row.get(f"KLS{visit}")),
                "asam_urat": _posbindu_number(row.get(f"AU{visit}")),
            }
            # Blood pressure arrives as a single "135/83" cell.
            reading = re.match(r"^\s*(\d{2,3})\s*/\s*(\d{2,3})\s*$", str(row.get(f"TD{visit}") or "").strip())
            measures["sistolik"] = float(reading.group(1)) if reading else ""
            measures["diastolik"] = float(reading.group(2)) if reading else ""
            # Registry BMI columns are full of #VALUE!; it is recomputed in clean.
            measures["imt"] = ""
            if not any(value != "" for value in measures.values()):
                continue

            raw = row.get(f"Pemeriksaan {visit}")
            date = excel_date(raw) if str(raw or "").strip() not in {"", "-", "nan"} else None
            if date is not None and not POSBINDU_FIRST_YEAR <= date.year <= POSBINDU_LAST_HISTORY_YEAR:
                skipped["di_luar_rentang"] += 1
                continue
            if date is None:
                # Truncated text like "-Agustus 2" survives as a countable visit
                # with no year, never as a guess.
                undated += 1
                year, month, precision = "", "", "tidak pasti"
            else:
                month = date.strftime("%Y-%m")
                if month in digitised_months:
                    skipped["bulan_sudah_didigitasi"] += 1
                    continue
                year, precision = date.year, "bulan"

            rows.append({
                "tahun": year,
                "bulan": month,
                "sumber": "registri",
                "presisi": precision,
                "kriteria": kriteria,
                "jenis_kelamin": sex,
                "kualitas": "",
                "peserta_ref": position,
                "urutan_kunjungan": visit,
                **measures,
            })

    digitised_rows = sum(1 for row in rows if row["sumber"] == "digitasi")
    summary = {
        "sesi_digitasi": len(digitised_months),
        "baris_digitasi": digitised_rows,
        "baris_registri": len(rows) - digitised_rows,
        "registri_tanpa_tanggal": undated,
        "registri_dilewati": skipped,
        "gender_digitasi_dari_registri": sum(
            1 for row in rows if row["sumber"] == "digitasi" and row["jenis_kelamin"]
        ),
    }
    return pd.DataFrame(rows), summary


def main() -> None:
    ensure_directories()
    manifest: dict[str, dict] = {}

    def record(name: str, frame: pd.DataFrame, files: list[str], removed: int = 0) -> None:
        frame.to_csv(LOADED_DIR / f"{name}.csv", index=False)
        manifest[name] = {
            "files": files,
            "rows_loaded": len(frame) + removed,
            "rows_after_deduplication": len(frame),
            "duplicate_rows_removed": removed,
        }

    for name, pattern in DATASETS.items():
        frame, files = read_parts(pattern)
        loaded_rows = len(frame)
        clean = deduplicate(frame)
        record(name, clean, [path.name for path in files], loaded_rows - len(clean))
        if name in EXPECTED_MULTIPART and loaded_rows != EXPECTED_MULTIPART[name]:
            raise AssertionError(f"{name}: {loaded_rows} baris; seharusnya {EXPECTED_MULTIPART[name]}")

    publications = load_scival_publications()
    record("publications", publications, [SCIVAL_PUBLICATIONS])
    record("scival_subject_areas", read_scival(SCIVAL_SUBJECT_AREAS), [SCIVAL_SUBJECT_AREAS])

    department_lookup, department_lookup_files = load_department_lookup()
    record("publication_department_lookup", department_lookup, department_lookup_files)

    tck = load_tck()
    record("tck_2026_indikator", tck, [TCK_WORKBOOK.name, "tck_pillar.csv", "tck_meta.csv", "tck_2026_anggaran.json"])

    sdm_lecturers = load_sdm_lecturers()
    record("sdm_lecturers", sdm_lecturers, [SDM_LECTURERS_FILE])
    record("sdm_staff", load_sdm_staff(), [SDM_STAFF_FILE])
    record("sdm_professors", load_sdm_professors(), [SDM_PROFESSORS_FILE])
    record("sdm_certification", load_sdm_certification(), [SDM_CERTIFICATION_FILE])

    partnerships = load_partnerships()
    record("partnerships", partnerships, [path.name for path in sorted(PARTNERSHIP_DIR.glob("*DATA LENTERA*.xlsx"))])

    revenue = load_partnership_revenue()
    record("partnership_revenue", revenue, [REVENUE_WORKBOOK])
    record("school_mou", load_school_mou(), [SCHOOL_MOU_WORKBOOK])

    academic_loaders = {
        "admissions": (load_admissions, "PROFIL MABA.xlsx"),
        "active_students": (load_active_students, "7. Profil Mahasiswa S1.xlsx"),
        "graduates": (load_graduates, "PROFIL LULUSAN.xlsx"),
        "achievements": (load_achievements, "PRESTASI MAHASISWA.xlsx"),
        "scholarships": (load_scholarships, "PENERIMA BEASISWA.xlsx"),
        "accreditation": (load_accreditation, "AKREDITASI PRODI MIPA.xlsx"),
        "exchange": (load_exchange, "mahasiswa Exchange.xlsx"),
    }
    extra_sources = {
        "graduates": [filename for filename, _ in POSTGRADUATE_FILES.values()],
    }
    for name, (loader, source) in academic_loaders.items():
        record(name, loader(), [source, *extra_sources.get(name, [])])

    from student_origins import load_origins, SOURCE as ORIGINS_SOURCE
    record("student_origins", load_origins(), [ORIGINS_SOURCE])

    roster, roster_files = load_student_roster()
    record("student_roster", roster, roster_files)

    waiting, sectors, tracer_summary = load_tracer()
    record("tracer_waiting", waiting, ["25,26.Waktu tunggu.xls"])
    record("tracer_sectors", sectors, ["27,29.bidang kerja.xls"])
    manifest["tracer_waiting"]["summary_sumber"] = tracer_summary

    visits, participants = load_posbindu()
    record("posbindu_visits", visits, ["hasil-posbindu-melati-mipa rekap 2026.xlsx"])
    record("posbindu_participants", participants, ["Data Posbindu.xlsx"])

    history, history_summary = load_posbindu_history()
    record(
        "posbindu_history",
        history,
        [POSBINDU_HISTORY_FILE, POSBINDU_REGISTRY_FILE],
        # Registry rows for months the digitisation already covers are the only
        # rows dropped, and they are dropped to avoid counting a session twice.
        removed=history_summary["registri_dilewati"]["bulan_sudah_didigitasi"],
    )
    manifest["posbindu_history"]["rekonsiliasi"] = history_summary

    (LOADED_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"Loaded {len(DATASETS)} historical datasets, {len(publications)} SciVal publications, "
        f"{len(department_lookup)} curated department pairs, {len(tck)} TCK indicators, "
        f"{len(partnerships)} cooperation documents, {len(revenue)} cooperation contracts, "
        f"{len(sdm_lecturers)} lecturers from SIMASTER, {len(academic_loaders)} academic tables, "
        f"{len(roster)} student records across {len(roster_files)} cohorts, "
        f"{len(visits)} anonymised Posbindu visits for 2026, "
        f"and {len(history)} for 2022-2025."
    )


if __name__ == "__main__":
    main()
