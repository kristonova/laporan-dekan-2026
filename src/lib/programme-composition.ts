import { niceMax } from '../components/charts/_utils';
import type { ProgrammeReading, CohortTotal, ProgrammeMetric } from './programme-trends';

export const DEGREE_PALETTE = [
  { key: 'S1', label: 'S1', color: '#01416b' },
  { key: 'S2', label: 'S2', color: '#527f9d' },
  { key: 'S3', label: 'S3', color: '#598b86' },
  { key: 'Non-gelar', label: 'Non-gelar', color: '#90979d' },
];

export interface ProgrammeCompositionPoint {
  year: number;
  count: number | null;
  value: number | null;
  x: number;
  y: number | null;
}

interface ProgrammeCompositionSegment {
  jenjang: string;
  n: number | null;
  share: number | null;
}

interface ProgrammeAggregate {
  count: number | null;
  knownCount: number;
  partial: boolean;
  share: number | null;
  segments: ProgrammeCompositionSegment[];
}

export interface ProgrammeComposition extends ProgrammeAggregate {
  prodi: string;
  points: ProgrammeCompositionPoint[];
  path: string;
  selectedPoint: ProgrammeCompositionPoint;
}

/** Counts describe records within an entry cohort, rather than active students. */
export function prepareProgrammeComposition(
  rows: ProgrammeReading[],
  totals: CohortTotal[],
  degree = 'all',
  year?: number,
  programme = 'all',
  metric: ProgrammeMetric = 'count',
) {
  const years = [...new Set([...totals.map(row => row.angkatan), ...rows.map(row => row.angkatan)])].sort((a, b) => a - b);
  const selectedYear = year !== undefined && years.includes(year) ? year : years.at(-1) ?? 0;
  const eligible = rows.filter(row => degree === 'all' || row.jenjang === degree);
  const names = [...new Set(eligible.map(row => row.prodi))];
  const denominatorFor = (cohort: number) => totals
    .filter(row => row.angkatan === cohort && (degree === 'all' || row.jenjang === degree))
    .reduce((sum, row) => sum + row.n, 0);
  const denominator = denominatorFor(selectedYear);
  const degreeOrder = (name: string) => {
    const index = DEGREE_PALETTE.findIndex(item => item.key === name);
    return index < 0 ? DEGREE_PALETTE.length : index;
  };

  const aggregates = names.map(prodi => {
    const programmeRows = eligible.filter(row => row.prodi === prodi);
    // A programme need not exist at every degree. Only an absent observation
    // within an existing programme/degree series means missing data.
    const degrees = [...new Set(programmeRows.map(row => row.jenjang))]
      .sort((a, b) => degreeOrder(a) - degreeOrder(b) || a.localeCompare(b, 'id'));
    const observations = new Map(programmeRows.map(row => [`${row.angkatan}:${row.jenjang}`, row]));
    const byYear = new Map<number, ProgrammeAggregate>();
    for (const cohort of years) {
      const cohortDenominator = denominatorFor(cohort);
      const segments = degrees.map(jenjang => {
        const row = observations.get(`${cohort}:${jenjang}`);
        const n = row && !row.disamarkan ? row.n : null;
        return { jenjang, n, share: n !== null && cohortDenominator > 0 ? n / cohortDenominator * 100 : null };
      });
      const partial = segments.some(segment => segment.n === null);
      const knownCount = segments.reduce((sum, segment) => sum + (segment.n ?? 0), 0);
      const count = partial ? null : knownCount;
      byYear.set(cohort, {
        count, knownCount, partial, segments,
        share: count !== null && cohortDenominator > 0 ? count / cohortDenominator * 100 : null,
      });
    }
    return { prodi, byYear };
  });

  const reading = (aggregate: ProgrammeAggregate) => metric === 'count' ? aggregate.count : aggregate.share;
  // Both scales are computed before applying the programme filter, so selecting
  // a smaller programme does not make its bar or trend appear artificially large.
  const maximum = niceMax(Math.max(1, ...aggregates.map(item => reading(item.byYear.get(selectedYear)!) ?? 0)));
  const trendMaximum = niceMax(Math.max(1, ...aggregates.flatMap(item => [...item.byYear.values()].map(aggregate => reading(aggregate) ?? 0))));
  const programmes: ProgrammeComposition[] = aggregates
    .filter(item => programme === 'all' || item.prodi === programme)
    .map(item => {
      const points = years.map((cohort, index) => {
        const aggregate = item.byYear.get(cohort)!;
        const value = reading(aggregate);
        return {
          year: cohort,
          count: aggregate.count,
          value,
          x: 4 + index / Math.max(1, years.length - 1) * 112,
          y: value === null ? null : 32 - value / trendMaximum * 28,
        };
      });
      let connected = false;
      const path = points.map(point => {
        if (point.y === null) { connected = false; return ''; }
        const command = `${connected ? 'L' : 'M'} ${point.x} ${point.y}`;
        connected = true;
        return command;
      }).filter(Boolean).join(' ');
      return {
        prodi: item.prodi,
        ...item.byYear.get(selectedYear)!,
        points,
        path,
        selectedPoint: points.find(point => point.year === selectedYear)!,
      };
    })
    .sort((a, b) => {
      if (a.count === null && b.count !== null) return 1;
      if (a.count !== null && b.count === null) return -1;
      return (b.count ?? 0) - (a.count ?? 0) || a.prodi.localeCompare(b.prodi, 'id');
    });

  return {
    years,
    year: selectedYear,
    denominator,
    maximum,
    trendMaximum,
    programmes,
    visibleTotal: programmes.some(item => item.partial) ? null : programmes.reduce((sum, item) => sum + item.count!, 0),
    knownVisibleTotal: programmes.reduce((sum, item) => sum + item.knownCount, 0),
  };
}
