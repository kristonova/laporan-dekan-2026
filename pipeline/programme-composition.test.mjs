import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import ts from 'typescript';

// Load the actual TypeScript helper without a second runtime or generated files.
const compile = source => ts.transpileModule(source, {
  compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ES2022 },
}).outputText;
const moduleUrl = source => `data:text/javascript;base64,${Buffer.from(source).toString('base64')}`;
const utils = moduleUrl(compile(await readFile(new URL('../src/components/charts/_utils.ts', import.meta.url), 'utf8')));
const helper = compile(await readFile(new URL('../src/lib/programme-composition.ts', import.meta.url), 'utf8'))
  .replace("'../components/charts/_utils'", JSON.stringify(utils));
const { prepareProgrammeComposition: prepare } = await import(moduleUrl(helper));
const realRows = JSON.parse(await readFile(new URL('../src/data/derived/students_programme_trends.json', import.meta.url)));
const realTotals = JSON.parse(await readFile(new URL('../src/data/derived/students_programme_trends_meta.json', import.meta.url))).per_angkatan_jenjang;
const row = (angkatan, jenjang, prodi, n, disamarkan = false) => ({ angkatan, jenjang, prodi, n, disamarkan });
const close = (actual, expected) => assert.ok(Math.abs(actual - expected) < 1e-10, `${actual} differs from ${expected}`);

test('uses latest cohort and combines programmes across degrees with source totals as denominator', () => {
  const chart = prepare(realRows, realTotals);
  assert.equal(chart.year, 2026);
  assert.deepEqual(chart.years, [2021, 2022, 2023, 2024, 2025, 2026]);
  assert.equal(chart.denominator, 1151);
  assert.equal(chart.visibleTotal, 1151);
  assert.equal(chart.knownVisibleTotal, 1151);
  assert.equal(chart.programmes.length, 10);
  assert.equal(chart.programmes[0].prodi, 'Kimia');
  assert.equal(chart.programmes[0].count, 247);
  assert.deepEqual(chart.programmes[0].segments.map(item => item.n), [182, 45, 20]);
  close(chart.programmes[0].share, 247 / 1151 * 100);
  assert.equal(chart.programmes[1].prodi, 'Ilmu Komputer');
  assert.equal(chart.programmes[1].count, 244);
});

test('programme selection changes visible total without renormalizing shares or scales', () => {
  for (const metric of ['count', 'share']) {
    const all = prepare(realRows, realTotals, 'S2', 2026, 'all', metric);
    const selected = prepare(realRows, realTotals, 'S2', 2026, 'Elektronika dan Instrumentasi', metric);
    assert.equal(selected.denominator, 211);
    assert.equal(selected.visibleTotal, 8);
    close(selected.programmes[0].share, 8 / 211 * 100);
    assert.equal(selected.maximum, all.maximum);
    assert.equal(selected.trendMaximum, all.trendMaximum);
    assert.deepEqual(selected.programmes[0].points, all.programmes.find(item => item.prodi === 'Elektronika dan Instrumentasi').points);
    close(selected.programmes[0].selectedPoint.value, metric === 'count' ? 8 : 8 / 211 * 100);
  }
});

test('year selection selects the right cohort while retaining the six-year context and scale', () => {
  const first = prepare(realRows, realTotals, 'S2', 2021, 'Elektronika dan Instrumentasi');
  const last = prepare(realRows, realTotals, 'S2', 2026, 'Elektronika dan Instrumentasi');
  assert.equal(first.year, 2021);
  assert.equal(first.denominator, 155);
  assert.equal(first.programmes[0].count, 0);
  assert.equal(first.programmes[0].partial, false);
  assert.equal(first.programmes[0].selectedPoint.y, 32);
  assert.equal(first.programmes[0].points.length, 6);
  assert.equal(first.trendMaximum, last.trendMaximum);
  assert.equal(first.programmes[0].selectedPoint.x, 4);
  assert.equal(last.programmes[0].selectedPoint.x, 116);
  assert.equal(prepare(realRows, realTotals, 'all', 1900).year, 2026);
});

test('incompatible programme and degree selections return an explicit empty selection', () => {
  const chart = prepare(realRows, realTotals, 'S3', 2026, 'Elektronika dan Instrumentasi');
  assert.deepEqual(chart.programmes, []);
  assert.equal(chart.denominator, 75);
  assert.equal(chart.visibleTotal, 0);
  assert.ok(prepare(realRows, realTotals, 'S3').programmes.every(item => !['Geofisika', 'Ilmu Aktuaria'].includes(item.prodi)));
});

test('withheld and missing observations suppress exact totals and create gaps, while preserving known segments', () => {
  const rows = [
    row(2021, 'S1', 'A', 10), row(2021, 'S2', 'A', 5),
    row(2022, 'S1', 'A', 12), row(2022, 'S2', 'A', null, true),
    row(2023, 'S1', 'A', 15), row(2023, 'S2', 'A', 5),
    row(2024, 'S1', 'A', 20), // Missing S2 observation is unknown, not zero.
    row(2025, 'S1', 'A', 20), row(2025, 'S2', 'A', 0),
  ];
  const totals = [2021, 2022, 2023, 2024, 2025].flatMap(angkatan => [
    { angkatan, jenjang: 'S1', n: 40 }, { angkatan, jenjang: 'S2', n: 10 },
  ]);
  const chart = prepare(rows, totals, 'all', 2022);
  const item = chart.programmes[0];
  assert.equal(item.count, null);
  assert.equal(item.share, null);
  assert.equal(item.knownCount, 12);
  assert.equal(item.partial, true);
  assert.equal(chart.visibleTotal, null);
  assert.equal(chart.knownVisibleTotal, 12);
  assert.equal(item.segments[0].n, 12);
  assert.equal(item.segments[1].share, null);
  assert.deepEqual(item.points.map(point => point.count), [15, null, 20, null, 20]);
  assert.equal(item.selectedPoint.y, null);
  assert.equal(item.path.match(/M /g).length, 3);
  assert.equal(item.path.includes('L '), false);
  assert.equal(item.points[3].y, null);
  const zero = prepare(rows, totals, 'S2', 2025).programmes[0];
  assert.equal(zero.count, 0);
  assert.equal(zero.share, 0);
  assert.equal(zero.selectedPoint.y, 32);
});

test('share calculations keep suppressed records in the supplied denominator and guard absent totals', () => {
  const rows = [row(2026, 'S1', 'A', 10), row(2026, 'S1', 'B', null, true)];
  const totals = [{ angkatan: 2026, jenjang: 'S1', n: 12 }];
  const chart = prepare(rows, totals, 'S1', 2026, 'A', 'share');
  close(chart.programmes[0].share, 10 / 12 * 100);
  assert.equal(chart.denominator, 12);
  const noTotal = prepare([row(2026, 'S1', 'A', 10)], [], 'all', 2026, 'all', 'share');
  assert.equal(noTotal.denominator, 0);
  assert.equal(noTotal.programmes[0].count, 10);
  assert.equal(noTotal.programmes[0].share, null);
  assert.equal(noTotal.programmes[0].segments[0].share, null);
  assert.equal(noTotal.programmes[0].selectedPoint.value, null);
  assert.equal(noTotal.programmes[0].path, '');
});

test('suppression flag remains authoritative and missing degrees are not invented', () => {
  const rows = [row(2026, 'S1', 'A', 1, true), row(2026, 'S2', 'B', 10)];
  const totals = [{ angkatan: 2026, jenjang: 'S1', n: 1 }, { angkatan: 2026, jenjang: 'S2', n: 10 }];
  const chart = prepare(rows, totals);
  assert.equal(chart.programmes.find(item => item.prodi === 'A').count, null);
  assert.equal(chart.programmes.find(item => item.prodi === 'A').knownCount, 0);
  assert.equal(chart.programmes.find(item => item.prodi === 'B').partial, false);
  assert.equal(chart.programmes.find(item => item.prodi === 'B').segments.length, 1);
  assert.equal(chart.visibleTotal, null);
});

test('empty datasets have finite scales and no invented observations', () => {
  const chart = prepare([], []);
  assert.deepEqual(chart.years, []);
  assert.deepEqual(chart.programmes, []);
  assert.equal(chart.visibleTotal, 0);
  assert.ok(Number.isFinite(chart.maximum) && chart.maximum > 0);
  assert.ok(Number.isFinite(chart.trendMaximum) && chart.trendMaximum > 0);
});
