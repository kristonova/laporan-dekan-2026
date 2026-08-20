# Pipeline data — Lima Tahun FMIPA

Jalankan dari root aplikasi:

```bash
npm run data
npm run validate:data
```

Urutan tahap:

1. `00_load.py` membaca seluruh file multi-part, menggabungkan, mendeduplikasi `Id`, dan menulis manifest asal data.
2. `01_clean.py` menormalisasi provinsi, memetakan departemen publikasi melalui ID Scopus, memulihkan pemisah ribuan skor SINTA, serta membuang kolom tingkat individu.
3. `02_aggregate.py` menghasilkan JSON kecil di `src/data/derived/` dan cermin unduhan yang sudah disanitasi di `public/data/`.
4. `03_validate.py` menguji jumlah part, angka jangkar PRD, 42 indikator TCK, arah indikator #27, monotonisitas triwulan, dan ketiadaan kunci privat.

Koordinat kegiatan pengabdian tidak ditebak. `outreach_points.json` mempertahankan `lat`/`lng` kosong dan status lokasi; UI memakai centroid provinsi skematik dengan label metodologis yang terlihat.

`build-service-worker.mjs` dijalankan setelah build untuk memasukkan seluruh output ber-hash ke precache. `check-build.mjs` memeriksa tautan internal, fragmen, nilai non-finit, format tahun, dan keberadaan setiap URL precache.
