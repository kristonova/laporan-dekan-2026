#!/usr/bin/env python3
"""Build browser-ready data without source identifiers or linked personal rows."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import pandas as pd

from utils import (
    CLEAN_DIR,
    LOADED_DIR,
    MAPPINGS_DIR,
    PUBLIC_DATA_DIR,
    SNAPSHOT,
    SNAPSHOT_LABEL,
    SNAPSHOT_LENTERA,
    SNAPSHOT_P2M,
    SNAPSHOT_SCIVAL,
    number,
    records,
    split_pipe,
    write_json,
)


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


# Publisher-side and permanent first, repository copy last, paywalled at the
# end - the order the stacked bars read in.
OPEN_ACCESS_ORDER = ["Gold", "Hybrid gold", "Bronze", "Green", "Tertutup"]

DEPARTMENT_LABELS = {
    "dike": "Ilmu Komputer dan Elektronika",
    "df": "Fisika",
    "dm": "Matematika",
    "dk": "Kimia",
}


def tck_outputs() -> list[dict]:
    tck = pd.read_csv(CLEAN_DIR / "tck_2026_indikator.csv", dtype={"no": "string"})
    numeric_columns = [
        column for column in tck.columns
        if column.startswith(("target_", "capaian_", "rasio_")) or column in DEPARTMENT_LABELS or column == "fakultas"
    ]
    for column in numeric_columns:
        tck[column] = pd.to_numeric(tck[column], errors="coerce")
    joined = records(tck)
    target_columns = ["no", "pilar", "indikator", "satuan", "target_tw1", "target_tw2", "target_tw3", "target_tw4", "tag", "program_renstra", "arah"]
    actual_columns = [
        "no", "capaian_tw1", "capaian_tw2", "capaian_tw3", "capaian_tw3_cacah",
        "kuartal_dinilai", "capaian_dinilai", "target_dinilai", "rasio_kuartal",
        "rasio_thd_target_tahunan", "status_kuartal", "status_thd_tahunan",
        "unit_mismatch", "anomali", "sumber_data",
    ]
    output("tck_2026_joined.json", joined)
    output("tck_2026_targets.json", records(tck[target_columns]))
    output("tck_2026_actuals.json", records(tck[actual_columns]))
    (PUBLIC_DATA_DIR / "tck_2026_indikator.csv").write_text(tck.to_csv(index=False), encoding="utf-8")

    # Departmental split: only the indicators the faculty actually breaks down.
    department_rows: list[dict] = []
    for row in joined:
        values = {key: number(row.get(key)) for key in DEPARTMENT_LABELS}
        if sum(values.values()) <= 0:
            continue
        department_rows.append({
            "no": row["no"],
            "indikator": row["indikator"],
            "pilar": row["pilar"],
            "satuan": row["satuan"],
            "total_departemen": round(sum(values.values()), 4),
            "capaian_fakultas": number(row.get("fakultas")),
            **{label: round(values[key], 4) for key, label in DEPARTMENT_LABELS.items()},
        })
    output("tck_2026_by_dept.json", department_rows)

    budget = json.loads((MAPPINGS_DIR / "tck_2026_anggaran.json").read_text(encoding="utf-8"))
    write_json("tck_2026_anggaran.json", budget)
    return joined


def snapshot_output() -> None:
    """One place the UI reads every "data ditarik per ..." label from."""
    write_json("snapshot.json", {
        "tanggal": SNAPSHOT,
        "label": SNAPSHOT_LABEL,
        "tck": SNAPSHOT_LABEL,
        "p2m": SNAPSHOT_P2M,
        "lentera": SNAPSHOT_LENTERA,
        "scival": SNAPSHOT_SCIVAL,
    })


def partnership_outputs() -> None:
    """Cooperation documents by year, partner, and Indonesian province."""
    partnerships = pd.read_csv(CLEAN_DIR / "partnerships.csv").fillna("")

    by_year = partnerships.groupby(["tahun", "lingkup", "tipe_dokumen"]).size().reset_index(name="n")
    by_year["tahun"] = by_year["tahun"].astype(int)
    output("partnerships_by_year.json", records(by_year.sort_values(["tahun", "lingkup", "tipe_dokumen"])))

    countries = partnerships.groupby(["negara", "lingkup"]).size().reset_index(name="n")
    countries["iso3"] = countries["negara"].map(lambda value: ISO3.get(value, ""))
    kinds = partnerships.groupby("jenis_mitra").size().reset_index(name="n")
    output("partnership_partners.json", {
        "total": int(len(partnerships)),
        "mitra_unik": int(partnerships["negara"].nunique()),
        "negara": records(countries.sort_values(["n", "negara"], ascending=[False, True])),
        "jenis_mitra": records(kinds.sort_values(["n", "jenis_mitra"], ascending=[False, True])),
    })

    points = partnerships[partnerships["location_status"] == "recorded"]
    points = points.groupby(["tahun", "provinsi", "bps_code"]).size().reset_index(name="n")
    points["tahun"] = points["tahun"].astype(int)
    unmapped = partnerships[partnerships["location_status"] != "recorded"]
    output("partnership_points.json", records(points.sort_values(["tahun", "provinsi"])))
    write_json("partnership_coverage.json", {
        "total": int(len(partnerships)),
        "terpetakan": int(len(partnerships) - len(unmapped)),
        "internasional": int((partnerships["lingkup"] == "Internasional").sum()),
        "lokasi_kosong": int((partnerships["location_status"] == "missing").sum()),
    })


def academic_outputs() -> None:
    """Admissions, enrolment, graduation, achievement, and support datasets."""
    admissions = pd.read_csv(CLEAN_DIR / "admissions.csv")
    admissions["tahun"] = admissions["tahun"].astype(int)
    for column in ("peminat", "diterima", "registrasi"):
        admissions[column] = pd.to_numeric(admissions[column], errors="coerce").fillna(0).astype(int)
    admissions["keketatan"] = (admissions["diterima"] / admissions["peminat"].replace(0, pd.NA)).round(4)
    output("admissions_by_year.json", records(admissions.sort_values(["tahun", "departemen", "prodi"])))

    active = pd.read_csv(CLEAN_DIR / "active_students.csv")
    active["angkatan"] = active["angkatan"].astype(int)
    active["mahasiswa"] = pd.to_numeric(active["mahasiswa"], errors="coerce").fillna(0).astype(int)
    output("active_students.json", records(active.sort_values(["prodi", "angkatan"])))

    graduates = pd.read_csv(CLEAN_DIR / "graduates.csv")
    graduates["tahun"] = graduates["tahun"].astype(int)
    graduates["lulusan"] = pd.to_numeric(graduates["lulusan"], errors="coerce").fillna(0).astype(int)
    per_year = graduates.groupby(["jenjang", "tahun", "tahun_ajaran"]).agg(
        lulusan=("lulusan", "sum"),
        total_tercatat=("total_lulusan", "max"),
        ipk_rerata=("ipk_rerata", "max"),
        cumlaude=("cumlaude", "max"),
        lama_studi=("lama_studi", "first"),
    ).reset_index()
    output("graduates_profile.json", records(per_year.sort_values(["jenjang", "tahun"])))
    output("graduates_by_programme.json", records(graduates[["jenjang", "tahun", "prodi", "lulusan"]].sort_values(["jenjang", "tahun", "prodi"])))

    achievements = pd.read_csv(CLEAN_DIR / "achievements.csv")
    achievements["tahun"] = achievements["tahun"].astype(int)
    achievements["prestasi"] = pd.to_numeric(achievements["prestasi"], errors="coerce").fillna(0).astype(int)
    output("student_achievements.json", records(achievements.sort_values(["tahun", "departemen", "tingkat"])))

    scholarships = pd.read_csv(CLEAN_DIR / "scholarships.csv")
    scholarships["penerima"] = pd.to_numeric(scholarships["penerima"], errors="coerce").fillna(0).astype(int)
    by_programme = scholarships.groupby("prodi")["penerima"].sum().reset_index(name="penerima")
    by_scheme = scholarships.groupby("beasiswa")["penerima"].sum().reset_index(name="penerima")
    by_scheme = by_scheme[by_scheme["penerima"] > 0].sort_values(["penerima", "beasiswa"], ascending=[False, True])
    write_json("scholarships.json", {
        "total": int(scholarships["penerima"].sum()),
        "skema": int(len(by_scheme)),
        "per_prodi": records(by_programme.sort_values(["penerima", "prodi"], ascending=[False, True])),
        "per_skema": records(by_scheme.head(15)),
    })

    accreditation = pd.read_csv(CLEAN_DIR / "accreditation.csv").fillna("")
    national = accreditation[accreditation["lingkup"] == "Nasional"]
    unggul = national[national["nilai"].str.strip().isin(["Unggul", "A"])]
    write_json("accreditation.json", {
        "prodi_nasional": int(len(national)),
        "prodi_unggul": int(len(unggul)),
        "prodi_internasional": int((accreditation["lingkup"] == "Internasional").sum()),
        "per_lembaga": records(national.groupby("lembaga").size().reset_index(name="n").sort_values(["n", "lembaga"], ascending=[False, True])),
        "internasional_per_jenjang": records(
            accreditation[accreditation["lingkup"] == "Internasional"].groupby("jenjang_grup").size().reset_index(name="n")
        ),
        "daftar": records(accreditation[["lingkup", "jenjang_grup", "departemen", "prodi", "lembaga", "periode", "nilai"]]),
    })

    exchange = pd.read_csv(CLEAN_DIR / "exchange.csv").fillna("")
    by_country = exchange.groupby("negara").size().reset_index(name="n").sort_values(["n", "negara"], ascending=[False, True])
    write_json("exchange_students.json", {
        "total": int(len(exchange)),
        "negara": int(exchange["negara"].nunique()),
        "universitas": int(exchange["universitas"].nunique()),
        "per_negara": records(by_country),
    })


# --- Profil mahasiswa --------------------------------------------------------

# Counts of one or two people are withheld. A single student in one province of
# one cohort of one programme is identifiable to anyone who knows them, and this
# site is public. The row still ships, so a reader can see the category exists —
# only the number is replaced by null and the row marked.
SMALL_CELL = 3


def suppress(frame: pd.DataFrame, column: str = "n") -> pd.DataFrame:
    """Null out counts below SMALL_CELL and flag the rows that were withheld."""
    result = frame.copy()
    withheld = result[column].between(1, SMALL_CELL - 1)
    result["disamarkan"] = withheld
    result[column] = result[column].where(~withheld).astype("Int64")
    return result


def gendered_counts(frame: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    """Group by keys and add the gender split alongside the total."""
    grouped = frame.groupby(keys, dropna=False).agg(
        n=("angkatan", "size"),
        perempuan=("gender", lambda values: int((values == "Perempuan").sum())),
        laki=("gender", lambda values: int((values == "Laki-laki").sum())),
    ).reset_index()
    # Gender is blank for the 2021-2022 non-degree intake, so the two named
    # counts do not always add up to n. The gap is reported, never imputed.
    grouped["tanpa_gender"] = grouped["n"] - grouped["perempuan"] - grouped["laki"]
    return grouped


def staffing_outputs() -> None:
    """Professor tenure, the vacant-position ratio, and certification coverage.

    All three read the SIMASTER extract of 3 September 2026 and are reported per
    department, because the faculty-level figures hide the only department that
    breaches the ceiling.
    """
    professors = pd.read_csv(CLEAN_DIR / "professors.csv")
    by_period = professors.groupby(["periode", "department"]).size().reset_index(name="n")
    by_year = professors.groupby("year").size().reset_index(name="n")
    by_year_dept = professors.groupby(["year", "department"]).size().reset_index(name="n")
    within = professors[professors["periode"] == "Periode 2021-2026"]
    write_json("professor_tenure.json", {
        "total": int(len(professors)),
        "periode_ini": int(len(within)),
        "sebelumnya": int(len(professors) - len(within)),
        "tahun_awal": int(within["year"].min()),
        "tahun_akhir": int(within["year"].max()),
        "per_periode": records(by_period.sort_values(["periode", "department"])),
        "per_tahun": records(by_year.sort_values("year")),
        "per_tahun_departemen": records(by_year_dept.sort_values(["year", "department"])),
    })

    # The source workbook states the ceiling in its own closing note: a
    # department may not leave more than 10% of its lecturers without an
    # academic position.
    ceiling = 10.0
    lecturers = pd.read_csv(CLEAN_DIR / "lecturers.csv")
    certification = pd.read_csv(CLEAN_DIR / "lecturer_certification.csv")
    totals = lecturers.groupby("department").size()
    teaching = lecturers[lecturers["position"] == "Tenaga Pengajar"].groupby("department").size()
    certified = certification[certification["certified"]].groupby("department").size()
    certified_totals = certification.groupby("department").size()

    rows = []
    for department in sorted(totals.index):
        total = int(totals[department])
        without = int(teaching.get(department, 0))
        has_cert = int(certified.get(department, 0))
        cert_total = int(certified_totals.get(department, 0))
        rows.append({
            "department": department,
            "dosen": total,
            "tanpa_jabatan": without,
            "rasio": round(without / total * 100, 2),
            "ambang": ceiling,
            "melampaui_ambang": bool(without / total * 100 > ceiling),
            "tersertifikasi": has_cert,
            "tersertifikasi_dari": cert_total,
            "rasio_sertifikasi": round(has_cert / cert_total * 100, 2) if cert_total else None,
        })
    faculty_without = int((lecturers["position"] == "Tenaga Pengajar").sum())
    faculty_certified = int(certification["certified"].sum())
    write_json("lecturer_ratio.json", {
        "ambang": ceiling,
        "dosen": int(len(lecturers)),
        "tanpa_jabatan": faculty_without,
        "rasio": round(faculty_without / len(lecturers) * 100, 2),
        "tersertifikasi": faculty_certified,
        "rasio_sertifikasi": round(faculty_certified / len(certification) * 100, 2),
        "per_departemen": rows,
    })
    output("lecturer_ratio_by_dept.json", rows)


def partnership_revenue_outputs() -> None:
    """Cooperation contract value and the development fee it returns to FMIPA.

    Kept deliberately separate from funding_by_year.json: that series counts
    research grants recorded in P2M, this one counts billed cooperation
    contracts. They are close in magnitude and must never be added together.
    """
    # Billing numbers are identifiers, not quantities: read as text so the
    # 16-digit ones do not come back as floats.
    revenue = pd.read_csv(CLEAN_DIR / "partnership_revenue.csv", dtype={"billing": "string"})
    per_year = revenue.groupby("tahun").agg(
        nominal=("nominal_kontrak", "sum"), dpi=("dpi", "sum"), n=("nominal_kontrak", "size")
    ).reset_index()
    per_year["rasio_dpi"] = (per_year["dpi"] / per_year["nominal"] * 100).round(2)
    # 2026 is the running year: the workbook was compiled in September.
    per_year["is_partial"] = per_year["tahun"].eq(2026)
    output("partnership_revenue_by_year.json", records(per_year.sort_values("tahun")))

    per_department = revenue.groupby("departemen").agg(
        nominal=("nominal_kontrak", "sum"), dpi=("dpi", "sum"), n=("nominal_kontrak", "size")
    ).reset_index()
    total = float(revenue["nominal_kontrak"].sum())
    per_department["porsi"] = (per_department["nominal"] / total * 100).round(2)
    per_department = per_department.sort_values(["nominal", "departemen"], ascending=[False, True])
    output("partnership_revenue_by_dept.json", records(per_department))

    unassigned = revenue[revenue["departemen"] == "Tidak berdepartemen"]
    billing = revenue[revenue["billing"].astype(str).str.strip().ne("")]
    duplicates = billing.groupby(["tahun", "billing"]).size().reset_index(name="n")
    write_json("partnership_revenue.json", {
        "kontrak": int(len(revenue)),
        "nominal": total,
        "dpi": float(revenue["dpi"].sum()),
        "rasio_dpi": round(revenue["dpi"].sum() / total * 100, 2),
        "tahun_awal": int(revenue["tahun"].min()),
        "tahun_akhir": int(revenue["tahun"].max()),
        "tanpa_departemen": {
            "kontrak": int(len(unassigned)),
            "nominal": float(unassigned["nominal_kontrak"].sum()),
            "porsi": round(unassigned["nominal_kontrak"].sum() / total * 100, 2),
        },
        "billing_ganda": records(duplicates[duplicates["n"] > 1]),
        "per_tahun": records(per_year.sort_values("tahun")),
        "per_departemen": records(per_department),
    })


def school_mou_outputs() -> None:
    """Schools that signed a memorandum in July 2026, against the feeder network.

    The three sheets are three signing days that overlap heavily, so the union
    is what counts, not the row total. Matching against the schools students
    actually come from is approximate: both sources type the name freely, and
    pipeline/mappings/sekolah_mou_alias.csv records every normalisation applied
    so the estimate can be audited rather than taken on trust.
    """
    mou = pd.read_csv(CLEAN_DIR / "school_mou.csv")
    schools = mou.drop_duplicates(subset=["kunci"])
    origins = pd.read_csv(CLEAN_DIR / "student_origin_schools.csv")
    feeders = set(origins["kunci"])

    matched = schools[schools["kunci"].isin(feeders)]
    per_session = mou.groupby("sesi").size().reset_index(name="n")
    write_json("school_mou.json", {
        "sekolah": int(len(schools)),
        "baris": int(len(mou)),
        "sesi": records(per_session),
        "sudah_menjadi_asal": int(len(matched)),
        "jejaring_baru": int(len(schools) - len(matched)),
        "sekolah_asal_tercatat": int(len(feeders)),
    })
    output("school_mou_status.json", [
        {"status": "Sudah menjadi sekolah asal", "n": int(len(matched))},
        {"status": "Jejaring baru", "n": int(len(schools) - len(matched))},
    ])



def student_profile_outputs() -> None:
    """Cohort demographics: origin, gender, pathway, family background, outcome."""
    students = pd.read_csv(CLEAN_DIR / "students.csv", keep_default_na=False, na_values=[""])
    students["angkatan"] = students["angkatan"].astype(int)
    degree = students[students["jenjang"] == "Sarjana"]
    years = sorted(students["angkatan"].unique().tolist())

    # Only the 38 BPS provinces carry a numeric code. "Luar Negeri" and the rows
    # with no province at all are excluded from the Java / outside-Java split and
    # counted separately, so a missing address never reads as "from outside Java".
    students["provinsi_domestik"] = students["provinsi_kode"].fillna("").str.fullmatch(r"\d+")

    # --- per cohort headline ------------------------------------------------
    per_year = students.groupby("angkatan").agg(
        total=("angkatan", "size"),
        perempuan=("gender", lambda values: int((values == "Perempuan").sum())),
        laki=("gender", lambda values: int((values == "Laki-laki").sum())),
        di_jawa=("di_jawa", "sum"),
        daerah_3t=("daerah_3t", "sum"),
        domestik=("provinsi_domestik", "sum"),
        luar_negeri=("provinsi", lambda values: int((values == "Luar Negeri").sum())),
    ).reset_index()
    domestic = students[students["provinsi_domestik"]]
    per_year["provinsi_terwakili"] = (
        domestic.groupby("angkatan")["provinsi_kode"].nunique()
        .reindex(per_year["angkatan"]).fillna(0).astype(int).values
    )
    per_year["sarjana"] = degree.groupby("angkatan").size().reindex(per_year["angkatan"]).fillna(0).astype(int).values
    per_year["non_gelar"] = per_year["total"] - per_year["sarjana"]
    per_year["iup"] = students[students["jalur"] == "IUP"].groupby("angkatan").size().reindex(per_year["angkatan"]).fillna(0).astype(int).values
    per_year["tergender"] = per_year["perempuan"] + per_year["laki"]
    per_year["porsi_perempuan"] = (per_year["perempuan"] / per_year["tergender"] * 100).round(1)
    per_year["luar_jawa"] = per_year["domestik"] - per_year["di_jawa"]
    per_year["tanpa_provinsi"] = per_year["total"] - per_year["domestik"] - per_year["luar_negeri"]
    per_year["porsi_luar_jawa"] = (per_year["luar_jawa"] / per_year["domestik"] * 100).round(1)
    for column in ("di_jawa", "luar_jawa", "daerah_3t", "domestik", "tanpa_provinsi"):
        per_year[column] = per_year[column].astype(int)

    first, last = per_year.iloc[0], per_year.iloc[-1]
    top_pathway = students["jalur"].value_counts().idxmax()
    write_json("students_summary.json", {
        "total": int(len(students)),
        "sarjana": int(len(degree)),
        "tahun": years,
        "tahun_awal": int(years[0]),
        "tahun_akhir": int(years[-1]),
        "prodi_n": int(degree["prodi"].nunique()),
        "jalur_terbesar": top_pathway,
        "jalur_terbesar_n": int((students["jalur"] == top_pathway).sum()),
        "porsi_perempuan_awal": float(first["porsi_perempuan"]),
        "porsi_perempuan_akhir": float(last["porsi_perempuan"]),
        "provinsi_awal": int(first["provinsi_terwakili"]),
        "provinsi_akhir": int(last["provinsi_terwakili"]),
        "porsi_luar_jawa_awal": float(first["porsi_luar_jawa"]),
        "porsi_luar_jawa_akhir": float(last["porsi_luar_jawa"]),
        "porsi_luar_jawa_puncak": float(per_year["porsi_luar_jawa"].max()),
        "tahun_luar_jawa_puncak": int(per_year.loc[per_year["porsi_luar_jawa"].idxmax(), "angkatan"]),
        "daerah_3t": int(per_year["daerah_3t"].sum()),
        "per_tahun": records(per_year),
    })

    # --- programme ----------------------------------------------------------
    by_programme = gendered_counts(students, ["angkatan", "jenjang", "departemen", "prodi"])
    output("students_by_programme.json", records(
        suppress(by_programme).sort_values(["angkatan", "jenjang", "departemen", "prodi"])
    ))

    # --- province -----------------------------------------------------------
    # The placeholder code is filled before grouping, not after: rows with a
    # missing address and rows the source marked "Lain-lain" carry the same
    # label and must land in one row, not two identical-looking ones.
    students["provinsi_kode"] = students["provinsi_kode"].fillna("UNKNOWN")
    by_province = students.groupby(["angkatan", "provinsi", "provinsi_kode"], dropna=False).size().reset_index(name="n")
    output("students_by_province.json", records(
        suppress(by_province).sort_values(["angkatan", "provinsi"])
    ))

    # Six-year totals are suppressed on their own count, not summed from the
    # per-cohort rows: adding up published cells would silently drop every
    # cohort cell that was withheld and understate the province.
    province_total = students.groupby(["provinsi", "provinsi_kode"], dropna=False).size().reset_index(name="n")
    province_total = suppress(province_total).sort_values(["n", "provinsi"], ascending=[False, True])

    # --- pathway ------------------------------------------------------------
    by_pathway = students.groupby(["angkatan", "jalur"]).size().reset_index(name="n")
    output("students_by_pathway.json", records(suppress(by_pathway).sort_values(["angkatan", "jalur"])))

    # --- family, faith, and school background -------------------------------
    occupation = students.groupby(["angkatan", "pekerjaan_wali"]).size().reset_index(name="n")
    religion = students.groupby(["angkatan", "agama"]).size().reset_index(name="n")
    # School of origin was not recorded at all for the 2021 and 2022 cohorts.
    with_school = students[students["sekolah"].notna() & (students["angkatan"] >= 2023)]
    schools = with_school.groupby("sekolah").size().reset_index(name="n")
    schools = schools[schools["n"] >= SMALL_CELL].sort_values(["n", "sekolah"], ascending=[False, True])
    school_province = with_school.groupby(["angkatan", "provinsi_sekolah"]).size().reset_index(name="n")
    school_years = sorted(with_school["angkatan"].unique().tolist())
    diy_share = 0.0
    if len(with_school):
        diy_share = with_school["provinsi_sekolah"].eq("Daerah Istimewa Yogyakarta").sum() / len(with_school) * 100
    write_json("students_background.json", {
        "pekerjaan_wali": records(suppress(occupation).sort_values(["angkatan", "pekerjaan_wali"])),
        "pekerjaan_wali_total": records(
            suppress(students.groupby("pekerjaan_wali").size().reset_index(name="n"))
            .sort_values(["n", "pekerjaan_wali"], ascending=[False, True])
        ),
        "agama": records(suppress(religion).sort_values(["angkatan", "agama"])),
        "sekolah_tahun": school_years,
        "sekolah_tercatat": int(len(with_school)),
        "sekolah_unik": int(with_school["sekolah"].nunique()),
        "sekolah_teratas": records(schools.head(15)),
        "sekolah_porsi_diy": round(float(diy_share), 1),
        "sekolah_provinsi": records(suppress(school_province).sort_values(["angkatan", "provinsi_sekolah"])),
        "wali_tidak_dilaporkan": int((students["pekerjaan_wali"] == "Tidak dilaporkan").sum()),
    })

    # --- cohort outcome and grades ------------------------------------------
    outcome = students.groupby(["angkatan", "status"]).size().reset_index(name="n")
    output("students_cohort_outcome.json", records(suppress(outcome).sort_values(["angkatan", "status"])))

    graded = degree[degree["ipk"].between(0, 4)].copy()
    ipk_year = graded.groupby("angkatan")["ipk"].agg(
        tercatat="size", rerata="mean", median="median",
        p25=lambda values: values.quantile(0.25), p75=lambda values: values.quantile(0.75),
    ).reset_index()
    def distribution(values):
        q1, q3 = values.quantile(0.25), values.quantile(0.75)
        iqr = q3 - q1
        within = values[values.between(q1 - 1.5 * iqr, q3 + 1.5 * iqr)]
        return {"tercatat": int(len(values)), "median": round(float(values.median()), 2),
                "p25": round(float(q1), 2), "p75": round(float(q3), 2),
                "bawah": round(float(within.min()), 2), "atas": round(float(within.max()), 2)}

    ipk_programme = pd.DataFrame([
        {"angkatan": int(year), "prodi": programme, **distribution(group["ipk"])}
        for (year, programme), group in graded.groupby(["angkatan", "prodi"])
    ])
    # A median over one or two students is as identifying as the values it hides.
    ipk_programme = ipk_programme[ipk_programme["tercatat"] >= SMALL_CELL]
    for frame, columns in ((ipk_year, ["rerata", "median", "p25", "p75"]), (ipk_programme, ["median"])):
        for column in columns:
            frame[column] = frame[column].round(2)
    write_json("students_ipk.json", {
        "metode": "Beeswarm: satu titik per IPK tercatat, warna menurut angkatan. Posisi horizontal menunjukkan IPK asli 0–4; posisi vertikal hanya menghindari tumpang tindih. Nilai diurutkan dalam prodi/angkatan tanpa identitas atau kaitan dengan atribut pribadi lain. Median gabungan dihitung dari seluruh pengamatan.",
        "tahun": sorted(graded["angkatan"].unique().tolist()),
        "tahun_tanpa_ipk": [year for year in years if year not in set(graded["angkatan"])],
        "per_tahun": records(ipk_year),
        "per_prodi": records(ipk_programme.sort_values(["angkatan", "prodi"])),
        "gabungan": [{"angkatan": 0, "prodi": programme, **distribution(group["ipk"])}
                     for programme, group in graded.groupby("prodi") if len(group) >= SMALL_CELL],
        # Only the grades needed by the beeswarm leave the local roster. Sorting
        # removes source row order; no identifiers or other student attributes travel.
        "sebaran": [{"angkatan": int(year), "prodi": programme,
                     "nilai": sorted(float(value) for value in group["ipk"])}
                    for (year, programme), group in graded.groupby(["angkatan", "prodi"])
                    if len(group) >= SMALL_CELL],
    })
    output("students_ipk_distribution.json", records(ipk_programme.sort_values(["angkatan", "prodi"])))

    # --- access -------------------------------------------------------------
    districts = students.groupby("kabupaten").size().reset_index(name="n")
    districts = districts[districts["n"] >= SMALL_CELL].sort_values(["n", "kabupaten"], ascending=[False, True])
    write_json("students_access.json", {
        "provinsi_total": records(province_total),
        "per_tahun": records(per_year[[
            "angkatan", "total", "domestik", "di_jawa", "luar_jawa", "porsi_luar_jawa",
            "provinsi_terwakili", "daerah_3t", "luar_negeri", "tanpa_provinsi",
        ]]),
        "kabupaten_teratas": records(districts.head(15)),
        "kabupaten_unik": int(students["kabupaten"].nunique()),
        "provinsi_tanpa_data": int((students["provinsi"] == "Tidak teridentifikasi").sum()),
        "luar_negeri": int((students["provinsi"] == "Luar Negeri").sum()),
        "daerah_3t_total": int(students["daerah_3t"].sum()),
    })


def tracer_outputs() -> None:
    """Graduate waiting time and employment sector, aggregated per programme."""
    waiting = pd.read_csv(CLEAN_DIR / "tracer_waiting.csv")
    buckets = waiting.groupby(["prodi", "kategori"]).size().reset_index(name="n")
    output("tracer_waiting_time.json", records(buckets.sort_values(["prodi", "kategori"])))
    write_json("tracer_summary.json", {
        "responden": int(len(waiting)),
        "tahun": sorted(int(year) for year in waiting["tahun"].unique()),
        "median_bulan": float(waiting["bulan"].median()),
        "rerata_bulan": round(float(waiting["bulan"].mean()), 4),
        "bekerja_sebelum_lulus": int((waiting["bulan"] <= 0).sum()),
        "dalam_6_bulan": int((waiting["bulan"] <= 6).sum()),
    })

    sectors = pd.read_csv(CLEAN_DIR / "tracer_sectors.csv")
    by_sector = sectors.groupby("sektor").size().reset_index(name="n").sort_values(["n", "sektor"], ascending=[False, True])
    output("tracer_sectors.json", records(by_sector))


# The six screening measures, in the order the report names them.
HEALTH_MEASURES = {
    "imt": "Indeks Massa Tubuh",
    "lingkar_perut": "Lingkar Perut",
    "tekanan_darah": "Tekanan Darah",
    "asam_urat": "Asam Urat",
    "kolesterol": "Kolesterol",
    "gula_darah": "Gula Darah",
}
HEALTH_STAFF = ["Dosen", "Tendik"]
HEALTH_BANDS = ["Normal", "Waspada", "Berisiko", "Tidak diperiksa"]


def health_outputs() -> None:
    """Posbindu screening results for teaching and support staff.

    The report is about the staff the faculty is responsible for, so students
    and uncategorised rows are filtered out here rather than in the page. What
    is excluded is counted and published alongside, so the universe is legible.
    """
    visits = pd.read_csv(CLEAN_DIR / "posbindu_visits.csv").fillna("")
    participants = pd.read_csv(CLEAN_DIR / "posbindu_participants.csv").fillna("")

    staff = visits[visits["kriteria"].isin(HEALTH_STAFF)]
    excluded = (
        visits[~visits["kriteria"].isin(HEALTH_STAFF)]
        .groupby("kriteria").size().sort_values(ascending=False)
    )

    sessions = []
    for date, group in staff.groupby("tanggal"):
        sessions.append({
            "tanggal": date,
            "peserta": int(len(group)),
            # Named "distribusi_" so the privacy guard can tell a category count
            # from a per-person measurement, which must never be exported.
            **{f"distribusi_{column}": dict(Counter(group[column])) for column in HEALTH_MEASURES},
            "dirujuk": int(group["dirujuk"].astype(str).str.lower().eq("true").sum()),
        })
    sessions.sort(key=lambda row: row["tanggal"])

    # One row per measure, ordered so the most pressing sits at the top of the
    # chart. "Tidak diperiksa" is excluded from the share: a measure nobody was
    # screened for is not a measure everybody passed.
    profile = []
    for column, label in HEALTH_MEASURES.items():
        counts = Counter(staff[f"risiko_{column}"])
        screened = sum(counts[band] for band in HEALTH_BANDS if band != "Tidak diperiksa")
        # The chart folds clinical categories into three bands; the source
        # categories travel with it so the table can show what was folded.
        categories = (
            staff.groupby([column, f"risiko_{column}"]).size()
            .reset_index(name="n").sort_values("n", ascending=False)
        )
        profile.append({
            "indikator": label,
            "kunci": column,
            "total": int(len(staff)),
            "diperiksa": int(screened),
            "pita": {band: int(counts.get(band, 0)) for band in HEALTH_BANDS},
            "porsi_berisiko": round(counts.get("Berisiko", 0) / screened, 4) if screened else 0.0,
            "kategori": [
                {"nilai": str(row[column]), "pita": str(row[f"risiko_{column}"]), "n": int(row["n"])}
                for _, row in categories.iterrows()
            ],
        })
    profile.sort(key=lambda row: row["porsi_berisiko"], reverse=True)

    # Same reason as the yearly file: the scene footer offers a CSV, so one is
    # written for the risk profile the chart actually draws.
    pd.DataFrame([
        {
            "indikator": row["indikator"],
            "kategori_sumber": category["nilai"],
            "pita": category["pita"],
            "kunjungan": category["n"],
            "diperiksa": row["diperiksa"],
            "porsi_berisiko": row["porsi_berisiko"],
        }
        for row in profile
        for category in row["kategori"]
    ]).to_csv(PUBLIC_DATA_DIR / "hpu_posbindu.csv", index=False)

    write_json("hpu_posbindu.json", {
        "universe": "Dosen dan tenaga kependidikan",
        "kunjungan": int(len(staff)),
        "sesi": sessions,
        "profil_risiko": profile,
        "kunjungan_per_kriteria": records(
            staff.groupby("kriteria").size().reset_index(name="n").sort_values(["n", "kriteria"], ascending=[False, True])
        ),
        "peserta_terdaftar": int(len(participants)),
        "komposisi_peserta": records(
            participants.groupby("kriteria").size().reset_index(name="n").sort_values(["n", "kriteria"], ascending=[False, True])
        ),
        "dikecualikan": {str(kriteria): int(n) for kriteria, n in excluded.items()},
        "catatan": "Agregat anonim. Nama, tanggal lahir, dan nilai pemeriksaan per orang tidak diekspor.",
    })


HEALTH_YEARS = ["2022", "2023", "2024", "2025", "2026"]

# Two reading layers, decided with the data owner: the headline stays the staff
# the faculty is responsible for, and the whole cohort travels beside it so the
# reach of the programme is legible rather than hidden by the filter.
HEALTH_LAYERS = {
    "staf": ("Dosen dan tenaga kependidikan", HEALTH_STAFF),
    "semua": ("Seluruh peserta", None),
}

# What each year can and cannot say, carried with the numbers so no chart has to
# imply a precision its source never had.
HEALTH_PROVENANCE = {
    "2022": ("Digitasi arsip analog + registri", "sesi dan bulan"),
    "2023": ("Digitasi arsip analog + registri", "sesi dan bulan"),
    "2024": ("Digitasi arsip analog + registri", "sesi dan bulan"),
    "2025": ("Registri Posbindu", "bulan"),
    "2026": ("Rekap Posbindu 2026", "sesi"),
}


def health_longitudinal_outputs() -> None:
    """Posbindu screening across 2022-2026, on one comparable set of categories.

    The 2022-2025 sources recorded measurements and the 2026 source recorded
    both measurements and interpretations, so the older years are re-derived in
    01_clean.py using thresholds read back off 2026 itself. What arrives here is
    already banded; this function only counts.

    Waist circumference and uric acid carry a second denominator. Their cut-off
    depends on sex, which the digitisation sheet never recorded, so a visit
    without a known sex is measured but not assessed. Both numbers are published
    rather than the smaller one being passed off as the whole.
    """
    history = pd.read_csv(CLEAN_DIR / "posbindu_history.csv", dtype={"tahun": "string"}).fillna("")
    current = pd.read_csv(CLEAN_DIR / "posbindu_visits.csv").fillna("")

    # 2026 arrives keyed by session date and already sex-complete, so every
    # measured indicator is also an assessed one.
    current["tahun"] = current["tanggal"].astype(str).str[:4]
    current["bulan"] = current["tanggal"].astype(str).str[:7]
    for measure in HEALTH_MEASURES:
        current[f"terukur_{measure}"] = current[f"risiko_{measure}"].ne("Tidak diperiksa")
    current["jumlah_berisiko"] = sum(
        current[f"risiko_{measure}"].eq("Berisiko").astype(int) for measure in HEALTH_MEASURES
    )
    current["jumlah_diperiksa"] = sum(
        current[f"risiko_{measure}"].ne("Tidak diperiksa").astype(int) for measure in HEALTH_MEASURES
    )

    shared = (
        ["tahun", "bulan", "kriteria", "jumlah_berisiko", "jumlah_diperiksa"]
        + [column for measure in HEALTH_MEASURES for column in (measure, f"risiko_{measure}", f"terukur_{measure}")]
    )
    dated = history[history["tahun"] != ""]
    combined = pd.concat([dated[shared], current[shared]], ignore_index=True)

    def layer_rows(scope: list[str] | None) -> pd.DataFrame:
        return combined if scope is None else combined[combined["kriteria"].isin(scope)]

    layers = []
    for key, (label, scope) in HEALTH_LAYERS.items():
        rows = layer_rows(scope)
        indicators = []
        for measure, measure_label in HEALTH_MEASURES.items():
            series = []
            for year in HEALTH_YEARS:
                yearly = rows[rows["tahun"] == year]
                counts = Counter(yearly[f"risiko_{measure}"])
                assessed = sum(count for band, count in counts.items() if band != "Tidak diperiksa")
                series.append({
                    "tahun": int(year),
                    "kunjungan": int(len(yearly)),
                    # Had a reading at all.
                    "terukur": int(yearly[f"terukur_{measure}"].astype(bool).sum()),
                    # Had a reading that could be placed in a band.
                    "dinilai": int(assessed),
                    "pita": {band: int(counts.get(band, 0)) for band in HEALTH_BANDS},
                    "porsi_berisiko": round(counts.get("Berisiko", 0) / assessed, 4) if assessed else None,
                })
            indicators.append({
                "kunci": measure,
                "indikator": measure_label,
                "berbasis_gender": measure in {"lingkar_perut", "asam_urat"},
                "seri": series,
            })
        # Ordered by the most recent year with a reading, so the chart opens on
        # what matters now rather than on what happened in 2022.
        indicators.sort(key=lambda row: row["seri"][-1]["porsi_berisiko"] or 0, reverse=True)
        layers.append({
            "kunci": key,
            "label": label,
            "kunjungan": int(len(rows)),
            "indikator": indicators,
            "partisipasi": [
                {
                    "tahun": int(year),
                    "kunjungan": int((rows["tahun"] == year).sum()),
                    "bulan_layanan": int(rows.loc[rows["tahun"] == year, "bulan"].nunique()),
                }
                for year in HEALTH_YEARS
            ],
            "multirisiko": [
                {"jumlah_indikator": int(count), "kunjungan": int(total)}
                for count, total in sorted(Counter(
                    rows.loc[rows["jumlah_diperiksa"] == len(HEALTH_MEASURES), "jumlah_berisiko"]
                ).items())
            ],
            "diperiksa_lengkap": int((rows["jumlah_diperiksa"] == len(HEALTH_MEASURES)).sum()),
        })

    # Repeat attendance, from the registry panel: one row per person, up to five
    # examinations each. It is the only source shaped to answer this at all.
    panel = history[history["urutan_kunjungan"] != ""].copy()
    panel["urutan_kunjungan"] = pd.to_numeric(panel["urutan_kunjungan"], errors="coerce")
    reach = panel.groupby("peserta_ref")["urutan_kunjungan"].max()
    retention = [
        {"kunjungan_ke": step, "orang": int((reach >= step).sum())}
        for step in range(1, int(reach.max()) + 1)
    ]

    quality = [
        {
            "tahun": int(year),
            **{
                label: int(((dated["tahun"] == year) & (dated["kualitas"] == label)).sum())
                for label in ("Jelas", "Perlu verifikasi", "Tidak dicatat")
            },
        }
        for year in HEALTH_YEARS[:-1]
    ]

    # output() mirrors a CSV only for list payloads, and this one is an object,
    # so the tidy download is written explicitly. Without it the chart footer
    # would offer "Unduh CSV" and hand the reader JSON.
    pd.DataFrame([
        {
            "tahun": point["tahun"],
            "lapisan": layer["label"],
            "indikator": measure["indikator"],
            "kunjungan": point["kunjungan"],
            "terukur": point["terukur"],
            "dinilai": point["dinilai"],
            **{f"pita_{band.lower().replace(' ', '_')}": count for band, count in point["pita"].items()},
            "porsi_berisiko": point["porsi_berisiko"],
        }
        for layer in layers
        for measure in layer["indikator"]
        for point in measure["seri"]
    ]).to_csv(PUBLIC_DATA_DIR / "hpu_posbindu_tahunan.csv", index=False)

    output("hpu_posbindu_tahunan.json", {
        "periode": "2022–2026",
        "tahun": [int(year) for year in HEALTH_YEARS],
        "sumber_per_tahun": [
            {
                "tahun": int(year),
                "sumber": HEALTH_PROVENANCE[year][0],
                "presisi": HEALTH_PROVENANCE[year][1],
                "bulan_layanan": int(combined.loc[combined["tahun"] == year, "bulan"].nunique()),
                "kunjungan": int((combined["tahun"] == year).sum()),
            }
            for year in HEALTH_YEARS
        ],
        "lapisan": layers,
        "kualitas": quality,
        "retensi": retention,
        "tanpa_tahun": int((history["tahun"] == "").sum()),
        "komposisi_kriteria": records(
            combined.groupby(["tahun", "kriteria"]).size().reset_index(name="n").sort_values(["tahun", "n"], ascending=[True, False])
        ),
        "catatan": (
            "Agregat anonim. Kategori 2022–2025 dihitung ulang dari nilai mentah memakai ambang "
            "yang dibaca balik dari sumber 2026 (pipeline/mappings/posbindu_ambang.csv). Lingkar "
            "perut dan asam urat memakai ambang berbeda per jenis kelamin, sehingga kunjungan "
            "tanpa data gender terukur tetapi tidak dinilai."
        ),
    })


def main() -> None:
    snapshot_output()
    tck_outputs()
    partnership_outputs()
    academic_outputs()
    staffing_outputs()
    partnership_revenue_outputs()
    school_mou_outputs()
    student_profile_outputs()
    from student_origins import aggregate_origins
    aggregate_origins(output, suppress)
    from student_programme_trends import aggregate_programme_trends
    aggregate_programme_trends(output, suppress)
    tracer_outputs()
    health_outputs()
    health_longitudinal_outputs()

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
        count=("eid", "size"),
        mapping=("mapping", lambda values: ",".join(sorted(set(values.dropna().astype(str))))),
    ).reset_index()
    publication_group["year"] = publication_group["year"].astype(int)
    # 2025 is complete in the 30 August 2026 SciVal snapshot; 2026 is the year
    # still being indexed. The citation series above keeps 2025 as its running
    # year because it comes from the P2M export, which stops there.
    publication_group["is_partial"] = publication_group["year"].eq(2026)
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
        # Prominence is a property of the cluster, not of any one paper, so every
        # row in a cluster repeats it; the median absorbs the few rows SciVal
        # left blank without shifting the value.
        prominence = group["topic_cluster_prominence"].dropna()
        topic_rows.append({
            "cluster": str(cluster), "topic": top_topic, "dept": dominant, "n": int(len(group)), "sample": samples,
            "prominence": None if prominence.empty else round(float(prominence.median()), 1),
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
        # Sorted by count then name so ties keep a stable order between runs.
        for country, total in sorted(country_totals.items(), key=lambda item: (-item[1], item[0]))
    ]
    output("collab_countries.json", country_rows)

    # The share of output written with at least one partner abroad. The story
    # used to state this as two numbers typed into the component; it is computed
    # here so a refreshed export moves the sentence with the chart.
    collab_share_rows: list[dict] = []
    for year, group in publications.dropna(subset=["year"]).groupby("year"):
        partners = group["country_region"].map(lambda value: [name for name in split_pipe(value) if name != "Indonesia"])
        recorded = group["country_region"].notna().sum()
        international = int(partners.map(bool).sum())
        collab_share_rows.append({
            "year": int(year),
            "total": int(len(group)),
            "recorded": int(recorded),
            "international": international,
            "share": round(100 * international / len(group), 1) if len(group) else 0.0,
            "is_partial": int(year) == 2026,
        })
    output("collab_share.json", sorted(collab_share_rows, key=lambda row: row["year"]))

    # One open access route per publication per year; see open_access_route() in
    # 01_clean.py for how a multi-label record is reduced to a single route.
    open_access_rows: list[dict] = []
    for (year, route), size in publications.dropna(subset=["year"]).groupby(["year", "open_access"]).size().items():
        open_access_rows.append({"year": int(year), "route": str(route), "n": int(size), "is_partial": int(year) == 2026})
    open_access_rows.sort(key=lambda row: (row["year"], OPEN_ACCESS_ORDER.index(row["route"])))
    output("open_access.json", open_access_rows)

    # Subject-area totals come from SciVal's own report rather than from the
    # publication rows: two thirds of publications carry several ASJC fields, so
    # these outputs deliberately sum past the 3,069 publications, and only SciVal
    # can deduplicate the researcher counts behind them.
    subject_areas = pd.read_csv(CLEAN_DIR / "scival_subject_areas.csv")
    subject_areas = subject_areas.sort_values(["output", "subject_area"], ascending=[False, True])
    output("research_quality.json", records(subject_areas))

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
    output("sinta_by_dept.json", records(sinta_group.sort_values(["total", "department"], ascending=[False, True])))

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
    certification = pd.read_csv(CLEAN_DIR / "lecturer_certification.csv")
    p2m_staff = pd.read_csv(LOADED_DIR / "academic_staff.csv", low_memory=False)
    departments = pd.read_csv(CLEAN_DIR / "departments.csv")
    laboratories = pd.read_csv(CLEAN_DIR / "laboratories.csv")
    # The accreditation workbook, not the P2M study_programme export, is the
    # authority for how many programmes the faculty runs: the export is missing
    # Magister Elektronika dan Instrumentasi and so counts 17 against its 18.
    accreditation = pd.read_csv(CLEAN_DIR / "accreditation.csv").fillna("")
    national = accreditation[accreditation["lingkup"] == "Nasional"]
    levels = {"S1 ": "Sarjana", "Magister ": "Magister", "Doktor ": "Doktor"}
    by_level = {label: 0 for label in levels.values()}
    for prodi in national["prodi"]:
        for prefix, label in levels.items():
            if str(prodi).startswith(prefix):
                by_level[label] += 1
                break
    if sum(by_level.values()) != len(national):
        raise AssertionError(f"Jenjang prodi tidak terpetakan penuh: {by_level} dari {len(national)} prodi")
    institution = {
        "lecturers": int(len(lecturers)), "academic_staff": int(len(staff)), "departments": 4,
        "study_programmes": int(len(national)), "study_programmes_by_level": by_level,
        "laboratories": int(len(laboratories)),
        "lecturer_doctoral": int(lecturers["doctoral"].astype(str).str.lower().eq("true").sum()),
        "lecturer_certified": int(certification["certified"].astype(str).str.lower().eq("true").sum()),
        # One SIMASTER extract now supplies every staffing number on the page,
        # so there is a single date to print rather than the two the earlier
        # merge of TCK and P2M rosters forced scene 2.5 to disclose.
        "lecturer_source": "SIMASTER, 3 September 2026",
        # The P2M export the tenaga kependidikan count used to come from is kept
        # beside the SIMASTER figure. It never retired departed staff, and
        # Laporan Dekan 2025 published a third number again; the methodology
        # page shows all three rather than presenting 120 as uncontested.
        "academic_staff_alternatif": {
            "p2m_2026": int(len(p2m_staff)),
            "laporan_dekan_2025": 129,
        },
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
