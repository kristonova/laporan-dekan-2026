# Pipeline data — Lima Tahun FMIPA

Jalankan dari root aplikasi:

```bash
npm run data
npm run validate:data
```

Kedua perintah memanggil `run-python.mjs`, yang memilih interpreter dari `.venv/`
aplikasi ini. Siapkan sekali sebelum menjalankan pipeline:

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r pipeline/requirements.txt   # Windows
.venv/bin/python -m pip install -r pipeline/requirements.txt           # macOS/Linux
```

Urutan tahap:

1. `00_load.py` membaca seluruh sumber sekali: CSV multi-part P2M di `data ugm/p2m/`, berkas Excel `TCK 2026.xlsx`, workbook kerja sama LENTERA, tujuh tabel akademik, dua ekspor tracer study `.xls`, serta rekap Posbindu. Baris didedup dan asal data dicatat pada manifest.
2. `01_clean.py` menormalisasi provinsi, memetakan departemen publikasi melalui ID Scopus, memulihkan pemisah ribuan skor SINTA, menghitung ulang rasio dan status TCK, mengklasifikasi bidang kerja lulusan, serta membuang kolom tingkat individu.
3. `02_aggregate.py` menghasilkan JSON kecil di `src/data/derived/` dan cermin unduhan yang sudah disanitasi di `public/data/`.
4. `03_validate.py` menguji jumlah part, angka jangkar PRD, 42 indikator TCK, arah indikator #27, kesesuaian dengan berkas rincian, dan ketiadaan kunci privat.

## Berkas terkurasi di `mappings/`

| Berkas | Isi |
| --- | --- |
| `tck_pillar.csv` | Urutan 42 indikator dan pemetaan pilarnya |
| `tck_meta.csv` | Satuan, arah, program renstra, penanggung jawab, tag, sumber — metadata yang tidak ada di berkas Excel |
| `tck_2026_anggaran.json` | Pagu dan realisasi anggaran fakultas |
| `provinsi_bps.csv` | Normalisasi nama provinsi ke kode BPS |
| `bidang_kerja.csv` | Aturan regex bidang kerja tracer study → 13 sektor kanonik (99,8% terklasifikasi) |

## Keputusan yang disengaja

- **Status TCK diturunkan, bukan disalin.** Berkas sumber hanya membedakan `tercapai`/`belum`; empat level pada laporan dihitung dari rasio dengan ambang 100% / 85% / 50%. Indikator berarah turun (#27) memakai rasio terbalik.
- **Satuan campur dinormalisasi secara eksplisit.** Capaian indikator 1c ditulis dalam rupiah penuh sementara targetnya dalam miliar, sehingga diskalakan. Indikator persentase #5b dan #8b1–8b3 menyimpan cacah orang di kolom TW1/TW3 tanpa penyebut: nilainya dipindah ke kolom `_cacah`, persentase dikosongkan, dan penilaian dikembalikan ke TW2.
- **Anomali dilaporkan, bukan disembunyikan.** Capaian triwulan yang tidak kumulatif (#1a, #15, #32) tercatat pada `anomali` tiap baris dan pada `validation_report.json`, lalu ditampilkan di `/data` dan pada komponen `TckOverview`.
- **Koordinat tidak ditebak.** `outreach_points.json` dan `partnership_points.json` mempertahankan status lokasi; UI memakai centroid provinsi skematik dengan label metodologis yang terlihat.
- **Data perorangan tidak pernah keluar.** Nama, NIP/NIM/NIU, kontak, dan seluruh nilai pemeriksaan Posbindu dibuang di tahap load atau clean. `03_validate.py` menolak proses bila salah satu kunci privat muncul di `src/data/derived/`.
- **Sesi Posbindu ganda didedup.** Satu lembar rekap menduplikasi sesi lain secara utuh; kunjungan dikunci pada pasangan (tanggal, peserta) sebelum nama dibuang.

`build-service-worker.mjs` dijalankan setelah build untuk memasukkan seluruh output ber-hash ke precache. `check-build.mjs` memeriksa tautan internal, fragmen, nilai non-finit, format tahun, dan keberadaan setiap URL precache.
