import { niceMax } from '../components/charts/_utils';

export interface ProgrammeReading {
  angkatan: number;
  jenjang: string;
  prodi: string;
  n: number | null;
  disamarkan: boolean;
}
export interface CohortTotal { angkatan: number; jenjang: string; n: number; }
export type ProgrammeMetric = 'share' | 'count';
export const degreeStyles = [
  { key: 'S1', label: 'S1', dash: '' },
  { key: 'S2', label: 'S2', dash: '10 5' },
  { key: 'S3', label: 'S3', dash: '2 5' },
  { key: 'Non-gelar', label: 'Non-gelar', dash: '10 4 2 4' },
];
export const plot = { width: 960, height: 470, left: 68, right: 112, top: 36, bottom: 52 };
export const formatReading = (n: number, digits = 1) => new Intl.NumberFormat('id-ID', { maximumFractionDigits: digits }).format(n);
export const seriesKey = (row: Pick<ProgrammeReading, 'jenjang' | 'prodi'>) => `${row.jenjang}:${row.prodi}`;

export function prepareProgrammeChart(rows: ProgrammeReading[], totals: CohortTotal[], degree = 'all', metric: ProgrammeMetric = 'share') {
  const years = [...new Set(totals.map(row => row.angkatan))].sort((a, b) => a - b);
  const eligible = rows.filter(row => degree === 'all' || row.jenjang === degree);
  const denominator = (year: number) => totals.filter(row => row.angkatan === year && (degree === 'all' || row.jenjang === degree)).reduce((sum, row) => sum + row.n, 0);
  const value = (row: ProgrammeReading) => row.n === null ? null : metric === 'count' ? row.n : denominator(row.angkatan) > 0 ? row.n / denominator(row.angkatan) * 100 : null;
  // Programme selection only changes visibility: neither denominators nor the scale change.
  const maximum = niceMax(Math.max(1, ...eligible.map(row => value(row) ?? 0)));
  const x = (index: number) => plot.left + index / Math.max(1, years.length - 1) * (plot.width - plot.left - plot.right);
  const y = (n: number) => plot.height - plot.bottom - n / maximum * (plot.height - plot.top - plot.bottom);
  const series = [...new Map(rows.map(row => [seriesKey(row), { key: seriesKey(row), prodi: row.prodi, jenjang: row.jenjang }])).values()].map(item => {
    const points = years.map((year, index) => {
      const row = rows.find(row => seriesKey(row) === item.key && row.angkatan === year);
      const n = row ? value(row) : null;
      return { year, x: x(index), y: n === null ? null : y(n), value: n, count: row?.n ?? null, suppressed: row?.disamarkan ?? false };
    });
    let connected = false;
    const path = points.map(point => {
      if (point.y === null) { connected = false; return ''; }
      const command = `${connected ? 'L' : 'M'} ${point.x} ${point.y}`;
      connected = true;
      return command;
    }).join(' ');
    return { ...item, points, path, dash: degreeStyles.find(style => style.key === item.jenjang)?.dash ?? '' };
  });
  return { years, series, maximum, x, y, denominator, value };
}
