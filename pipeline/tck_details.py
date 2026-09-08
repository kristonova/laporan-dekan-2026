"""Aggregate TCK evidence lists without publishing student identifiers.

These are evidence records, not distinct students or a graduate population.
Read only numbered detail rows; several workbooks append numbered recaps.
"""
from __future__ import annotations

import os
import re
from collections import Counter
from datetime import datetime

import openpyxl
import pandas as pd

from utils import TCK_RINCIAN_DIR, PUBLIC_DATA_DIR, write_json


def detail_rows(prefix: str, columns: dict[str, int], required: str) -> tuple[str, list[dict]]:
    matches = list(TCK_RINCIAN_DIR.glob(prefix + '*.xlsx'))
    if len(matches) != 1:
        raise AssertionError(f'{prefix}: expected one workbook, got {len(matches)}')
    path = matches[0]
    # Some official filenames exceed Windows MAX_PATH.
    filename = '\\\\?\\' + str(path.resolve()) if os.name == 'nt' else str(path)
    book = openpyxl.load_workbook(filename, read_only=True, data_only=True)
    result = []
    try:
        for row in book.active.iter_rows(values_only=True):
            if not row or not isinstance(row[0], (int, float)):
                continue
            item = {key: row[index] if index < len(row) else None for key, index in columns.items()}
            if not isinstance(item[required], str) or not item[required].strip():
                continue
            result.append(item)
    finally:
        book.close()
    if not result:
        raise AssertionError(f'{prefix}: no detail rows')
    return path.name, result


def text(value) -> str:
    return re.sub(r'\s+', ' ', str(value or '')).strip()


def numeric(value) -> float | None:
    try:
        n = float(str(value).replace(',', '.'))
        return n if pd.notna(n) else None
    except (ValueError, TypeError):
        return None


def counts(rows: list[dict], key: str) -> list[dict]:
    return [{'label': label, 'n': n} for label, n in sorted(
        Counter(r[key] for r in rows).items(), key=lambda item: (-item[1], item[0]))]


COUNTRIES = {
    'japan': 'Jepang', 'jepang': 'Jepang', 'timor leste': 'Timor-Leste', 'timor-leste': 'Timor-Leste',
    'cambodia': 'Kamboja', 'united states of america': 'Amerika Serikat', 'russia': 'Rusia',
    'china': 'Tiongkok', 'vietnam': 'Vietnam', 'viet nam': 'Vietnam', 'thailand': 'Thailand',
    'ethiopia': 'Etiopia', 'bolivia': 'Bolivia', 'egypt': 'Mesir', 'algeria': 'Aljazair',
    'saudi arabia': 'Arab Saudi', 'palestinian territory': 'Palestina',
    'sri lanka': 'Sri Lanka',
}


def country(value) -> str:
    raw = text(value)
    if raw in ('', '-'): return 'Belum tercatat'
    base = raw.split(',')[0].strip().lower()
    # "Hailand" is ambiguous: retain it instead of assigning a country.
    if base == 'hailand': return 'Hailand (sesuai sumber)'
    return COUNTRIES.get(base, base.title())


def programme(value) -> str:
    label = text(value)
    replacements = {
        'Doctor in ': 'Doktor ', 'Master in ': 'Magister ', 'Bachelor in ': 'Sarjana ',
        'S1 ': 'Sarjana ', 'Computer Science': 'Ilmu Komputer', 'Chemistry': 'Kimia',
        'Mathematics': 'Matematika', 'Physics': 'Fisika', 'Statistics': 'Statistika',
        'Electronics and Instrumentation': 'Elektronika dan Instrumentasi',
        'Artificial Intelligence': 'Kecerdasan Artifisial', 'Kecerdasan Artificial': 'Kecerdasan Artifisial',
    }
    for old, new in replacements.items(): label = label.replace(old, new)
    return label


def export(name: str, payload: dict, tables: dict[str, list[dict]]) -> None:
    write_json(name + '.json', payload)
    for suffix, rows in tables.items():
        pd.DataFrame(rows).to_csv(PUBLIC_DATA_DIR / f'{name}{suffix}.csv', index=False)


def international_details() -> None:
    credit_source, credit = detail_rows('4.A.', {'prodi': 3, 'negara': 4, 'status': 6}, 'prodi')
    non_source, non = detail_rows('4.B.', {'negara': 2, 'kegiatan': 3, 'departemen': 4, 'status': 5}, 'kegiatan')
    for row in credit:
        row['kelompok'] = 'Kredit'
        row['prodi'] = programme(row['prodi'])
    for row in non:
        row['kelompok'] = 'Nonkredit'
        row['kegiatan'] = text(row['kegiatan'])
        row['departemen'] = text(row['departemen']).title().replace('Dan', 'dan')
    for row in credit + non:
        row['negara'] = country(row['negara'])
        row['status'] = text(row['status']) or 'Belum tercatat'
    panels = []
    for label, rows in [('Semua', credit + non), ('Kredit', credit), ('Nonkredit', non)]:
        nations = counts(rows, 'negara')
        panels.append({
            'label': label, 'total': len(rows), 'per_negara': nations,
            'negara_tercatat': len({r['negara'] for r in rows if r['negara'] not in ('Belum tercatat', 'Hailand (sesuai sumber)')}),
            'negara_belum_tercatat': sum(r['negara'] == 'Belum tercatat' for r in rows),
            'per_status': counts(rows, 'status'),
        })
    payload = {'sumber': [credit_source, non_source], 'panel': panels,
               'per_prodi': counts(credit, 'prodi'), 'per_kegiatan': counts(non, 'kegiatan'),
               'per_departemen': counts(non, 'departemen')}
    export('tck_international', payload, {
        '_negara': [{'kelompok': p['label'], **r} for p in panels for r in p['per_negara']],
        '_program': [{'kelompok': 'Kredit', **r} for r in payload['per_prodi']] +
                    [{'kelompok': 'Nonkredit', **r} for r in payload['per_kegiatan']],
    })


MONTHS = {'januari': 1, 'februari': 2, 'maret': 3, 'april': 4, 'apri': 4, 'mei': 5,
          'juni': 6, 'juli': 7, 'agustus': 8, 'september': 9, 'oktober': 10, 'november': 11, 'desember': 12}


def date_value(value) -> datetime:
    if isinstance(value, datetime): return value
    match = re.fullmatch(r'(\d{1,2})\s+(\w+)\s+(\d{4})', text(value).lower())
    if not match: raise AssertionError(f'Unsupported graduation date: {value}')
    day, month, year = match.groups()
    return datetime(int(year), MONTHS[month], int(day))


def statistics(rows: list[dict], key: str) -> dict:
    values = pd.Series([r[key] for r in rows if r[key] is not None], dtype=float)
    if len(values) < 3:
        return {'terukur': len(values), 'rerata': None, 'median': None, 'q1': None, 'q3': None, 'min': None, 'max': None}
    return {'terukur': len(values), 'rerata': round(float(values.mean()), 2), 'median': round(float(values.median()), 2),
            'q1': round(float(values.quantile(.25)), 2), 'q3': round(float(values.quantile(.75)), 2),
            'min': float(values.min()), 'max': float(values.max())}


def graduate_details() -> None:
    panels, table = [], []
    for prefix, level in [('8B1.', 'S1'), ('8B2.', 'S2'), ('8B3.', 'S3')]:
        cols = {'prodi': 3, 'tanggal': 5, 'ipk': 6, 'semester': 7 if level == 'S1' else 8}
        if level != 'S1': cols['bulan'] = 7
        source, rows = detail_rows(prefix, cols, 'prodi')
        for row in rows:
            row['prodi'] = programme(row['prodi'])
            row['tanggal'] = date_value(row['tanggal'])
            for key in ('ipk', 'semester', 'bulan'): row[key] = numeric(row.get(key))
            if row['semester'] is None or row['semester'] <= 0:
                raise AssertionError(f'{prefix}: invalid study duration')
            if row['ipk'] is not None and not 0 <= row['ipk'] <= 4:
                row['ipk'] = None
        # The S2 month column repeats GPA values in a block of rows. Use the
        # explicitly reported semester column consistently across all levels.
        metric = 'semester'
        by_programme = []
        for prodi in sorted({r['prodi'] for r in rows}):
            group = [r for r in rows if r['prodi'] == prodi]
            by_programme.append({'prodi': prodi, 'n': len(group), **statistics(group, metric),
                                 'ipk': statistics(group, 'ipk')['rerata']})
        panel = {'jenjang': level, 'sumber': source, 'total': len(rows), 'satuan': metric,
                 'awal': min(r['tanggal'] for r in rows).date().isoformat(),
                 'akhir': max(r['tanggal'] for r in rows).date().isoformat(),
                 'lama_studi': statistics(rows, metric), 'ipk': statistics(rows, 'ipk')['rerata'],
                 'ipk_tidak_valid': sum(r['ipk'] is None for r in rows),
                 'bulan_menyalin_ipk': sum(r['bulan'] is not None and r['bulan'] == r['ipk'] for r in rows),
                 'semester': [{'semester': int(n), 'n': count} for n, count in sorted(Counter(r['semester'] for r in rows).items())],
                 'per_prodi': by_programme}
        panels.append(panel)
        table += [{'jenjang': level, 'satuan': metric, **r} for r in by_programme]
    export('tck_graduates', {'panel': panels}, {'_prodi': table,
        '_semester': [{'jenjang': p['jenjang'], **r} for p in panels for r in p['semester']]})


def achievement_details() -> None:
    source, rows = detail_rows('9.', {'departemen': 3, 'hasil': 4, 'tingkat': 5, 'kegiatan': 6, 'status': 7}, 'departemen')
    for row in rows:
        row.update({key: text(value) for key, value in row.items()})
        row['departemen'] = row['departemen'].title().replace('Dan', 'dan')
        row['jenis'] = {'Publikasi mahasiswa': 'Publikasi mahasiswa', 'KKN-TTG 2026': 'Karya KKN-TTG', 'Penyaji': 'Penyaji'}.get(row['hasil'], 'Kejuaraan')
    panels = []
    for label in ['Semua', 'Kejuaraan', 'Publikasi mahasiswa', 'Karya KKN-TTG', 'Penyaji']:
        group = rows if label == 'Semua' else [r for r in rows if r['jenis'] == label]
        panels.append({'label': label, 'total': len(group), 'per_departemen': counts(group, 'departemen'),
                       'per_tingkat': counts(group, 'tingkat'), 'per_hasil': counts(group, 'hasil')})
    events = Counter((r['jenis'], r['kegiatan'], r['hasil'], r['tingkat']) for r in rows)
    event_rows = [{'jenis': kind, 'kegiatan': event, 'hasil': result, 'tingkat': tier, 'n': count}
                  for (kind, event, result, tier), count in sorted(events.items())]
    export('tck_achievements', {'sumber': source, 'total': len(rows), 'per_jenis': counts(rows, 'jenis'),
           'panel': panels, 'kegiatan': event_rows, 'per_status': counts(rows, 'status')},
           {'_kegiatan': event_rows, '_departemen': [{'jenis': p['label'], **r} for p in panels for r in p['per_departemen']]})


def supporting_details() -> None:
    source, rows = detail_rows('8A.', {'prodi': 3, 'kegiatan': 4, 'sks': 5}, 'prodi')
    for r in rows:
        r['prodi'] = text(r['prodi'])
        r['kegiatan'] = text(r['kegiatan']) or 'Belum tercatat'
        r['sks'] = numeric(r['sks'])
    _, fast = detail_rows('10.', {'prodi': 3, 'departemen': 4, 'batch': 5}, 'prodi')
    for r in fast:
        for key in r: r[key] = text(r[key]) or 'Belum tercatat'
    _, buildings = detail_rows('31.', {'gedung': 1, 'kursi_roda': 2, 'ram': 3, 'parkir': 4, 'toilet': 5, 'lift': 6}, 'gedung')
    for r in buildings:
        for key in ('kursi_roda', 'ram', 'parkir', 'toilet', 'lift'): r[key] = int(numeric(r[key]) or 0)
        r['total'] = sum(r[key] for key in ('kursi_roda', 'ram', 'parkir', 'toilet', 'lift'))
    payload = {'mbkm': {'sumber': source, 'total': len(rows), 'per_prodi': counts(rows, 'prodi'),
                       'per_kegiatan': counts(rows, 'kegiatan'), 'sks': statistics(rows, 'sks'),
                       'sks_di_bawah_10': sum(r['sks'] is not None and r['sks'] < 10 for r in rows)},
               'jalur_pascasarjana': {'total': len(fast), 'per_prodi': counts(fast, 'prodi'), 'per_batch': counts(fast, 'batch')},
               'fasilitas': {'total': sum(r['total'] for r in buildings), 'gedung': buildings}}
    export('tck_supporting', payload, {'_fasilitas': buildings, '_mbkm': payload['mbkm']['per_prodi'], '_pascasarjana': payload['jalur_pascasarjana']['per_prodi']})


def generate_tck_details() -> None:
    international_details()
    graduate_details()
    achievement_details()
    supporting_details()


if __name__ == '__main__':
    generate_tck_details()
    print('TCK detail aggregates generated.')
