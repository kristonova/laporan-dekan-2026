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
SOURCE_DIR = WORKSPACE_ROOT / "data ugm"
TCK_DIR = WORKSPACE_ROOT / "target_capaian_kinerja"
WORK_DIR = APP_ROOT / "pipeline" / "work"
LOADED_DIR = WORK_DIR / "loaded"
CLEAN_DIR = WORK_DIR / "cleaned"
DERIVED_DIR = APP_ROOT / "src" / "data" / "derived"
PUBLIC_DATA_DIR = APP_ROOT / "public" / "data"
MAPPINGS_DIR = APP_ROOT / "pipeline" / "mappings"


def ensure_directories() -> None:
    for directory in (LOADED_DIR, CLEAN_DIR, DERIVED_DIR, PUBLIC_DATA_DIR, MAPPINGS_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def read_parts(pattern: str) -> tuple[pd.DataFrame, list[Path]]:
    files = sorted(SOURCE_DIR.glob(pattern))
    if not files:
        raise FileNotFoundError(f"Tidak ada sumber untuk pola: {pattern}")
    frames = [pd.read_csv(path, low_memory=False) for path in files]
    return pd.concat(frames, ignore_index=True), files


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
