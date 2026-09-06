import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import ts from 'typescript';

const source = await readFile(new URL('../src/lib/ipk-beeswarm.ts', import.meta.url), 'utf8');
const compiled = ts.transpileModule(source, { compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ES2022 } }).outputText;
const { layoutBeeswarm, programmePoints, cohortColors } = await import(`data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}`);
const data = JSON.parse(await readFile(new URL('../src/data/derived/students_ipk.json', import.meta.url), 'utf8'));

test('every cohort and combined programme preserves all grades, fits the plot, and has no overlapping dots', () => {
  let layouts = 0;
  for (const width of [280, 720]) {
    const radius = width < 440 ? 1.65 : 2.4;
    for (const year of [0, ...data.tahun]) {
      const readings = year ? data.per_prodi.filter(row => row.angkatan === year) : data.gabungan;
      for (const reading of readings) {
        const points = programmePoints(data.sebaran, reading.prodi).filter(point => !year || point.angkatan === year);
        const swarm = layoutBeeswarm(points, width, radius);
        assert.equal(swarm.points.length, reading.tercatat);
        assert.deepEqual(swarm.points.map(point => point.ipk).sort((a,b) => a-b), points.map(point => point.ipk).sort((a,b) => a-b));
        for (let i = 0; i < swarm.points.length; i++) {
          const point = swarm.points[i];
          assert.ok(Math.abs(point.x - (8 + point.ipk / 4 * (width - 16))) < 1e-9);
          assert.ok(point.x >= radius && point.x <= width - radius);
          assert.ok(point.y >= radius && point.y <= swarm.height - radius);
          assert.ok(cohortColors[point.angkatan]);
          for (let j = i + 1; j < swarm.points.length; j++) {
            const other = swarm.points[j];
            if (other.x - point.x >= radius * 2 + .55) break;
            assert.ok(Math.hypot(point.x - other.x, point.y - other.y) >= radius * 2 + .55 - 1e-7, `${reading.prodi}, ${year}, ${width}: overlapping points`);
          }
        }
        layouts++;
      }
    }
  }
  assert.equal(layouts, 96);
});

test('equal grades remain exact and layout is deterministic when input order changes', () => {
  const points = Array.from({ length: 60 }, (_, order) => ({ ipk: order < 30 ? 0 : 4, angkatan: 2021 + order % 5, order }));
  const forward = layoutBeeswarm(points, 320, 1.65);
  assert.deepEqual(forward, layoutBeeswarm(points.slice().reverse(), 320, 1.65));
  assert.equal(new Set(forward.points.filter(point => point.ipk === 0).map(point => point.x)).size, 1);
  assert.equal(new Set(Object.values(cohortColors)).size, data.tahun.length);
  assert.equal(layoutBeeswarm([], 320).points.length, 0);
});
