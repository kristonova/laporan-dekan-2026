"""Cohort programme counts from disjoint degree coverage in two student sources."""

import re

import pandas as pd

from student_origins import SOURCE as ORIGINS_SOURCE, SOURCE_DATE
from utils import ACADEMIC_DIR, CLEAN_DIR, records, write_json


LEVELS = ["S1", "S2", "S3", "Non-gelar"]
NON_DEGREE_LABEL = "Non-gelar (pertukaran & MBKM)"


def postgraduate_programme(value: str, level: str) -> str:
    """Keep degree in its own field, with the same programme labels as S1."""
    prefix = {"S2": "MAGISTER ", "S3": "DOKTOR "}[level]
    text = re.sub(r"\s+", " ", str(value)).strip().upper()
    if not text.startswith(prefix):
        raise ValueError(f"Nama prodi {level} tidak sesuai sumber: {value!r}")
    return " ".join(
        word.lower() if word == "DAN" else word.capitalize()
        for word in text[len(prefix):].split()
    )


def aggregate_programme_trends(output, suppress):
    # The roster cleaner has already folded regular and IUP classes into one
    # programme. Non-degree remains a separate series as in the original chart.
    roster = pd.read_csv(CLEAN_DIR / "students.csv", usecols=["angkatan", "jenjang", "prodi"])
    assert roster["jenjang"].isin(["Sarjana", "Non-gelar"]).all()
    roster["jenjang"] = roster["jenjang"].replace({"Sarjana": "S1"})
    roster.loc[roster["jenjang"].eq("Non-gelar"), "prodi"] = NON_DEGREE_LABEL

    origins = pd.read_csv(CLEAN_DIR / "student_origins.csv", usecols=["angkatan", "jenjang", "prodi"])
    # S1 and non-degree rows in this workbook overlap the rosters. Take only
    # postgraduate degrees, without joining anonymous identifiers or deduping
    # repeated attributes that may belong to different students.
    postgraduate = origins[origins["jenjang"].isin(["S2", "S3"])].copy()
    postgraduate["prodi"] = [
        postgraduate_programme(programme, level)
        for programme, level in zip(postgraduate["prodi"], postgraduate["jenjang"])
    ]
    students = pd.concat([roster, postgraduate], ignore_index=True)
    students["angkatan"] = pd.to_numeric(students["angkatan"], errors="raise").astype(int)
    assert students["angkatan"].between(2021, 2026).all()
    assert students[["angkatan", "jenjang", "prodi"]].notna().all().all()
    years = list(range(2021, 2027))

    counts = students.groupby(["angkatan", "jenjang", "prodi"]).size()
    series = students[["jenjang", "prodi"]].drop_duplicates()
    grid = pd.MultiIndex.from_tuples([
        (year, level, programme)
        for year in years
        for level in LEVELS
        for programme in sorted(series.loc[series["jenjang"].eq(level), "prodi"])
    ], names=["angkatan", "jenjang", "prodi"])
    # Zero means no row in the source for this programme/cohort. Suppressed
    # small counts remain null and must never be drawn as zero in the chart.
    by_programme = counts.reindex(grid, fill_value=0).reset_index(name="n")
    output("students_programme_trends.json", records(suppress(by_programme)))

    per_level = students.groupby("jenjang").size()
    per_year = students.groupby("angkatan").size().reset_index(name="total")
    per_year_level = students.groupby(["angkatan", "jenjang"]).size().reset_index(name="n")
    write_json("students_programme_trends_meta.json", {
        "tahun": years,
        "total": len(students),
        "per_jenjang": {level: int(per_level.get(level, 0)) for level in LEVELS},
        "per_angkatan": records(per_year),
        "per_angkatan_jenjang": records(per_year_level),
        "sumber": [
            {
                "jenjang": ["S1", "Non-gelar"],
                "berkas": [path.name for path in sorted((ACADEMIC_DIR / "daftar mahasiswa").glob("Daftar mahasiswa *.xlsx"))],
            },
            {"jenjang": ["S2", "S3"], "berkas": [ORIGINS_SOURCE], "tanggal": SOURCE_DATE},
        ],
        "catatan": (
            "Jumlah rekaman per angkatan 2021–2026, bukan jumlah mahasiswa aktif atau orang unik lintas jenjang. "
            "S1 reguler dan kelas internasional digabung per prodi; non-gelar mencakup pertukaran dan MBKM dari daftar mahasiswa. "
            "Workbook asal pendidikan hanya menyumbang S2 dan S3, sehingga cakupan kedua sumber tidak tumpang tindih. "
            "Nol berarti tidak ada rekaman prodi pada angkatan tersebut; bukan penetapan tahun pembukaan prodi. "
            "Sel 1–2 disamarkan sebagai null. Penyebut persentase memakai seluruh rekaman dalam jenjang yang dipilih, "
            "termasuk sel yang disamarkan, dan tetap sama saat prodi difilter."
        ),
    })
