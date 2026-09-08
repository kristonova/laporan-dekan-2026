import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import ts from 'typescript';

const source=await readFile(new URL('../src/lib/scholarship-profile.ts',import.meta.url),'utf8');
const compiled=ts.transpileModule(source,{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ES2022}}).outputText;
const {scholarshipProfile:profile}=await import(`data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}`);
const data=JSON.parse(await readFile(new URL('../src/data/derived/scholarships.json',import.meta.url)));
const total=rows=>rows.reduce((sum,r)=>sum+r.n,0);

test('all source schemes and programme totals remain visible without filters',()=>{
  const result=profile(data.rincian);
  assert.equal(result.schemes,79);
  assert.equal(result.matched,703);
  assert.equal(total(result.perProgramme),703);
  assert.equal(result.perProgramme.length,data.per_prodi.length);
});

test('programme distribution and scheme list reconcile for every programme and group',()=>{
  for(const programme of ['',...data.per_prodi.map(r=>r.prodi)]){
    for(const group of ['','KIP Kuliah','Program UGM','Program lainnya']){
      for(const query of ['','kip','bayan','bank indonesia','zzz-no-match']){
        const result=profile(data.rincian,programme,group,query);
        assert.equal(total(result.rows),result.matched);
        assert.equal(total(result.perProgramme),result.matched);
        assert.ok(result.matched<=result.total);
        assert.ok(Number.isFinite(result.max)&&result.max>=1);
        if(programme) assert.ok(result.perProgramme.length<=1);
      }
    }
  }
});

test('search is case insensitive and matches names without dropping scheme variants',()=>{
  const expected=data.per_skema.filter(r=>/kip/i.test(r.beasiswa));
  const result=profile(data.rincian,'','','  kIp  ');
  assert.equal(result.rows.length,expected.length);
  assert.equal(result.matched,expected.reduce((sum,r)=>sum+r.penerima,0));
});
