# Pipeline data — Lima Tahun FMIPA

Pembaruan 2 September 2026: `student_origins.py` memproses workbook
`20260902 Data Asal Sekolah dan Asal Univ Fak MIPA tahun 2021-2026.xlsx`.
Sebanyak 6.856 rekaman mencakup S1 (4.571), S2 (1.362), S3 (534), dan non-gelar (389).
Hanya prodi, jenjang, angkatan, SMA, universitas S1, dan universitas S2 dibaca ke keluaran lokal.
Nomor peserta dan NIU pengganti tidak disimpan atau dipakai untuk mencocokkan individu.
Untuk visualisasi asal pendidikan, sumber ini berdiri sendiri; jangan menjumlahkan
seluruh isinya dengan daftar mahasiswa lama.
Nama institusi dinormalisasi pada kapitalisasi dan spasi; alias tidak digabung berdasarkan dugaan.
Angkatan 0 pada unduhan institusi berarti gabungan 2021–2026 yang dihitung langsung,
bukan untuk dijumlahkan dengan baris per-angkatan. Sel 1–2 tetap disamarkan.

`student_programme_trends.py` menyiapkan grafik garis komposisi prodi 2021–2026.
`students_programme_trends.json` dan CSV memuat S1 (4.571) serta non-gelar (374)
dari `daftar mahasiswa`, ditambah hanya S2 (1.362) dan S3 (534) dari workbook asal
pendidikan. Total 6.841 rekaman terdiri dari cakupan jenjang yang tidak tumpang
tindih, bukan orang unik lintas jenjang. Kelas reguler dan IUP S1 digabung per
prodi; semua non-gelar roster menjadi satu seri pertukaran dan MBKM.
Ada 19 seri dalam satu grid 2021–2026. Nilai nol berarti tidak ada rekaman sumber
pada kombinasi prodi/angkatan itu; nilai null berarti sel kecil disamarkan.
`students_programme_trends_meta.json` menyertakan sumber dan total angkatan/jenjang
sebagai penyebut persentase yang tetap utuh saat prodi difilter atau sel disamarkan.

IPK tetap berasal dari daftar mahasiswa S1 2021–2025, karena workbook baru tidak memuat IPK.
`students_ipk.json` kini memuat kuartil, median, dan whisker pengamatan dalam 1,5 IQR
per prodi/angkatan serta gabungan yang dihitung dari semua pengamatan, dengan interpolasi
kuartil linear. Nilai numerik 0–4, termasuk nol, disertakan; kelompok di bawah tiga ditahan.
`students_ipk_distribution.csv` menyajikan statistik per prodi/angkatan tanpa nilai individu.
Pembaruan 6 September 2026: grafik memakai beeswarm dengan satu titik per IPK dan warna
tetap menurut angkatan. `students_ipk.json` menambahkan `sebaran`, yaitu daftar nilai asli
yang diurutkan per prodi/angkatan, tanpa nama, NIM, urutan sumber, atau atribut pribadi lain.
Kelompok kurang dari tiga tetap ditahan. Nilai nol dan ekstrem tidak dihilangkan atau
diambil sampelnya. Susunan vertikal menghindari tabrakan titik tanpa menggeser IPK pada
sumbu horizontal. Tabel dan median mengikuti filter; CSV tetap berupa ringkasan statistik.
Keputusan boxplot di `docs/visualisasi-20260905.md` merupakan catatan desain sebelumnya.

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

1. `00_load.py` membaca seluruh sumber sekali: CSV multi-part P2M di `data ugm/p2m/`, berkas Excel `TCK 2026.xlsx`, workbook kerja sama LENTERA, tujuh tabel akademik, dua ekspor tracer study `.xls`, serta empat sumber Posbindu (rekap 2026, digitasi arsip analog 2022–2024, dan registri peserta). Baris didedup dan asal data dicatat pada manifest.
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
| `jalur_masuk.csv` | Normalisasi nama jalur masuk mahasiswa |
| `pekerjaan_wali.csv` | Normalisasi pekerjaan wali mahasiswa |
| `posbindu_risiko.csv` | Kategori klinis sumber → tiga pita risiko (Normal, Waspada, Berisiko) |
| `posbindu_ambang.csv` | Ambang klinis per indikator dan jenis kelamin, dibaca berurutan dan yang pertama cocok dipakai |
| `posbindu_ambang_tensi.csv` | Ambang tekanan darah, yang butuh sistolik dan diastolik sekaligus |

## Keputusan yang disengaja

- **Status TCK diturunkan, bukan disalin.** Berkas sumber hanya membedakan `tercapai`/`belum`; empat level pada laporan dihitung dari rasio dengan ambang 100% / 85% / 50%. Indikator berarah turun (#27) memakai rasio terbalik.
- **Satuan campur dinormalisasi secara eksplisit.** Capaian indikator 1c ditulis dalam rupiah penuh sementara targetnya dalam miliar, sehingga diskalakan. Indikator persentase #5b dan #8b1–8b3 menyimpan cacah orang di kolom TW1/TW3 tanpa penyebut: nilainya dipindah ke kolom `_cacah`, persentase dikosongkan, dan penilaian dikembalikan ke TW2.
- **Anomali dilaporkan, bukan disembunyikan.** Capaian triwulan yang tidak kumulatif (#1a, #15, #32) tercatat pada `anomali` tiap baris dan pada `validation_report.json`, lalu ditampilkan di `/data` dan pada komponen `TckOverview`.
- **Koordinat tidak ditebak.** `outreach_points.json` dan `partnership_points.json` mempertahankan status lokasi; UI memakai centroid provinsi skematik dengan label metodologis yang terlihat.
- **Data perorangan tidak pernah keluar.** Nama, NIP/NIM/NIU, kontak, dan seluruh nilai pemeriksaan Posbindu dibuang di tahap load atau clean. `03_validate.py` menolak proses bila salah satu kunci privat muncul di `src/data/derived/`.
- **Sesi Posbindu ganda didedup.** Satu lembar rekap menduplikasi sesi lain secara utuh; kunjungan dikunci pada pasangan (tanggal, peserta) sebelum nama dibuang.
- **Kategori Posbindu 2022–2025 dihitung ulang, bukan ditebak.** Sumber lama hanya mencatat angka; berkas 2026 mencatat angka sekaligus interpretasinya. Ambang dibaca balik dari pasangan tersebut dan diverifikasi terhadap label 2026 itu sendiri: tekanan darah, lingkar perut, asam urat, kolesterol, dan gula darah cocok 100%, IMT 273 dari 278 (lima sisanya baris yang labelnya bertentangan dengan angkanya sendiri di berkas asli). Ambangnya tinggal di `mappings/`, bukan di kode.
- **Dua sumber Posbindu disatukan per bulan, bukan per baris.** Digitasi arsip analog memegang 12 sesi bertanggal pasti; registri memegang bulan-bulan yang tidak pernah didigitasi — termasuk seluruh 2025. Registri hanya diterima untuk bulan yang tidak dicakup digitasi, sehingga kedua sumber tidak pernah menggambarkan sesi yang sama dan tidak ada pencocokan nama yang perlu dipercaya.
- **Terukur dan dinilai dibedakan.** Lingkar perut dan asam urat berambang beda per jenis kelamin, yang tidak pernah dicatat lembar digitasi. Kunjungan tanpa gender dihitung terukur tetapi tidak dinilai; keduanya diekspor agar penyebut persentase tetap jujur.

`build-service-worker.mjs` dijalankan setelah build untuk memasukkan seluruh output ber-hash ke precache. `check-build.mjs` memeriksa tautan internal, fragmen, nilai non-finit, format tahun, dan keberadaan setiap URL precache.
