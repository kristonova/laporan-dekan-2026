# Pembaruan visualisasi dan sumber · 5 September 2026

Boxplot dipilih untuk IPK S1 karena memperlihatkan pusat dan variasi distribusi per
program studi, dengan pilihan satu angkatan sebagai tampilan utama. Kotak P25–P75
dan median mengikuti definisi [NIST](https://www.itl.nist.gov/div898/handbook/eda/section3/boxplot.htm),
sedangkan whisker memakai pengamatan terjauh dalam batas 1,5 IQR.
Gabungan seluruh angkatan dihitung dari pengamatan asal, bukan median dari lima median.

[Observable dodge](https://observablehq.com/plot/transforms/dodge) menjelaskan beeswarm:
titik digeser pada sumbu lain untuk mengurangi tumpang tindih. Beeswarm tepat bila
pengamatan individual perlu dilihat; untuk ribuan IPK, titik akan padat dan memerlukan
publikasi nilai individual. Karena situs hanya mengeluarkan agregat, boxplot lebih sesuai.
Tidak dibuat beeswarm palsu dari kuartil atau data sintetis. IPK 2026 belum tersedia;
skala 0–4 tetap, dan nilai nol sumber dipertahankan.

Corong seleksi dan kunjungan Posbindu memakai batang horizontal dari titik nol yang
sama, dengan panjang proporsional terhadap jumlah tahap awal. Jumlah dan denominator
rasio dicetak di luar batang agar nilai kecil tetap terbaca. Selisih setiap tahap
diberi label tersendiri. Retensi Posbindu merupakan minimal jumlah kunjungan selama
periode registri; selisih tidak ditafsirkan sebagai kepastian peserta berhenti.

Grafik dana riset memakai viewBox lebih dekat dengan lebar tampil dan font sumbu
16px serta label nilai 17px pada koordinat grafik. Judul skala 15px di luar SVG.
Di layar sempit tersedia gulir horizontal agar teks tidak menyusut berlebihan.

Workbook asal pendidikan 2 September berisi 6.856 rekaman anonim lintas jenjang.
Sumber itu mengganti cakupan dan sekolah asal, serta menambah universitas asal S2/S3.
Data gender, alamat, jalur masuk, keluarga, status, dan IPK tetap memakai sumber lama
dengan label cakupan S1/non-gelar. Kedua sumber tidak ditautkan pada individu.
Grafik komposisi prodi memakai S1/non-gelar hanya dari daftar mahasiswa dan S2/S3
hanya dari workbook asal pendidikan, sehingga tidak menghitung ulang jenjang yang
sama antar-sumber. Satu grafik garis menampilkan angkatan 2021–2026; klik prodi
memfilter semua jenjang prodi tersebut, sementara pilihan jenjang membatasi
perbandingan. Proporsi memakai total angkatan pada jenjang terpilih dan penyebut
tidak berubah saat prodi difilter. Pilihan jumlah mempertahankan unit rekaman.

## Verifikasi

- `npm run data` dan `npm run validate:data`: lulus. Total jenjang dan angkatan,
  kelengkapan sekolah S1, batas statistik IPK, serta penyamaran sel kecil diperiksa.
- `npm run build`: lulus, tanpa error. Satu hint variabel `selectivityShrinking`
  yang sudah ada sebelumnya berada di luar perubahan ini.
- `node pipeline/check-build.mjs`: empat halaman, tautan internal, dan precache lulus.
- Chromium pada hasil build: 46 pemeriksaan filter lulus (enam pilihan IPK beserta
  tabelnya dan 28 kombinasi jenjang/angkatan institusi asal). Klik dan keyboard
  Tab/Enter diuji untuk angkatan; select jenjang dan angkatan diuji dengan kontrol asli.
- Tampilan 1440px dan 390px diperiksa untuk dana riset, seleksi, retensi, IPK, dan
  institusi asal. Lebar halaman tidak melebihi viewport. IPK pada ponsel memakai
  satu baris ringkas per prodi agar seluruh kotak tetap terlihat.
- Mode gelap IPK dan institusi asal diperiksa; konsol browser tanpa error.
