"""Anonymous education origins: never join synthetic participant IDs to rosters."""
import re
import pandas as pd
from utils import ACADEMIC_DIR, CLEAN_DIR, LOADED_DIR, records, read_workbook, write_json

SOURCE = '20260902 Data Asal Sekolah dan Asal Univ Fak MIPA tahun 2021-2026.xlsx'
SOURCE_DATE = '2 September 2026'
COLUMNS = {'Prodi': 'prodi', 'Jenjang': 'jenjang', 'Angkatan': 'angkatan',
           'SMA': 'sma', 'Univ S1': 'univ_s1', 'Univ S2': 'univ_s2'}
LEVELS = ['S1', 'S2', 'S3', 'NONDEGREE']


def load_origins():
    source = read_workbook(ACADEMIC_DIR / SOURCE, 'Data', header=0)
    # NIU and No Peserta are serial surrogates in this export, not linkage keys.
    data = source[list(COLUMNS)].rename(columns=COLUMNS).copy()
    data = data.dropna(how='all')
    assert data['jenjang'].isin(LEVELS).all()
    data['angkatan'] = pd.to_numeric(data['angkatan'], errors='raise').astype(int)
    assert data['angkatan'].between(2021, 2026).all()
    assert data['prodi'].notna().all()
    # Equal anonymous attributes can describe different people: do not deduplicate.
    return data


def clean_origins():
    data = pd.read_csv(LOADED_DIR / 'student_origins.csv')
    for key in ['prodi', 'sma', 'univ_s1', 'univ_s2']:
        data[key] = data[key].map(lambda v: re.sub(r'\s+', ' ', str(v)).strip().upper() if pd.notna(v) else None)
    data.to_csv(CLEAN_DIR / 'student_origins.csv', index=False)


def aggregate_origins(output, suppress):
    data = pd.read_csv(CLEAN_DIR / 'student_origins.csv')
    years = sorted(data['angkatan'].unique().tolist())
    levels = data.groupby('jenjang').size()
    cohorts = data.groupby(['angkatan', 'jenjang']).size().reset_index(name='n')
    programmes = data.groupby(['angkatan', 'jenjang', 'prodi']).size().reset_index(name='n')
    output('students_origins_cohorts.json', records(suppress(cohorts)))
    output('students_origins_programmes.json', records(suppress(programmes)))
    panels = []
    for level, field, label in [('S1', 'sma', 'SMA/MA asal mahasiswa S1'),
                                ('S2', 'univ_s1', 'Universitas S1 asal mahasiswa S2'),
                                ('S3', 'univ_s2', 'Universitas S2 asal mahasiswa S3'),
                                ('S3', 'univ_s1', 'Universitas S1 asal mahasiswa S3')]:
        for year in [0, *years]:
            subset = data[data['jenjang'].eq(level) & (data['angkatan'].eq(year) if year else True)]
            reported = subset.dropna(subset=[field])
            counts = reported.groupby(field).size().reset_index(name='n').rename(columns={field: 'institusi'})
            counts = suppress(counts).sort_values(['n', 'institusi'], ascending=[False, True], na_position='last')
            panels.append({'jenjang': level, 'asal': field, 'label': label, 'angkatan': year,
                           'total': len(subset), 'tercatat': len(reported), 'tidak_tercatat': len(subset)-len(reported),
                           'institusi_unik': reported[field].nunique(), 'institusi': records(counts)})
    write_json('students_origins.json', {
        'sumber': SOURCE, 'tanggal': SOURCE_DATE, 'tahun': years, 'total': len(data),
        'per_jenjang': {level: int(levels.get(level, 0)) for level in LEVELS},
        'panel': panels,
        'catatan': 'Cakupan rekaman angkatan, bukan jumlah mahasiswa aktif atau orang unik lintas jenjang. Sumber anonim berdiri sendiri; tidak ditautkan atau dijumlahkan dengan daftar mahasiswa lama. Nama institusi diseragamkan kapitalisasi dan spasinya; alias tidak digabung tanpa rujukan.'
    })
    output('students_origins_institutions.json', [
        {key: p[key] for key in ['jenjang', 'asal', 'angkatan']} | row for p in panels for row in p['institusi']
    ])
