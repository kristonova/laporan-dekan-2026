from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd


APP_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = APP_ROOT.parent
DATA_ROOT = WORKSPACE_ROOT / "data ugm"
SOURCE_DIR = DATA_ROOT / "p2m"
# Direct SciVal exports live beside the P2M database dumps. They carry the
# richer bibliometrics (FWCI, open access, prominence) the P2M mirror drops.
SCIVAL_DIR = SOURCE_DIR / "from_scival"
ACADEMIC_DIR = DATA_ROOT / "akademik"
PARTNERSHIP_DIR = DATA_ROOT / "kerjasama"
HEALTH_DIR = DATA_ROOT / "health promotion university posbindu"
TCK_DIR = WORKSPACE_ROOT / "target_capaian_kinerja"
TCK_2026_DIR = TCK_DIR / "tck_2026"
WORK_DIR = APP_ROOT / "pipeline" / "work"
LOADED_DIR = WORK_DIR / "loaded"
CLEAN_DIR = WORK_DIR / "cleaned"
DERIVED_DIR = APP_ROOT / "src" / "data" / "derived"
PUBLIC_DATA_DIR = APP_ROOT / "public" / "data"
MAPPINGS_DIR = APP_ROOT / "pipeline" / "mappings"

# Single source of truth for every "data ditarik per ..." label in the UI.
SNAPSHOT = "2026-08-31"
SNAPSHOT_LABEL = "31 Agustus 2026"
# Historical P2M exports and the LENTERA workbook were pulled on their own dates.
SNAPSHOT_P2M = "19 Agustus 2026"
SNAPSHOT_LENTERA = "20 Agustus 2026"
# SciVal reports its own "date last updated"; publication counts, topics,
# collaboration, and SDG tags carry this date rather than the P2M pull date.
SNAPSHOT_SCIVAL = "30 Agustus 2026"


def ensure_directories() -> None:
    for directory in (LOADED_DIR, CLEAN_DIR, DERIVED_DIR, PUBLIC_DATA_DIR, MAPPINGS_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def read_parts(pattern: str) -> tuple[pd.DataFrame, list[Path]]:
    files = sorted(SOURCE_DIR.glob(pattern))
    if not files:
        raise FileNotFoundError(f"Tidak ada sumber untuk pola: {pattern}")
    frames = [pd.read_csv(path, low_memory=False) for path in files]
    return pd.concat(frames, ignore_index=True), files


def read_workbook(path: Path, sheet: Any = 0, header: Any = None) -> pd.DataFrame:
    """Read one sheet of an .xlsx/.xls workbook as raw positional cells.

    Every source workbook here uses merged, multi-row headers, so the default is
    ``header=None``: callers slice the rows they need and name columns themselves
    rather than fighting pandas' header inference.
    """
    if not path.exists():
        raise FileNotFoundError(f"Berkas sumber tidak ditemukan: {path}")
    engine = "xlrd" if path.suffix.lower() == ".xls" else "openpyxl"
    return pd.read_excel(path, sheet_name=sheet, header=header, engine=engine, dtype=object)


def workbook_sheets(path: Path) -> list[str]:
    engine = "xlrd" if path.suffix.lower() == ".xls" else "openpyxl"
    with pd.ExcelFile(path, engine=engine) as book:
        return list(book.sheet_names)


def cell(row: pd.Series, index: int) -> Any:
    """Positional cell access that tolerates short rows and NaN padding."""
    if index >= len(row):
        return None
    value = row.iloc[index]
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    return value


def text_cell(row: pd.Series, index: int) -> str:
    value = cell(row, index)
    return "" if value is None else str(value).strip()


def numeric_cell(row: pd.Series, index: int) -> float | None:
    """Parse a spreadsheet cell into a float, rejecting Excel error strings."""
    value = cell(row, index)
    if value is None:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return None if math.isnan(float(value)) else float(value)
    text = str(value).strip()
    if not text or text.startswith("#"):
        return None
    text = text.replace(" ", "").replace(" ", "")
    # Indonesian sheets mix "1.234,56" and plain "1234.56"; normalise both.
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    elif "," in text:
        text = text.replace(",", ".")
    try:
        parsed = float(text)
    except ValueError:
        return None
    return None if math.isnan(parsed) else parsed


def excel_date(value: Any) -> pd.Timestamp | None:
    """Convert an Excel serial number (or already-parsed date) to a Timestamp."""
    if value is None:
        return None
    if isinstance(value, pd.Timestamp):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if math.isnan(float(value)) or float(value) <= 0:
            return None
        return pd.Timestamp("1899-12-30") + pd.Timedelta(days=float(value))
    text = str(value).strip()
    # ISO timestamps come back from openpyxl already parsed; only the loose
    # Indonesian "dd/mm/yyyy" strings need dayfirst.
    dayfirst = not re.match(r"^\d{4}-\d{2}-\d{2}", text)
    parsed = pd.to_datetime(text, errors="coerce", dayfirst=dayfirst)
    return None if pd.isna(parsed) else parsed


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    if "Id" in df.columns:
        return df.drop_duplicates(subset=["Id"], keep="last").reset_index(drop=True)
    return df.drop_duplicates().reset_index(drop=True)


def number(value: Any, default: float = 0.0) -> float:
    try:
        converted = float(value)
        return converted if math.isfinite(converted) else default
    except (TypeError, ValueError):
        return default


def json_value(value: Any) -> Any:
    if value is None or value is pd.NA:
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if math.isnan(float(value)) else float(value)
    if isinstance(value, float):
        return None if math.isnan(value) else value
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [json_value(item) for item in value]
    return value


def write_json(filename: str, rows: Any, mirror_public: bool = True) -> None:
    ensure_directories()
    payload = json.dumps(json_value(rows), ensure_ascii=False, indent=2, sort_keys=False)
    (DERIVED_DIR / filename).write_text(payload + "\n", encoding="utf-8")
    if mirror_public:
        (PUBLIC_DATA_DIR / filename).write_text(payload + "\n", encoding="utf-8")


def records(df: pd.DataFrame) -> list[dict[str, Any]]:
    return [json_value(row) for row in df.to_dict(orient="records")]


def slug_key(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def split_pipe(value: Any) -> list[str]:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return []
    return [part.strip() for part in str(value).split("|") if part.strip()]


def safe_year(series: pd.Series, minimum: int = 1900, maximum: int = 2100) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    return numeric.where(numeric.between(minimum, maximum)).astype("Int64")


def year_from_date(series: pd.Series, minimum: int = 1900, maximum: int = 2100) -> pd.Series:
    parsed = pd.to_datetime(series, errors="coerce")
    return parsed.dt.year.where(parsed.dt.year.between(minimum, maximum)).astype("Int64")


def require_columns(df: pd.DataFrame, columns: Iterable[str], label: str) -> None:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(f"{label}: kolom hilang {missing}")
