#!/usr/bin/env python3
"""Load every source part once, deduplicate deterministically, and record provenance."""

from __future__ import annotations

import json
import re

import pandas as pd

from utils import (
    ACADEMIC_DIR,
    HEALTH_DIR,
    LOADED_DIR,
    MAPPINGS_DIR,
    PARTNERSHIP_DIR,
    TCK_2026_DIR,
    cell,
    deduplicate,
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


def load_student_roster() -> tuple[pd.DataFrame, list[str]]:
    """Per-cohort student rosters, stripped of every personal column at load.

    Returns the frame plus the file names that produced it, because this is the
    one loader that reads a whole directory instead of a single workbook.
    """
    paths = sorted(ROSTER_DIR.glob("Daftar mahasiswa *.xlsx"))
    if not paths:
        raise FileNotFoundError(f"Tidak ada berkas daftar mahasiswa di {ROSTER_DIR}")

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
    return frame[~frame.set_index(["jenjang", "tahun"]).index.isin(empty)].reset_index(drop=True)


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
    grid = read_workbook(ACADEMIC_DIR / "24.Penerima Beasiswa.xlsx", "Rekapitulasi")
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

    Both sheets end with a Rekap block whose numbered rows would otherwise parse
    as programmes; a real entry always carries a YYYY-YYYY validity period, so
    that is what separates the two.
    """
    path = ACADEMIC_DIR / "13-14.Akreditasi sarjana dan pascasarjana.xlsx"
    rows: list[dict] = []

    national = read_workbook(path, "AKREDITASI NASIONAL")
    for _, row in national.iloc[3:].iterrows():
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
    group = ""
    for _, row in international.iloc[1:].iterrows():
        first = text_cell(row, 0)
        if first.upper() in {"SARJANA", "PASCASARJANA"}:
            group = first.title()
            continue
        if first.lower() == "rekap":
            break
        if not first.isdigit() or not PERIOD_PATTERN.match(text_cell(row, 3)):
            continue
        rows.append({
            "lingkup": "Internasional",
            "jenjang_grup": group,
            "departemen": "",
            "prodi": text_cell(row, 1),
            "lembaga": text_cell(row, 2),
            "periode": text_cell(row, 3),
            "nilai": "",
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

    tck = load_tck()
    record("tck_2026_indikator", tck, [TCK_WORKBOOK.name, "tck_pillar.csv", "tck_meta.csv", "tck_2026_anggaran.json"])

    partnerships = load_partnerships()
    record("partnerships", partnerships, [path.name for path in sorted(PARTNERSHIP_DIR.glob("*DATA LENTERA*.xlsx"))])

    academic_loaders = {
        "admissions": (load_admissions, "PROFIL MABA.xlsx"),
        "active_students": (load_active_students, "7. Profil Mahasiswa S1.xlsx"),
        "graduates": (load_graduates, "PROFIL LULUSAN.xlsx"),
        "achievements": (load_achievements, "PRESTASI MAHASISWA.xlsx"),
        "scholarships": (load_scholarships, "24.Penerima Beasiswa.xlsx"),
        "accreditation": (load_accreditation, "13-14.Akreditasi sarjana dan pascasarjana.xlsx"),
        "exchange": (load_exchange, "mahasiswa Exchange.xlsx"),
    }
    for name, (loader, source) in academic_loaders.items():
        record(name, loader(), [source])

    roster, roster_files = load_student_roster()
    record("student_roster", roster, roster_files)

    waiting, sectors, tracer_summary = load_tracer()
    record("tracer_waiting", waiting, ["25,26.Waktu tunggu.xls"])
    record("tracer_sectors", sectors, ["27,29.bidang kerja.xls"])
    manifest["tracer_waiting"]["summary_sumber"] = tracer_summary

    visits, participants = load_posbindu()
    record("posbindu_visits", visits, ["hasil-posbindu-melati-mipa rekap 2026.xlsx"])
    record("posbindu_participants", participants, ["Data Posbindu.xlsx"])

    (LOADED_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"Loaded {len(DATASETS)} historical datasets, {len(tck)} TCK indicators, "
        f"{len(partnerships)} cooperation documents, {len(academic_loaders)} academic tables, "
        f"{len(roster)} student records across {len(roster_files)} cohorts, "
        f"and {len(visits)} anonymised Posbindu visits."
    )


if __name__ == "__main__":
    main()
