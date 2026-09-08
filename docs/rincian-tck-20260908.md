# Integrasi rincian TCK — 8 September 2026

Rincian masuk ke bagian yang telah membahas indikatornya. Beasiswa mendapat
satu bagian tersendiri pada pilar Mahasiswa & Akses. Tampilan memakai warna
UGM, label angka langsung, tombol jenjang/kategori, serta tabel dan unduhan.

| Sumber | Keluaran dan pemakaian | Cakupan |
| --- | --- | --- |
| Rincian #4a–4b | `tck_international`: negara, program/kegiatan, status bukti | 90 kredit + 108 nonkredit; rekaman, bukan orang unik |
| Rincian #8b1–8b3 | `tck_graduates`: satu titik per rekaman menurut semester, median, kuartil dan rentang per prodi | S1 150, S2 57, S3 35; daftar bukti khusus, bukan semua lulusan |
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

## Penyambungan ke halaman cerita

Audit lanjutan 8 September menemukan bahwa lima komponen rincian dan datasetnya
ada di repositori, tetapi belum diimpor atau dirender oleh `src/pages/index.astro`.
Komponen sekarang dipasang pada tujuh lokasi berikut; katalog `/data` juga
memuat kelima dataset rincian. Seluruh pipeline diregenerasi dan divalidasi;
angka agregat tidak berubah dari sumber yang tersedia.

| Bagian | Tautan | Visualisasi |
| --- | --- | --- |
| 4.3 | `#rincian-pengalaman-belajar` | MBKM dan jalur pascasarjana per prodi |
| 4.4 | `#profil-mahasiswa-asing` | Batang terbagi kredit/nonkredit menurut negara, pilihan jalur dan program |
| 4.5 | `#rincian-lama-studi` | Satu titik per rekaman kelulusan, median, pita 50% tengah, minimum–maksimum |
| 4.7 | `#profil-lulusan-jenjang` | Perbandingan tiga jenjang pada skala bulan yang sama, tren lima tahun, IPK, komposisi prodi |
| 4.7 | `#rincian-prestasi` | Komposisi kategori, departemen, hasil, dan daftar kegiatan yang dapat dicari |
| 5.2 | `#rincian-fasilitas-gedung` | Matriks gedung × jenis fasilitas |
| 6.4′ | `#beasiswa` | Pencarian 79 skema/periode dan sebaran penerima per prodi yang mengikuti filter |

Navigasi cepat setelah ringkasan TCK mengarah ke empat rincian utama. Angka
ringkasan fakultas pada beasiswa tetap utuh; subtotal skema, subtotal prodi, dan
persentase terhadap rekap fakultas berubah bersama mengikuti pilihan pembaca.
Label “rekaman tanpa negara asal” menggantikan label yang dapat terbaca sebagai
jumlah negara hilang. Mobilitas masuk dan keluar tidak dinarasikan sebagai arus
yang seimbang karena kedua daftar memiliki cakupan berbeda.

`npm run test:details` menguji cakupan seluruh skema serta rekonsiliasi filter
program studi, kelompok, pencarian, dan hasil kosong. Pemeriksaan build kini
memastikan tujuh lokasi **beserta komponen yang dirender** benar-benar ada pada
HTML hasil produksi, untuk menangkap kembali kasus komponen yang tidak terpasang.

Verifikasi 8 September: pipeline penuh dan pemeriksaan build lulus. Pemeriksaan
browser pada build produksi mencakup 14 pilihan panel, filter/pencarian/reset
beasiswa, unduhan CSV, lebar 1440/768/390 piksel, dan mode gelap. Tidak ada
kesalahan JavaScript atau pelebaran halaman pada ukuran yang diperiksa.

Rincian penelitian, kerja sama, dan SDM yang telah tercakup dalam dataset tematik
tidak dijumlah ulang dengan daftar TCK yang berpotensi tumpang tindih.
