# Integrasi rincian TCK — 8 September 2026

Rincian masuk ke bagian yang telah membahas indikatornya. Beasiswa mendapat
satu bagian tersendiri pada pilar Mahasiswa & Akses. Tampilan memakai warna
UGM, label angka langsung, tombol jenjang/kategori, serta tabel dan unduhan.

| Sumber | Keluaran dan pemakaian | Cakupan |
| --- | --- | --- |
| Rincian #4a–4b | `tck_international`: negara, program/kegiatan, status bukti | 90 kredit + 108 nonkredit; rekaman, bukan orang unik |
| Rincian #8b1–8b3 | `tck_graduates`: histogram semester, median, kuartil per prodi | S1 150, S2 57, S3 35; daftar bukti khusus, bukan semua lulusan |
| Rincian #9 | `tck_achievements`: jenis, departemen, tingkat, daftar kegiatan | 167 rekaman; ringkasan TCK 168 |
| PENERIMA BEASISWA 2026 / Rekapitulasi | `scholarships` lengkap + `scholarships_detail` | 703 penerima tabel; 79 skema aktif, sebelumnya hanya 15 diekspor |
| Rincian #8a dan #10 | `tck_supporting`: partisipasi per prodi | 603 MBKM, 44 jalur pascasarjana |
| Rincian #31 | `tck_supporting`: matriks gedung × fasilitas | 21 unit terinci; total tertulis 23 |
| Rekap profil lulusan yang sudah ada | Profil jenjang, tren bulan, IPK, prodi | Seluruh lulusan 2021/2022–2025/2026 |

## Keputusan data

- Baris detail wajib bernomor dan mempunyai label prodi/kegiatan berupa teks.
  Ini membuang rekap departemen bernomor di bagian bawah workbook, yang jika
  ikut terbaca akan menaikkan kredit 90 menjadi 94 dan pascasarjana 44 menjadi 48.
- Semester dipertahankan sebagaimana sumber. Pada sejumlah baris S2, kolom
  bulan menyalin IPK; kolom itu tidak digunakan untuk statistik. Tidak ada
  perkalian semester dengan enam untuk menebak masa studi bulanan.
- Dua nilai IPK S3 (46,2 dan 40,2) tidak valid dan dikeluarkan hanya dari statistik
  IPK; kedua rekaman tetap dihitung. Kelompok prodi kurang dari tiga tidak
  menerbitkan IPK maupun statistik lama studi.
- Masa studi rekap S1 dikonversi dari tahun+bulan ke bulan. S2/S3 2025/2026
  menggunakan rekap berbobot jumlah wisudawan yang sudah dihitung pipeline.
- Nama negara dan prodi diterjemahkan hanya bila padanannya jelas. “Hailand”
  tidak ditebak. Program tanpa jenjang eksplisit tetap tanpa jenjang.
- Kejuaraan tidak disatukan dengan publikasi/KKN. Judul kegiatan tetap memakai
  nama sumber; tidak ada penggabungan berdasarkan kemiripan nama.
- Beasiswa tetap memakai varian skema/angkatan/semester resmi. Pengelompokan
  KIP/UGM berdasarkan nama; kategori lainnya tidak menebak pemberi dana.
- CSV/JSON hanya memuat agregat. Nama orang, NIM/NIU, tanggal perorangan, dan
  tautan bukti tidak disimpan dalam data publik.
- Lokasi kiriman September kini berada di
  `data laporan dekan 2021-2026/Laporan Dekan 2026`; pipeline memakai lokasi ini
  dengan fallback lokasi `data ugm/Laporan Dekan 2026` untuk checkout lama.

## Regenerasi dan validasi

`npm run data` menjalankan agregasi rincian pada tahap 02. `npm run validate:data`
memeriksa jumlah terhadap sumber, rekonsiliasi seluruh kelompok, semester,
penahanan statistik kecil, IPK, cakupan 79 skema, serta ketiadaan kunci privat.
`npm run build` dan `node pipeline/check-build.mjs` memeriksa artefak web.

Verifikasi 8 September: pipeline penuh dan pemeriksaan build lulus. Pemeriksaan
browser pada build produksi mencakup 14 pilihan panel, filter/pencarian/reset
beasiswa, unduhan CSV, lebar 1440/768/390 piksel, dan mode gelap. Tidak ada
kesalahan JavaScript atau pelebaran halaman pada ukuran yang diperiksa.

Rincian penelitian, kerja sama, dan SDM yang telah tercakup dalam dataset tematik
tidak dijumlah ulang dengan daftar TCK yang berpotensi tumpang tindih.
