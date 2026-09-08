export type ScholarshipRow = { beasiswa:string; prodi:string; penerima:number };
export const programmeLabel:Record<string,string>={Elins:'Elektronika dan Instrumentasi',IlKomp:'Ilmu Komputer',Matemat:'Matematika',Aktuaria:'Ilmu Aktuaria'};
export const scholarshipGroup=(name:string)=>/KIP|Kartu Indonesia Pintar/i.test(name)?'KIP Kuliah':/UGM/i.test(name)?'Program UGM':'Program lainnya';
export function scholarshipProfile(rows:ScholarshipRow[],prodi='',group='',query='') {
  const source=rows.filter(r=>!prodi||r.prodi===prodi).filter(r=>!group||scholarshipGroup(r.beasiswa)===group);
  const schemes=new Map<string,number>();
  source.forEach(r=>schemes.set(r.beasiswa,(schemes.get(r.beasiswa)||0)+r.penerima));
  const all=[...schemes].map(([label,n])=>({label,n})).filter(r=>r.n>0).sort((a,b)=>b.n-a.n||a.label.localeCompare(b.label,'id'));
  const matched=all.filter(r=>r.label.toLocaleLowerCase('id').includes(query.trim().toLocaleLowerCase('id')));
  return {total:all.reduce((sum,r)=>sum+r.n,0),schemes:all.length,rows:matched,matched:matched.reduce((sum,r)=>sum+r.n,0),max:Math.max(1,...matched.map(r=>r.n))};
}
