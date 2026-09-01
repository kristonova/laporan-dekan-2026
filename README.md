# Lima Tahun FMIPA

Implementasi web data story untuk Laporan Dekan FMIPA UGM 2026. Produk ini terdiri dari cerita panjang di `/`, katalog data dan metodologi di `/data`, serta deck layar penuh yang dapat dipakai tanpa internet di `/presentasi`.

## Menjalankan lokal

Prasyarat: Node.js 22.12+ dan Python 3.11+.

Pipeline dijalankan lewat virtual environment di `.venv/`; `npm run data` dan
`npm run validate:data` memilih interpreternya sendiri, jadi venv tidak perlu
diaktifkan manual.

```bash
npm install
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r pipeline/requirements.txt   # Windows
.venv/bin/python -m pip install -r pipeline/requirements.txt           # macOS/Linux
npm run data
npm run validate:data
npm run dev
```

Build produksi dan preview:

```bash
npm run build
npm run preview
```

Untuk menjalankan pipeline, validasi angka, type-check, build, pemeriksaan tautan internal, dan audit precache dalam satu perintah:

```bash
npm run verify
```

Set `PUBLIC_SITE_URL` ketika membangun untuk domain produksi agar canonical URL dan Open Graph image menjadi absolut. Gunakan `PUBLIC_BASE_PATH` bila situs dipasang di subpath:

```bash
PUBLIC_SITE_URL=https://contoh.fmipa.ugm.ac.id npm run build
PUBLIC_SITE_URL=https://contoh.github.io PUBLIC_BASE_PATH=/laporan-dekan-2026 npm run build
```

## Struktur utama

- `src/pages/index.astro` — 3 babak, 5 pilar, dan 36 scene termasuk scene pelengkap 4.3′.
- `src/pages/data.astro` — inventaris sumber, definisi, kualitas, konflik angka, dan unduhan data tersanitasi.
- `src/pages/presentasi.astro` — satu scene per layar; panah kiri/kanan atau klik untuk berpindah, `P` untuk catatan, `F` untuk layar penuh.
- `src/components/charts/` — grafik SVG/HTML yang dapat dipakai ulang, lengkap dengan tabel alternatif.
- `src/data/derived/` — keluaran agregat yang dipakai saat build.
- `public/data/` — cermin dataset tersanitasi untuk diunduh pembaca.
- `pipeline/` — tahap load, clean, aggregate, dan validate. Lihat [pipeline/README.md](pipeline/README.md).

## Memperbarui data

Timpa berkas sumber di direktori induk dengan versi terbaru—nama berkas dan struktur sheet dipertahankan—lalu jalankan:

```bash
npm run data
npm run validate:data
npm run build
```

Berkas Excel dibaca langsung, jadi tidak ada langkah konversi manual. Sumber yang dipakai:

| Sumber | Lokasi | Dipakai untuk |
| --- | --- | --- |
| Ekspor P2M (25 berkas CSV) | `data ugm/p2m/` | Sitasi, publikasi, riset, PkM, SDM, jurnal, media |
| `TCK 2026.xlsx` | `target_capaian_kinerja/tck_2026/` | 42 indikator kinerja beserta rincian per departemen |
| `RINCIAN TCK/` | `target_capaian_kinerja/tck_2026/` | Rujukan cek silang manual, tidak diekspor |
| Workbook LENTERA | `data ugm/kerjasama/` | Dokumen kerja sama 2021–2026 |
| Tabel akademik | `data ugm/akademik/` | Maba, mahasiswa aktif, lulusan, prestasi, beasiswa, akreditasi, exchange, tracer study |
| Daftar mahasiswa per angkatan (6 berkas) | `data ugm/akademik/daftar mahasiswa/` | Profil mahasiswa: asal provinsi, gender, jalur masuk, latar wali, sekolah asal, status akhir |
| Rekap Posbindu | `data ugm/health promotion university posbindu/` | Agregat Health Promoting University |

Pipeline memisahkan TCK 2026 dari data historis, menggabungkan berkas multi-part, mendeduplikasi `Id`, melakukan remap departemen publikasi melalui Scopus ID, dan hanya mengekspor agregat tanpa data tingkat individu. Validasi memeriksa 42 indikator TCK, angka jangkar PRD, arah indikator, satuan indikator persentase, jumlah dokumen kerja sama, kunci privat, ambang sel kecil pada agregat mahasiswa, serta rekonsiliasi registrasi antara daftar mahasiswa dan PROFIL MABA.

Tanggal penarikan data ditulis satu kali sebagai konstanta `SNAPSHOT` di `pipeline/utils.py`, diekspor ke `snapshot.json`, dan dipakai seluruh halaman—tidak ada tanggal yang ditulis manual di komponen.

## Keputusan data yang disengaja

- Capaian TCK adalah snapshot berjalan per 31 Agustus 2026 dan ditandai provisional. Angka berasal dari berkas Excel resmi, bukan transkripsi tangkapan layar.
- Status empat level diturunkan dari rasio capaian terhadap target kuartal (≥100% tercapai, ≥85% mendekati, ≥50% tertinggal), karena berkas sumber hanya membedakan tercapai/belum.
- Indikator persentase #5b dan #8b1–8b3 dinilai pada TW2. Kolom TW3-nya memuat cacah mahasiswa tanpa penyebut, sehingga persentase tidak direka; cacahnya tetap disimpan pada kolom `_cacah`.
- Capaian 1c dinormalisasi ke miliar rupiah karena berkas sumber mencampur rupiah penuh dengan miliar.
- Data Posbindu hanya disajikan sebagai hitungan kategori per sesi. Satu lembar rekap yang menduplikasi sesi lain didedup berdasarkan (tanggal, peserta) sebelum nama dibuang.
- Bidang kerja tracer study dinormalisasi dari 331 varian teks bebas menjadi 13 sektor melalui `pipeline/mappings/bidang_kerja.csv`.
- Lokasi 619 catatan pengabdian memang kosong. Koordinat tidak direka; visual memakai agregasi centroid provinsi di atas GeoJSON publik 38 provinsi dan memberi label metodologis yang terlihat.
- Batas peta berasal dari [AlfianAliM/Indonesia-GeoJSON](https://github.com/AlfianAliM/Indonesia-GeoJSON) (Peta Nusa / Laravel Nusa, MIT), lalu disederhanakan secara topologis untuk tampilan web. Berkas unduhan dan atribusinya tersedia di `public/data/`.
- Peta kolaborasi internasional memakai GeoJSON batas negara [Natural Earth Vector 1:110m](https://github.com/nvkelso/natural-earth-vector) (public domain). Properti dipangkas dan presisi koordinat dibulatkan untuk web tanpa mengubah sumber posisi titik kolaborasi.
- Keselamatan/PPKS/HSE, penyebut indikator persentase, dan anomali indikator bangunan hijau tetap ditampilkan sebagai gap, bukan diisi dengan asumsi. Tracer study dan masa tunggu kerja kini tersedia dan menggantikan placeholder sebelumnya.
- Berkas daftar mahasiswa memuat nama, NIM, alamat, nomor telepon, dan identitas wali. Kolom-kolom itu dibuang pada tahap `00_load.py` sehingga tidak pernah tertulis ke disk; hanya tabulasi silang yang diekspor. Sel yang memuat satu atau dua orang disamarkan menjadi `null`—bukan nol—dengan penanda `disamarkan`, karena satu mahasiswa pada satu provinsi, prodi, dan angkatan dapat dikenali kembali pada situs publik. `03_validate.py` menggagalkan build jika ada cacah di bawah tiga yang lolos.
- Jumlah mahasiswa sarjana per angkatan pada daftar mahasiswa cocok persis dengan kolom `registrasi` PROFIL MABA untuk 2022, 2023, 2024, dan 2026; hanya 2025 berselisih empat mahasiswa. Selisih itu ditampilkan pada tabel konflik `/data`, tidak didamaikan diam-diam.
- Nama jalur seleksi nasional berubah pada 2023. SNMPTN disatukan dengan SNBP dan SBMPTN dengan SNBT melalui `pipeline/mappings/jalur_masuk.csv`, agar garis waktu enam angkatan dapat dibandingkan.
- Pekerjaan wali dinormalisasi dari 175 varian teks bebas menjadi 11 kelompok melalui `pipeline/mappings/pekerjaan_wali.csv`. Karena 885 rekaman mengisinya dengan "lain-lain", tanda hubung, atau kosong, sebaran ini disajikan sebagai latar pekerjaan—bukan ukuran kemampuan ekonomi.
- Porsi "luar Jawa" hanya dihitung terhadap mahasiswa dengan provinsi Indonesia yang tercatat. Mahasiswa beralamat luar negeri dan yang provinsinya kosong dilaporkan terpisah, bukan dihitung sebagai luar Jawa.
- Sekolah asal tidak tercatat sama sekali pada angkatan 2021 dan 2022, sehingga scene 6.6 hanya mencakup 2023–2026 dan menyebutkan batas itu secara eksplisit.
- Semua grafik penting dapat dipahami tanpa interaksi dan memiliki tabel data alternatif untuk aksesibilitas.

## Offline dan deployment

Output bersifat statis. Service worker melakukan precache atas halaman, font, aset brand, dan dataset publik setelah kunjungan pertama. Untuk rapat tanpa jaringan, buka `/presentasi` sekali saat masih online dan pastikan semua slide sudah termuat sebelum berpindah jaringan.

Push ke branch `main` akan menjalankan workflow GitHub Pages di `.github/workflows/deploy.yml`. Ketika berjalan di GitHub Actions, konfigurasi build otomatis mengambil owner dan nama repository untuk membentuk URL project site `https://<owner>.github.io/<repository>/`; repository khusus `<owner>.github.io` otomatis tetap memakai root.

Untuk repository private, GitHub Pages memerlukan paket GitHub Pro, Team, atau Enterprise. Repository source boleh private, tetapi situs hasil Pages beserta seluruh berkas di `public/` tetap dapat diakses publik. Jangan menaruh data individu, credential, atau materi internal di `public/` maupun `src/data/derived/`.

Deploy manual ke host statis lain tetap dapat dilakukan dengan mengunggah isi `dist/`. Untuk domain sendiri di root, set `PUBLIC_SITE_URL` dan biarkan `PUBLIC_BASE_PATH` kosong.
