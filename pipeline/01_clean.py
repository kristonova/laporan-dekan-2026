#!/usr/bin/env python3
"""Normalize known quality issues and remove person-level fields before aggregation."""

from __future__ import annotations

import json
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


# --- TCK 2026 ---------------------------------------------------------------

# Published status thresholds. The workbook only distinguishes "tercapai" from
# "belum", so the four levels the report uses are derived from the ratio here and
# documented on /data. `arah = turun` indicators invert the ratio: a smaller
# actual is better.
STATUS_THRESHOLDS = ((1.00, "tercapai"), (0.85, "mendekati"), (0.50, "tertinggal"))
RUPIAH_TO_MILIAR = 1_000_000_000
# Indicator 1c mixes units: targets are stated in billions, actuals in full
# rupiah. Anything above this bound is a raw rupiah figure to rescale.
MILIAR_SCALE_BOUND = 10_000


def status_for(ratio: float | None) -> str:
    if ratio is None:
        return "meleset"
    for bound, label in STATUS_THRESHOLDS:
        if ratio >= bound:
            return label
    return "meleset"


def ratio_for(actual: float | None, target: float | None, direction: str) -> float | None:
    if actual is None or target is None:
        return None
    if direction == "turun":
        if actual <= 0:
            return 2.5
        return round(target / actual, 4)
    if target <= 0:
        return None
    return round(actual / target, 4)


QUARTERS = ("tw1", "tw2", "tw3", "tw4")


def is_number(value: object) -> bool:
    return value is not None and not pd.isna(value)


def rescale_creative_funding(row: dict) -> None:
    """Indicator 1c states targets in billions but actuals in full rupiah."""
    fields = [f"capaian_{q}" for q in QUARTERS] + [f"target_{q}" for q in QUARTERS]
    fields += ["target_tahunan", "dike", "df", "dm", "dk", "fakultas"]
    for field in fields:
        value = row.get(field)
        if is_number(value) and abs(value) > MILIAR_SCALE_BOUND:
            row[field] = round(value / RUPIAH_TO_MILIAR, 4)


def normalize_percentage(row: dict) -> tuple[bool, list[str]]:
    """Separate real percentages from headcounts on `satuan = Persen` rows.

    The workbook stores a percentage either as a fraction (0–1) or as the bare
    numerator of that fraction; the denominator is never written down. Fractions
    are scaled to percent, numerators are moved to a `_cacah` column and the
    percentage is left empty rather than guessed. Indicators whose actuals are
    all outside 0–1 (such as #32) carry no fraction at all and are left alone.
    """
    notes: list[str] = []
    for quarter in QUARTERS:
        field = f"target_{quarter}"
        value = row.get(field)
        if is_number(value) and 0 < value <= 1:
            row[field] = round(value * 100, 4)

    actuals = {quarter: row.get(f"capaian_{quarter}") for quarter in QUARTERS}
    has_fraction = any(is_number(value) and 0 < value <= 1 for value in actuals.values())
    if not has_fraction:
        return False, notes

    headcount_quarters: list[str] = []
    for quarter, value in actuals.items():
        if not is_number(value):
            continue
        if 0 < value <= 1:
            row[f"capaian_{quarter}"] = round(value * 100, 4)
        elif value > 1:
            row[f"capaian_{quarter}_cacah"] = value
            row[f"capaian_{quarter}"] = None
            headcount_quarters.append(quarter.upper())

    if headcount_quarters:
        notes.append(
            f"capaian {', '.join(headcount_quarters)} tercatat sebagai cacah orang tanpa penyebut; "
            "persentase tidak dihitung"
        )
    return bool(headcount_quarters), notes


def assessed_quarter(row: dict) -> tuple[str, float | None, float | None]:
    """Latest quarter that has both an actual and a target to judge against."""
    for quarter in ("tw3", "tw2", "tw1"):
        actual = row.get(f"capaian_{quarter}")
        target = row.get(f"target_{quarter}")
        if is_number(actual) and is_number(target):
            return quarter, actual, target
    return "tw3", row.get("capaian_tw3"), row.get("target_tw3")


def clean_tck() -> None:
    """Recompute ratios and statuses, and surface the workbook's unit problems.

    Nothing here patches a defect silently: rescaling, missing denominators, and
    non-cumulative quarters each leave a note in `anomali` that /data renders.
    """
    tck = pd.read_csv(LOADED_DIR / "tck_2026_indikator.csv", dtype={"no": "string"})

    rows: list[dict] = []
    for _, source in tck.iterrows():
        row = source.to_dict()
        for quarter in QUARTERS:
            row[f"capaian_{quarter}_cacah"] = None
        direction = str(row.get("arah") or "naik").strip() or "naik"
        anomalies: list[str] = []
        unit_mismatch = False

        if str(row["no"]) == "1c":
            rescale_creative_funding(row)
            anomalies.append("nilai rupiah penuh pada sumber diskalakan ke miliar")

        if str(row.get("satuan") or "").strip().lower() == "persen":
            unit_mismatch, notes = normalize_percentage(row)
            anomalies.extend(notes)

        row["target_tw4"] = row.get("target_tahunan")

        quarter, actual, target = assessed_quarter(row)
        row["kuartal_dinilai"] = quarter
        row["capaian_dinilai"] = actual
        row["target_dinilai"] = target
        row["rasio_kuartal"] = ratio_for(actual, target, direction)
        row["status_kuartal"] = status_for(row["rasio_kuartal"])
        row["rasio_thd_target_tahunan"] = ratio_for(actual, row.get("target_tahunan"), direction)
        row["status_thd_tahunan"] = status_for(row["rasio_thd_target_tahunan"])
        if quarter != "tw3":
            anomalies.append(f"penilaian memakai {quarter.upper()} karena TW3 tidak dapat dinilai")

        # A "turun" indicator is supposed to fall quarter over quarter, so only
        # the cumulative ones are checked for a backwards step.
        if direction != "turun":
            progression = [row.get(f"capaian_{quarter}") for quarter in ("tw1", "tw2", "tw3")]
            progression = [value for value in progression if is_number(value)]
            if any(after < before for before, after in zip(progression, progression[1:])):
                anomalies.append("capaian triwulan tidak kumulatif")

        row["unit_mismatch"] = unit_mismatch
        row["anomali"] = "; ".join(anomalies)
        rows.append(row)

    pd.DataFrame(rows).to_csv(CLEAN_DIR / "tck_2026_indikator.csv", index=False)


# --- Kerja sama -------------------------------------------------------------


def clean_partnerships(province_lookup: dict) -> None:
    """One row per cooperation document, with location and scope normalised."""
    source = pd.read_csv(LOADED_DIR / "partnerships.csv").fillna("")
    start = pd.to_datetime(source["mulai"], errors="coerce")
    signed = pd.to_datetime(source["tanggal_tanda_tangan"], errors="coerce")
    year = signed.dt.year.fillna(start.dt.year).fillna(source["tahun_sheet"]).astype(int)

    raw_province = source["provinsi"].astype(str).str.strip()
    mapped = raw_province.map(lambda value: province_lookup.get(value, {}))
    country = source["negara"].astype(str).str.strip().replace("", "Tidak diketahui")

    clean = pd.DataFrame({
        "tahun": year,
        "negara": country,
        "lingkup": country.map(lambda value: "Domestik" if value == "Indonesia" else "Internasional"),
        "jenis_mitra": source["jenis_mitra"].astype(str).str.strip().replace("", "Tidak terklasifikasi"),
        "tipe_dokumen": source["tipe_dokumen"].astype(str).str.strip().replace("", "Tidak terklasifikasi"),
        "provinsi_raw": raw_province,
        "provinsi": mapped.map(lambda value: value.get("canonical", "") if isinstance(value, dict) else ""),
        "bps_code": mapped.map(lambda value: value.get("bps_code", "") if isinstance(value, dict) else ""),
        "kabupaten": source["kabupaten"].astype(str).str.strip(),
        "prodi": source["prodi"].astype(str).str.strip(),
        "bidang": source["bidang"].astype(str).str.strip(),
    })
    clean["location_status"] = "recorded"
    clean.loc[clean["lingkup"] == "Internasional", "location_status"] = "foreign"
    clean.loc[(clean["lingkup"] == "Domestik") & (clean["provinsi"] == ""), "location_status"] = "missing"
    clean.to_csv(CLEAN_DIR / "partnerships.csv", index=False)


# --- Tracer study -----------------------------------------------------------

# Waiting time is reported in months; negative values mean the graduate was
# already working before the graduation date.
WAITING_BUCKETS = (
    (0, "Sudah bekerja sebelum lulus"),
    (3, "0–3 bulan"),
    (6, "4–6 bulan"),
    (12, "7–12 bulan"),
    (float("inf"), "Lebih dari 12 bulan"),
)


def waiting_bucket(months: float) -> str:
    for bound, label in WAITING_BUCKETS:
        if months <= bound:
            return label
    return WAITING_BUCKETS[-1][1]


def clean_tracer() -> None:
    waiting = pd.read_csv(LOADED_DIR / "tracer_waiting.csv")
    waiting["kategori"] = waiting["bulan"].map(waiting_bucket)
    waiting["prodi"] = waiting["prodi"].astype(str).str.strip().str.title()
    waiting[["prodi", "tahun", "bulan", "kategori"]].to_csv(CLEAN_DIR / "tracer_waiting.csv", index=False)

    rules = pd.read_csv(MAPPINGS_DIR / "bidang_kerja.csv")
    compiled = [(re.compile(pattern, re.I), sector) for pattern, sector in zip(rules["pola"], rules["sektor"])]

    def classify(value: object) -> str:
        text = str(value or "").strip().lower()
        for pattern, sector in compiled:
            if pattern.search(text):
                return sector
        return "Lainnya"

    sectors = pd.read_csv(LOADED_DIR / "tracer_sectors.csv")
    sectors["sektor"] = sectors["bidang_raw"].map(classify)
    sectors["prodi"] = sectors["prodi"].astype(str).str.strip().str.title()
    sectors[["prodi", "tahun", "sektor"]].to_csv(CLEAN_DIR / "tracer_sectors.csv", index=False)


# --- Health Promoting University --------------------------------------------

# The recap sheets use slightly different spellings across months; these keep the
# published categories stable without inventing clinical judgements.
POSBINDU_LABELS = {
    "imt": {"underweight": "Kurang", "normal": "Normal", "overweight": "Berlebih", "obesity": "Obesitas"},
    "tekanan_darah": {
        "normal": "Normal", "prehipertensi": "Prehipertensi",
        "hipertensi grade 1": "Hipertensi Grade 1", "hipertensi grade 2": "Hipertensi Grade 2",
    },
    "lingkar_perut": {"normal": "Normal", "tidak normal": "Tidak Normal"},
    "asam_urat": {"normal": "Normal", "tinggi": "Tinggi"},
    "kolesterol": {"normal": "Normal", "waspada": "Waspada", "tinggi": "Tinggi"},
    "gula_darah": {"normal": "Normal", "waspada": "Waspada", "tinggi": "Tinggi"},
}

POSBINDU_MEASURES = ["imt", "tekanan_darah", "lingkar_perut", "asam_urat", "kolesterol", "gula_darah"]

# Screening staff, so the two categories the report is about are spelled one
# way. The 2022-2025 sources spell the same roles differently again, so their
# labels join the same table rather than becoming separate categories.
POSBINDU_CRITERIA = {
    "dosen": "Dosen",
    "tendik": "Tendik", "tenaga kependidikan": "Tendik",
    "thl": "THL", "tenaga harian lepas": "THL",
    "mahasiswa": "Mahasiswa",
    "cleaning service": "Cleaning Service",
    "asisten": "Asisten",
    "lain-lain": "Lainnya", "lainnya (kode l)": "Lainnya",
    # The source itself could not place these; they are not guessed here.
    "perlu klasifikasi": "Tanpa kriteria", "belum dipastikan": "Tanpa kriteria",
}


def normalize_measure(column: str, value: object) -> str:
    text = str(value or "").strip()
    if not text or text in {"-", "nan"}:
        return "Tidak diperiksa"
    lookup = POSBINDU_LABELS.get(column, {})
    return lookup.get(text.lower(), text.title())


def risk_bands() -> dict[tuple[str, str], str]:
    """Source category to risk band, from the reviewable mapping table.

    The clinical judgement lives in pipeline/mappings/posbindu_risiko.csv so the
    data owner can check it without reading code.
    """
    table = pd.read_csv(MAPPINGS_DIR / "posbindu_risiko.csv")
    return {
        (str(row.indikator).strip(), str(row.nilai_sumber).strip()): str(row.pita).strip()
        for row in table.itertuples()
    }


def clean_posbindu() -> None:
    visits = pd.read_csv(LOADED_DIR / "posbindu_visits.csv").fillna("")
    bands = risk_bands()

    clean = pd.DataFrame({"tanggal": visits["tanggal"]})
    for column in POSBINDU_MEASURES:
        clean[column] = visits[column].map(lambda value, column=column: normalize_measure(column, value))
        # "Tidak diperiksa" stays its own band; it is never folded into Normal.
        clean[f"risiko_{column}"] = clean[column].map(
            lambda label, column=column: bands.get((column, label), "Tidak diperiksa")
        )
    clean["dirujuk"] = visits["rujukan"].astype(str).str.strip().str.lower().eq("rujuk")
    clean["kriteria"] = (
        visits["kriteria"].astype(str).str.strip()
        .map(lambda value: POSBINDU_CRITERIA.get(value.lower(), value.title() if value else "Tanpa kriteria"))
    )
    clean.to_csv(CLEAN_DIR / "posbindu_visits.csv", index=False)

    participants = pd.read_csv(LOADED_DIR / "posbindu_participants.csv").fillna("")
    participants["kriteria"] = participants["kriteria"].astype(str).str.strip().replace("", "Tidak diketahui")
    participants[["kriteria"]].to_csv(CLEAN_DIR / "posbindu_participants.csv", index=False)


# --- Posbindu 2022-2025: categories recomputed from raw measurements ---------

# The 2022-2025 sources recorded numbers, not interpretations. The 2026 workbook
# recorded both, which is what makes the older years recoverable: the thresholds
# below were read back off the 2026 pairs and reproduce its own labels exactly
# (blood pressure, waist, uric acid, cholesterol and glucose all 100%; BMI on
# 273 of 278, the five gaps being rows where the source contradicts its own
# numbers). Applying them to 2022-2025 therefore yields a series that is
# comparable with 2026 rather than merely adjacent to it.
POSBINDU_HISTORY_MEASURES = {
    "imt": "imt",
    "lingkar_perut": "lp",
    "asam_urat": "asam_urat",
    "kolesterol": "kolesterol",
    "gula_darah": "gula_darah",
}

# Waist circumference and uric acid are the two indicators whose cut-off depends
# on sex. The digitisation sheet never recorded it, so a row without a sex is
# left unassessed rather than assessed against the wrong threshold.
POSBINDU_SEXED = {"lingkar_perut", "asam_urat"}


def posbindu_thresholds() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Clinical cut-offs, from the two reviewable mapping tables.

    Kept beside posbindu_risiko.csv for the same reason: the data owner can
    check the clinical judgement without reading code.
    """
    single = pd.read_csv(MAPPINGS_DIR / "posbindu_ambang.csv")
    tension = pd.read_csv(MAPPINGS_DIR / "posbindu_ambang_tensi.csv")
    return single.sort_values("urutan"), tension.sort_values("urutan")


def classify_measure(table: pd.DataFrame, measure: str, value: object, sex: str) -> str:
    """First matching rule wins, in the order the mapping table lists them."""
    if value == "" or pd.isna(value):
        return ""
    rules = table[table["indikator"] == measure]
    if measure in POSBINDU_SEXED:
        if not sex:
            return ""
        rules = rules[rules["jenis_kelamin"] == sex]
    for rule in rules.itertuples():
        operator = str(rule.operator).strip()
        if operator == "selain itu":
            return str(rule.nilai_sumber)
        if operator == "<" and float(value) < float(rule.ambang):
            return str(rule.nilai_sumber)
        if operator == "<=" and float(value) <= float(rule.ambang):
            return str(rule.nilai_sumber)
    return ""


def classify_tension(table: pd.DataFrame, systolic: object, diastolic: object) -> str:
    """Blood pressure needs both readings, so it has its own small table."""
    if systolic == "" or diastolic == "" or pd.isna(systolic) or pd.isna(diastolic):
        return ""
    for rule in table.itertuples():
        if pd.isna(rule.sistolik_minimal) and pd.isna(rule.diastolik_minimal):
            return str(rule.nilai_sumber)
        if float(systolic) >= float(rule.sistolik_minimal) or float(diastolic) >= float(rule.diastolik_minimal):
            return str(rule.nilai_sumber)
    return ""


def clean_posbindu_history() -> None:
    history = pd.read_csv(LOADED_DIR / "posbindu_history.csv")
    single, tension = posbindu_thresholds()
    bands = risk_bands()

    def number(column: str) -> pd.Series:
        return pd.to_numeric(history[column], errors="coerce")

    weight, height = number("bb"), number("tb")
    # The digitisation sheet carries a computed BMI; the registry carries a
    # column full of #VALUE!. Either way it is recomputed where the inputs exist.
    body_mass = number("imt").where(lambda series: series.notna(), weight / (height / 100) ** 2)
    body_mass = body_mass.where(height > 0)

    values = {
        "imt": body_mass,
        "lp": number("lp"),
        "asam_urat": number("asam_urat"),
        "kolesterol": number("kolesterol"),
        "gula_darah": number("gula_darah"),
    }
    systolic, diastolic = number("sistolik"), number("diastolik")
    sex = history["jenis_kelamin"].fillna("").astype(str).str.strip()

    clean = pd.DataFrame({
        "tahun": history["tahun"].fillna("").map(lambda year: "" if year == "" else str(int(year))),
        # Month, not date: the registry never had a trustworthy day, so service
        # cadence is counted in months across every source.
        "bulan": history["bulan"].fillna(""),
        "presisi": history["presisi"],
        "sumber": history["sumber"],
        "kualitas": history["kualitas"].fillna("Tidak dicatat").replace("", "Tidak dicatat"),
        "jenis_kelamin": sex.replace("", "Tidak diketahui"),
        "peserta_ref": history["peserta_ref"].fillna(""),
        "urutan_kunjungan": history["urutan_kunjungan"].fillna(""),
    })

    for measure, column in POSBINDU_HISTORY_MEASURES.items():
        series = values[column]
        raw = [classify_measure(single, measure, value, row_sex) for value, row_sex in zip(series, sex)]
        clean[measure] = [normalize_measure(measure, label) for label in raw]
        clean[f"risiko_{measure}"] = clean[measure].map(
            lambda label, measure=measure: bands.get((measure, label), "Tidak diperiksa")
        )
        # A reading that exists but cannot be judged for want of a sex is not the
        # same as no reading at all, and the two are never merged in the totals.
        clean[f"terukur_{measure}"] = series.notna()

    raw_tension = [classify_tension(tension, top, bottom) for top, bottom in zip(systolic, diastolic)]
    clean["tekanan_darah"] = [normalize_measure("tekanan_darah", label) for label in raw_tension]
    clean["risiko_tekanan_darah"] = clean["tekanan_darah"].map(
        lambda label: bands.get(("tekanan_darah", label), "Tidak diperiksa")
    )
    clean["terukur_tekanan_darah"] = systolic.notna() & diastolic.notna()

    clean["kriteria"] = (
        history["kriteria"].fillna("").astype(str).str.strip()
        .map(lambda value: POSBINDU_CRITERIA.get(value.lower(), value.title() if value else "Tanpa kriteria"))
    )
    # How many of the six indicators put this visit in the highest band at once.
    clean["jumlah_berisiko"] = sum(
        clean[f"risiko_{measure}"].eq("Berisiko").astype(int) for measure in POSBINDU_MEASURES
    )
    clean["jumlah_diperiksa"] = sum(
        clean[f"risiko_{measure}"].ne("Tidak diperiksa").astype(int) for measure in POSBINDU_MEASURES
    )
    clean.to_csv(CLEAN_DIR / "posbindu_history.csv", index=False)


# --- Academic labels ---------------------------------------------------------

# Programme and department names arrive shouted from the source spreadsheets,
# and one of them carries a literal newline from a wrapped Excel cell. They are
# printed as prose on the page, so they are tidied here rather than per scene —
# that way the downloadable CSVs read the same as the charts.
LABEL_CONNECTORS = {"dan", "atau", "di", "ke", "dari", "yang", "untuk", "pada", "dalam", "serta"}
LABEL_ACRONYMS = {"S1", "S2", "S3", "IKE", "ELINS", "FMIPA", "UGM", "MIPA", "IUP"}


def tidy_label(value: object) -> str:
    """Collapse stray whitespace and recase a shouted label to Title Case."""
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    # Only all-caps values are recased; anything already mixed is left as written.
    if not text or not text.isupper():
        return text
    words = []
    for index, word in enumerate(text.split(" ")):
        if word.strip(".") in LABEL_ACRONYMS:
            words.append(word)
            continue
        lowered = word.lower()
        words.append(lowered if index and lowered.strip(".") in LABEL_CONNECTORS
                     else lowered[:1].upper() + lowered[1:])
    return " ".join(words)


# --- Daftar mahasiswa --------------------------------------------------------

# Programmes prefixed "ND" in the roster are non-degree: inbound exchange and
# MBKM participants who never enter a degree cohort. They are kept, but tagged,
# because mixing them into the S1 counts is what makes this file disagree with
# the registration figures in PROFIL MABA.
NON_DEGREE_PREFIX = "ND "
# Department names are spelled exactly as `admissions.csv` spells them, so a
# programme keeps one colour and one label across every scene of the report.
PROGRAMME_DEPARTMENT = {
    "fisika": "Dep. Fisika",
    "geofisika": "Dep. Fisika",
    "elektronika dan instrumentasi": "Dep IKE",
    "ilmu komputer": "Dep IKE",
    "kimia": "Dep Kimia",
    "matematika": "Dep Matematika",
    "statistika": "Dep Matematika",
    "ilmu aktuaria": "Dep Matematika",
}
# The source distinguishes ten final statuses. Five groups are enough to read a
# cohort's outcome, and grouping them here keeps the suppression threshold from
# erasing the rare ones entirely.
STATUS_GROUPS = {
    "LULUS": "Lulus",
    "AKTIF": "Masih aktif",
    "REGISTRASI": "Masih aktif",
    "KAMPUS MERDEKA": "Masih aktif",
    "CUTI DENGAN IJIN": "Masih aktif",
    "MENGUNDURKAN DIRI": "Mengundurkan diri",
    "NON AKTIF": "Tidak aktif",
    "HILANG": "Tidak aktif",
    "SELESAI PENDIDIKAN NON GE": "Selesai non-gelar",
    "MENINGGAL DUNIA": "Lainnya",
}
# Six provinces carry the bulk of the intake; the split is what the "is FMIPA
# becoming national or staying local?" scene is about.
JAVA_PROVINCES = {
    "Jawa Tengah", "Daerah Istimewa Yogyakarta", "DKI Jakarta",
    "Jawa Barat", "Jawa Timur", "Banten",
}
UNKNOWN_PROVINCE = "Tidak teridentifikasi"


def programme_parts(value: object) -> tuple[str, str, str]:
    """Split a roster programme cell into level, tidy programme, and department."""
    raw = re.sub(r"\s+", " ", str(value or "")).strip()
    if not raw:
        return "", "", "Belum terpetakan"
    non_degree = raw.upper().startswith(NON_DEGREE_PREFIX)
    bare = raw.split(" ", 1)[1] if (non_degree or raw.upper().startswith("S1 ")) else raw
    department = PROGRAMME_DEPARTMENT.get(bare.strip().lower(), "Belum terpetakan")
    return ("Non-gelar" if non_degree else "Sarjana"), tidy_label(bare), department


# School names are shouted in the source too, but `tidy_label` would turn SMAN
# into "Sman". The school-type prefixes are the part readers scan for, so they
# stay upper-case while the place name is recased.
SCHOOL_ACRONYMS = {
    "SMA", "SMAN", "SMAS", "SMK", "SMKN", "SMKS", "SMU", "SMTA",
    "MA", "MAN", "MAS", "MTS", "SMP", "SMPN", "SD", "SDN",
    "IT", "IPA", "IPS", "PPMI", "PGRI", "NU", "BPK", "UGM",
}


def tidy_school(value: object) -> str:
    """Recase a shouted school name, preserving the school-type acronym."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = re.sub(r"\s+", " ", str(value)).strip()
    if not text:
        return ""
    # A handful of rows carry the source's own catch-all instead of a school.
    # It is not a school, so it is dropped rather than charted as the seventh
    # largest feeder; the count of unrecorded schools is published separately.
    if re.fullmatch(r"[A-Za-z/ ]*lain[- ]?lain", text, re.I):
        return ""
    words = []
    for word in text.split(" "):
        parts = []
        for part in word.split("/"):
            if part.strip(".,").upper() in SCHOOL_ACRONYMS:
                parts.append(part.upper())
            elif part.isupper():
                parts.append(part[:1] + part[1:].lower())
            else:
                parts.append(part)
        words.append("/".join(parts))
    return " ".join(words)


def clean_students(province_lookup: dict) -> None:
    """Group the roster's free-text columns into the categories the report shows.

    Nothing here re-identifies anyone: the loader already dropped every personal
    column, so this stage only rewrites category labels.
    """
    roster = pd.read_csv(LOADED_DIR / "student_roster.csv", low_memory=False)

    pathway_rules = pd.read_csv(MAPPINGS_DIR / "jalur_masuk.csv")
    pathway_map = {str(raw).strip().lower(): group for raw, group
                   in zip(pathway_rules["raw"], pathway_rules["kelompok"])}

    occupation_rules = pd.read_csv(MAPPINGS_DIR / "pekerjaan_wali.csv")
    occupation_patterns = [(re.compile(pattern, re.I), group) for pattern, group
                           in zip(occupation_rules["pola"], occupation_rules["kelompok"])]
    # The lookup shipped for partnerships is exact-case; the roster shouts some
    # of the same names, so it is re-keyed case-insensitively here.
    province_by_name = {str(raw).strip().lower(): value for raw, value in province_lookup.items()}

    def pathway(value: object) -> str:
        key = str(value or "").strip().lower()
        if not key or key == "nan":
            return "Tidak tercatat"
        group = pathway_map.get(key)
        if group is None:
            raise ValueError(f"Jalur masuk belum dipetakan: {value!r}")
        return group

    def occupation(value: object) -> str:
        text = str(value or "").strip().lower()
        if not text or text == "nan":
            return "Tidak dilaporkan"
        for pattern, group in occupation_patterns:
            if pattern.search(text):
                return group
        return "Tidak dilaporkan"

    def label(value: object, fallback: str = "") -> str:
        """Tidy a category cell. `float("nan") or ""` yields "nan", so NaN is
        tested for explicitly rather than relying on truthiness."""
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return fallback
        return tidy_label(value) or fallback

    def province(value: object) -> tuple[str, str]:
        key = str(value or "").strip().lower()
        if not key or key == "nan":
            return UNKNOWN_PROVINCE, ""
        entry = province_by_name.get(key)
        if entry is None:
            raise ValueError(f"Provinsi belum dipetakan: {value!r}")
        return entry["canonical"], entry["bps_code"]

    levels, programmes, departments = zip(*roster["program_studi"].map(programme_parts))
    ktp_names, ktp_codes = zip(*roster["propinsi_ktp"].map(province))
    school_names, _school_codes = zip(*roster["propinsi_sekolah"].map(province))

    gender = roster["jenis_kelamin"].map(
        lambda value: {"L": "Laki-laki", "P": "Perempuan"}.get(str(value or "").strip().upper(), "")
    )
    # "Tidak ada data" and "Lainnya" both mean "not recorded" in the source; they
    # are folded together so the chart has one honest residual category.
    religion = roster["agama"].map(lambda value: label(value, "Tidak dilaporkan"))
    religion = religion.where(
        ~religion.str.lower().isin(["tidak ada data", "lainnya"]), "Tidak dilaporkan"
    )

    clean = pd.DataFrame({
        "angkatan": pd.to_numeric(roster["angkatan"], errors="coerce").astype("Int64"),
        "jenjang": levels,
        "prodi": programmes,
        "departemen": departments,
        "jalur": roster["jalur_masuk"].map(pathway),
        "jalur_raw": roster["jalur_masuk"].fillna("").astype(str).str.strip(),
        "kelas": roster["sub_angkatan"].map(lambda value: label(value, "Tidak tercatat")),
        "gender": gender,
        "agama": religion,
        "provinsi": ktp_names,
        "provinsi_kode": ktp_codes,
        "kabupaten": roster["kabupaten_ktp"].map(label),
        "provinsi_sekolah": school_names,
        "sekolah": roster["sekolah_asal"].map(tidy_school),
        "pekerjaan_wali": roster["pekerjaan_wali"].map(occupation),
        "daerah_3t": roster["asal_3t"].notna(),
        "ipk": pd.to_numeric(roster["ipk"], errors="coerce"),
        "sks": pd.to_numeric(roster["sks_kumulatif"], errors="coerce"),
        "status": roster["status_akhir"].map(
            lambda value: STATUS_GROUPS.get(str(value or "").strip().upper(), "Lainnya")
        ),
    })
    clean["di_jawa"] = clean["provinsi"].isin(JAVA_PROVINCES)
    clean.to_csv(CLEAN_DIR / "students.csv", index=False)


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

    clean_tck()
    clean_partnerships(province_lookup)
    clean_students(province_lookup)
    from student_origins import clean_origins
    clean_origins()
    clean_tracer()
    clean_posbindu()
    clean_posbindu_history()

    # Academic tables arrive already aggregated; they only need to be carried
    # forward so the aggregate stage reads everything from one directory.
    passthrough = (
        "study_programmes", "departments", "laboratories",
        "admissions", "active_students", "graduates", "achievements",
        "scholarships", "accreditation", "exchange",
    )
    for name in passthrough:
        frame = pd.read_csv(LOADED_DIR / f"{name}.csv", low_memory=False)
        for column in ("prodi", "departemen"):
            if column in frame.columns:
                frame[column] = frame[column].map(tidy_label)
        frame.to_csv(CLEAN_DIR / f"{name}.csv", index=False)

    print("Cleaned sources written without person-level identifiers.")


if __name__ == "__main__":
    main()
