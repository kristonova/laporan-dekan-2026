export const ui = {
  reportTitle: "Lima Tahun FMIPA",
  reportKicker: "Laporan Dekan FMIPA UGM 2021–2026",
  table: "Tampilkan tabel lengkap",
  download: "Unduh CSV",
  source: "Sumber data",
  updated: "Pembaruan data",
  ongoing: "Tahun berjalan",
  next: "Lanjutkan membaca",
};

export const chapters = {
  position: {
    number: "Bagian I",
    title: "Potret Institusi & Capaian Kinerja",
    description:
      "Potret menyeluruh FMIPA UGM berdasarkan data resmi institusi: profil sivitas akademika, realisasi target perjanjian kinerja, serta pemetaan objektif atas berbagai aspek strategis fakultas.",
  },
  journey: {
    number: "Bagian II",
    title: "Rekam Jejak Transformasi Lima Tahun",
    description:
      "Capaian lima tahun dipahami secara utuh melalui rekam jejak perjalanannya. Melalui lima pilar tridharma, bagian ini mengulas perkembangan riset, kontribusi pengabdian kepada masyarakat, profil mahasiswa dari berbagai penjuru tanah air, hingga aspek-aspek yang terus ditingkatkan mutunya.",
  },
  handover: {
    number: "Bagian III",
    title: "Estafet Kepemimpinan & Agenda Strategis",
    description:
      "Laporan pertanggungjawaban ini meletakkan fondasi data yang tepercaya dan peta jalan yang jelas bagi kepemimpinan fakultas periode berikutnya untuk terus melangkah maju.",
  },
};

/**
 * Figures that move whenever a source workbook is refreshed. Any deck sentence
 * that quotes one is written as a function so the copy can never drift from the
 * data the same page renders.
 */
export interface SceneValues {
  lecturers: number;
  professors: number;
  professorShare: number;
  academicStaff: number;
  studyProgrammes: number;
  laboratories: number;
  activeStudents: number;
  tckTotal: number;
  tckAchieved: number;
  tckBehind: number;
  contributionAchieved: number;
  contributionTotal: number;
  welfareAchieved: number;
  welfareTotal: number;
  partnershipTotal: number;
  partnershipInternational: number;
  partnershipCountries: number;
  admissionsApplicants: number;
  admissionsApplicantsFirst: number;
  admissionsSeats: number;
  admissionsRegistered: number;
  admissionsTightnessFirst: number;
  admissionsTightnessLast: number;
  admissionsYieldFirst: number;
  admissionsYieldLast: number;
  admissionsFirstYear: number;
  admissionsLastYear: number;
  graduatesLatest: number;
  achievementsTotal: number;
  achievementsInternational: number;
  tracerRespondents: number;
  tracerWithinSixMonths: number;
  tracerTopSector: string;
  tracerBeforeGraduation: number;
  foreignCredit: number;
  foreignNonCredit: number;
  disabilityFacilities: number;
  disabilityTarget: number;
  posbinduVisits: number;
  posbinduSessions: number;
  posbinduRegistered: number;
  posbinduLecturers: number;
  posbinduStaff: number;
  posbinduTopRisk: string;
  posbinduFirstYear: number;
  posbinduLastYear: number;
  posbinduYearVisits: number;
  posbinduTensionFirst: number;
  posbinduTensionLast: number;
  studentsTotal: number;
  studentsMasters: number;
  studentsDoctoral: number;
  studentsAllNonDegree: number;
  studentsMasterOrigins: number;
  studentsDoctorOrigins: number;
  studentsUndergraduate: number;
  studentsProgrammes: number;
  studentsFirstYear: number;
  studentsLastYear: number;
  studentsNonDegreeFirst: number;
  studentsNonDegreeLast: number;
  studentsWomenShareFirst: number;
  studentsWomenShareLast: number;
  studentsWomenTopProgramme: string;
  studentsWomenTopShare: number;
  studentsWomenLowProgramme: string;
  studentsWomenLowShare: number;
  studentsProvincesFirst: number;
  studentsProvincesLast: number;
  studentsOutsideJavaPeak: number;
  studentsOutsideJavaPeakYear: number;
  studentsOutsideJavaLast: number;
  studentsTopPathway: string;
  studentsTopPathwayShare: number;
  studentsIup: number;
  studentsGuardianTop: string;
  studentsGuardianTopShare: number;
  studentsGuardianUnreported: number;
  studentsSchoolDiyShare: number;
  studentsSchoolUnique: number;
  studentsCohortGraduated: number;
  studentsCohortWithdrew: number;
  posbinduTopRiskShare: number;
  publicationsMappedShare: number;
  publicationsUnmapped: number;
  publicationsFirstYear: number;
  publicationsLastYear: number;
  topicClusters: number;
  collabCountries: number;
  collabFirstYear: number;
  collabFirstShare: number;
  collabLastYear: number;
  collabLastShare: number;
  researchAreas: number;
  researchAreasAtWorld: number;
  researchLeadArea: string;
  researchLeadFwci: number;
  openAccessFirstYear: number;
  openAccessFirstShare: number;
  openAccessLastYear: number;
  openAccessLastShare: number;
  openAccessGreenLatest: number;
  // Added with the September 2026 delivery: cooperation revenue, professor
  // regeneration, the vacant-position ratio, and the school memorandum network.
  revenueContracts: number;
  revenueTotal: number;
  revenueDpi: number;
  professorsThisPeriod: number;
  professorsThisPeriodShare: number;
  lecturersWithoutPosition: number;
  lecturersWithoutPositionShare: number;
  lecturersCertifiedShare: number;
  mouSchools: number;
  mouNewSchools: number;
  format: (value: number, digits?: number) => string;
}

type Deck = string | ((values: SceneValues) => string);

interface Scene {
  question: string;
  deck: Deck;
}

export const scenes = {
  "1.1": {
    question: "Bagaimana Profil Sumber Daya dan Sivitas FMIPA UGM Saat Ini?",
    deck: (v) =>
      `Aktivitas tridharma di FMIPA UGM dijalankan oleh ${v.format(v.lecturers)} dosen dan ${v.format(v.academicStaff)} tenaga kependidikan di empat departemen yang menaungi ${v.format(v.studyProgrammes)} program studi. Ekosistem pembelajaran dan riset ini didukung ${v.format(v.laboratories)} laboratorium terpadu serta melayani ${v.format(v.activeStudents)} mahasiswa sarjana aktif.`,
  },
  "1.2": {
    question: "Bagaimana Capaian Target Perjanjian Kinerja Fakultas?",
    deck: (v) =>
      `Hingga triwulan berjalan tahun 2026, sebanyak ${v.format(v.tckAchieved)} dari ${v.format(v.tckTotal)} indikator kinerja telah mencapai target. Pemenuhan ${v.format(v.tckBehind)} indikator lainnya terus diakselerasi menuju akhir tahun anggaran, dengan evaluasi dan catatan konteks data yang disajikan secara transparan.`,
  },
  "1.3": {
    question: "Bagaimana Sumber Daya Dikelola Menjadi Dampak Nyata Tridharma?",
    deck: "Alokasi pendanaan dan komitmen kerja sivitas diterjemahkan ke dalam hasil nyata: gagasan riset di laboratorium berkembang menjadi publikasi ilmiah bereputasi, program pengabdian masyarakat di berbagai daerah, serta manfaat langsung bagi kemaslahatan publik.",
  },
  "2.1": {
    question: "Bagaimana Perkembangan Dampak dan Sitasi Riset FMIPA di Tingkat Global?",
    deck: "Dampak riset sivitas meningkat signifikan dalam enam tahun terakhir: jumlah sitasi tahunan naik lebih dari tiga kali lipat, dari 4.129 sitasi pada 2019 hingga mencapai puncaknya 12.629 sitasi pada 2024. Data tahun 2025 masih terus bertambah seiring proses pemutakhiran berkala pada pangkalan data Scopus.",
  },
  "2.2": {
    question: "Bagaimana Produktivitas Publikasi Tersebar di Empat Departemen?",
    deck: (v) =>
      `Sebanyak ${v.format(v.publicationsMappedShare, 1)}% publikasi ilmiah periode ${v.publicationsFirstYear}–${v.publicationsLastYear} telah terpetakan ke departemen pengampu, baik melalui basis data fakultas maupun identifikasi profil Scopus para penulis. Sebanyak ${v.format(v.publicationsUnmapped)} artikel lainnya terus diverifikasi untuk melengkapi gambaran menyeluruh produktivitas riset fakultas.`,
  },
  "2.2p": {
    question: "Bagaimana Mutu dan Dampak Sitasi Riset FMIPA Dibandingkan Rata-Rata Dunia?",
    deck: (v) =>
      `Pertumbuhan kuantitas publikasi terus diimbangi dengan peningkatan mutu sitasi: dari ${v.format(v.researchAreas)} bidang ilmu yang tercatat, ${v.format(v.researchAreasAtWorld)} bidang telah mencapai atau melampaui rata-rata dunia (FWCI ≥ 1,00). Pada bidang dengan publikasi terbanyak, ${v.researchLeadArea} mencatat capaian tertinggi dengan FWCI ${v.format(v.researchLeadFwci, 2)}. Penguatan mutu dan rekognisi ilmiah ini menjadi prioritas strategis yang berjalan beriringan dengan produktivitas publikasi.`,
  },
  "2.3": {
    question: "Apa Saja Fokus dan Klaster Topik Riset Unggulan di FMIPA?",
    deck: (v) =>
      `Sebanyak ${v.format(v.topicClusters)} klaster topik riset menunjukkan peta keilmuan fakultas yang kaya dan interdisipliner—mencakup sains material, energi terbarukan, kecerdasan buatan, biosains, hingga teknologi sensor dan pemantauan lingkungan.`,
  },
  "2.4": {
    question: "Sejauh Mana Jangkauan Kolaborasi Riset Internasional Peneliti FMIPA?",
    deck: (v) =>
      `Jejaring kolaborasi ilmiah para peneliti FMIPA kini terhubung dengan mitra riset di ${v.format(v.collabCountries)} negara. Proporsi publikasi bersama mitra internasional meningkat dari ${v.format(v.collabFirstShare, 1)}% pada ${v.collabFirstYear} menjadi ${v.format(v.collabLastShare, 1)}% pada ${v.collabLastYear}.`,
  },
  "2.4p": {
    question: "Bagaimana Keterbukaan Akses Publik terhadap Publikasi Ilmiah FMIPA?",
    deck: (v) =>
      `Sekitar separuh publikasi ilmiah fakultas kini dapat diakses secara terbuka (Open Access): ${v.format(v.openAccessFirstShare, 1)}% pada ${v.openAccessFirstYear} dan ${v.format(v.openAccessLastShare, 1)}% pada ${v.openAccessLastYear}. Mayoritas artikel terbit melalui jalur Gold Open Access di pihak penerbit, sementara pemanfaatan repositori institusi (Green Open Access) baru mencatat ${v.format(v.openAccessGreenLatest)} artikel pada ${v.openAccessLastYear}—jalur mandiri yang ke depan terus didorong penguatannya oleh fakultas.`,
  },
  "2.5": {
    question: "Bagaimana Komposisi Jabatan Fungsional dan Kualifikasi Dosen FMIPA?",
    deck: (v) =>
      `Kapasitas kepakaran akademik terus bertumbuh: lebih dari seperempat dosen tetap aktif (${v.format(v.professorShare, 1)}% atau ${v.format(v.professors)} dari ${v.format(v.lecturers)} dosen) telah menduduki jabatan fungsional tertinggi sebagai Guru Besar.`,
  },
  "2.6": {
    question: "Agenda Strategis Apa yang Perlu Dipercepat pada Pilar Reputasi Akademik?",
    deck: "Seiring peningkatan produktivitas riset, langkah akselerasi difokuskan pada dua agenda utama: mendorong pemerataan publikasi antardepartemen serta memacu luaran publikasi mahasiswa program doktor bersama jejaring mitra global.",
  },
  "3.1": {
    question: "Bagaimana Perkembangan Pendanaan Riset Fakultas Selama Lima Tahun?",
    deck: "Perolehan dana riset tumbuh signifikan hingga mencapai puncaknya sebesar Rp74,91 miliar pada 2024, naik lebih dari dua puluh kali lipat dibandingkan posisi Rp3,30 miliar pada 2021. Pada 2025, perolehan dana tercatat sebesar Rp69,51 miliar, mencerminkan kapasitas pendanaan riset yang tetap kokoh dan berkelanjutan jauh di atas skala awal periode.",
  },
  "3.2": {
    question: "Di Mana Saja Sebaran Kegiatan Pengabdian kepada Masyarakat FMIPA UGM?",
    deck: "Aktivitas Pengabdian kepada Masyarakat (PkM) meningkat lebih dari empat kali lipat, dari 109 kegiatan pada 2021 menjadi 445 kegiatan per tahun. Sepanjang 2021–2025, sebanyak 921 dari 1.481 kegiatan telah terverifikasi dan dipetakan lokasinya di berbagai provinsi di seluruh tanah air.",
  },
  "3.3": {
    question: "Bagaimana Kontribusi Tridharma FMIPA terhadap Tujuan Pembangunan Berkelanjutan (SDGs)?",
    deck: "Kiprah tridharma sivitas berkontribusi nyata terhadap pencapaian agenda pembangunan berkelanjutan, terutama pada pilar industri dan inovasi (SDG 9), kesehatan dan kesejahteraan (SDG 3), konsumsi dan produksi bertanggung jawab (SDG 12), serta penyediaan air bersih (SDG 6), di samping penguatan pencatatan pada pilar-pilar SDGs lainnya.",
  },
  "3.4": {
    question: "Bagaimana Peran Jurnal Berkala Ilmiah FMIPA dalam Diseminasi Pengetahuan?",
    deck: "Empat jurnal berkala ilmiah yang dikelola FMIPA secara konsisten menjadi wadah diseminasi riset berkualitas dengan mempublikasikan 461 artikel terindeks bereputasi. Penyebarluasan hasil inovasi juga diperkuat melalui dokumentasi 115 liputan media massa yang terhimpun rapi sejak 2023.",
  },
  "3.5": {
    question: "Bagaimana Perkembangan Jejaring Kerja Sama Strategis FMIPA UGM?",
    deck: (v) =>
      `Sepanjang periode 2021–2026, FMIPA UGM menjalin ${v.format(v.partnershipTotal)} naskah kerja sama resmi. Sebanyak ${v.format(v.partnershipInternational)} dokumen di antaranya merupakan kolaborasi internasional yang menghubungkan fakultas dengan berbagai institusi mitra di ${v.format(v.partnershipCountries)} negara.`,
  },
  "3.5p": {
    question: "Berapa Nilai Ekonomi Kerja Sama dan Kontribusinya bagi Fakultas?",
    deck: (v) =>
      `Kemitraan tidak berhenti pada naskah perjanjian: sepanjang 2022–2026 tercatat ${v.format(v.revenueContracts)} kontrak kerja sama senilai ${v.format(v.revenueTotal, 2)} miliar rupiah, dengan ${v.format(v.revenueDpi, 2)} miliar rupiah kembali ke fakultas sebagai Dana Pengembangan Institusi.`,
  },
  "3.6": {
    question: "Program Apa yang Menjadi Prioritas Akselerasi pada Pilar Kontribusi?",
    deck: (v) =>
      `Pilar kontribusi terus mempercepat ketercapaian target indikator: saat ini ${v.format(v.contributionAchieved)} dari ${v.format(v.contributionTotal)} indikator telah terpenuhi pada triwulan berjalan. Fokus akselerasi diarahkan pada hilirisasi hasil riset ke masyarakat dan dunia industri, serta penyempurnaan pencatatan kegiatan berbasis SDGs.`,
  },
  "4.1": {
    question: "Di Sektor Mana Saja Lulusan FMIPA Mengembangkan Karier?",
    deck: (v) =>
      `Lulusan sains dan matematika membuktikan daya saing yang tinggi di dunia profesional. Survei penelusuran lulusan (tracer study) terhadap ${v.format(v.tracerRespondents)} alumni mencatat sektor ${v.tracerTopSector} sebagai penyerap terbanyak, diikuti sektor perbankan dan jasa keuangan, industri teknologi, serta dunia pendidikan dan riset.`,
  },
  "4.2": {
    question: "Berapa Lama Rata-Rata Masa Tunggu Kerja Lulusan FMIPA?",
    deck: (v) =>
      `Masa tunggu lulusan untuk memperoleh pekerjaan tergolong singkat: sebanyak ${v.format(v.tracerWithinSixMonths)} dari ${v.format(v.tracerRespondents)} responden telah bekerja dalam waktu kurang dari enam bulan setelah kelulusan. Bahkan, ${v.format(v.tracerBeforeGraduation)} orang di antaranya telah diterima bekerja sebelum resmi diwisuda.`,
  },
  "4.3": {
    question: "Bagaimana Kesiapan Karier Mahasiswa Dibina Selama Masa Studi?",
    deck: "Penguatan kompetensi di luar ruang kuliah berjalan aktif: partisipasi mahasiswa dalam program Merdeka Belajar Kampus Merdeka (MBKM) melampaui target tahunan fakultas, diperkaya dengan program percepatan studi (fast track), keikutsertaan kompetisi keilmuan, serta pembekalan karier profesional terstruktur.",
  },
  "4.4": {
    question: "Bagaimana Pelaksanaan Program Mobilitas Internasional Mahasiswa?",
    deck: (v) =>
      `Program mobilitas mahasiswa berlangsung dinamis dan dua arah: fakultas menyambut ${v.format(v.foreignCredit)} mahasiswa asing pada program berbobot sks (credit-earning) dan ${v.format(v.foreignNonCredit)} mahasiswa pada program non-kredit, sekaligus memfasilitasi mahasiswa FMIPA untuk menimba pengalaman akademik di luar negeri.`,
  },
  "4.5": {
    question: "Bagaimana Capaian Kelulusan Tepat Waktu di Seluruh Jenjang Studi?",
    deck: "Persentase kelulusan tepat waktu di jenjang Sarjana, Magister, maupun Doktor secara konsisten memenuhi target yang ditetapkan universitas, berkat pemantauan masa studi berkala dan pendampingan tugas akhir yang efektif.",
  },
  "4.6": {
    question: "Bagaimana Minat Pendaftar dan Keketatan Seleksi Mahasiswa Baru?",
    deck: (v) =>
      `Peminat program sarjana tumbuh dari ${v.format(v.admissionsApplicantsFirst)} pendaftar pada ${v.admissionsFirstYear} menjadi ${v.format(v.admissionsApplicants)} pada ${v.admissionsLastYear}. Dengan daya tampung ${v.format(v.admissionsSeats)} kursi, rasio keketatan seleksi berada pada kisaran 1 : ${v.format(v.admissionsTightnessLast, 1)} (dibandingkan 1 : ${v.format(v.admissionsTightnessFirst, 1)} pada awal periode). Komitmen calon mahasiswa juga sangat kuat, tecermin dari tingkat registrasi ulang yang mencapai ${v.format(v.admissionsYieldLast, 1)}%.`,
  },
  "4.7": {
    question: "Bagaimana Profil Kelulusan dan Raihan Prestasi Mahasiswa Setiap Tahun?",
    deck: (v) =>
      `Fakultas meluluskan ${v.format(v.graduatesLatest)} sarjana baru pada tahun akademik terakhir. Pada saat yang sama, mahasiswa FMIPA menorehkan ${v.format(v.achievementsTotal)} prestasi kejuaraan sejak 2022, termasuk ${v.format(v.achievementsInternational)} penghargaan di tingkat internasional.`,
  },
  "4.3p": {
    question: "Sejauh Mana Keterlibatan Mahasiswa Sarjana dalam Riset Dosen?",
    deck: "Keterlibatan mahasiswa dalam riset dosen menjadi sarana penguatan kompetensi nyata: sebanyak 182 judul penelitian telah melibatkan langsung mahasiswa sarjana sebagai asisten peneliti, dengan peningkatan partisipasi yang nyata pada kurun 2023–2024.",
  },
  "5.1": {
    question: "Bagaimana Perkembangan Pembinaan Karier dan Kualifikasi Dosen?",
    deck: (v) =>
      `Tata kelola SDM dan pengembangan karier staf menunjukkan capaian positif: ${v.format(v.welfareAchieved)} dari ${v.format(v.welfareTotal)} indikator kinerja telah memenuhi target, didukung oleh kelancaran usulan kenaikan jabatan fungsional dosen serta perolehan rekognisi kepakaran internasional.`,
  },
  "5.1p": {
    question: "Bagaimana Regenerasi Guru Besar Berlangsung Selama Lima Tahun?",
    deck: (v) =>
      `Regenerasi kepakaran berjalan pesat: ${v.format(v.professorsThisPeriod)} dari ${v.format(v.professors)} Guru Besar aktif (${v.format(v.professorsThisPeriodShare, 1)}%) menerima jabatannya pada periode kepemimpinan 2021–2026.`,
  },
  "5.1q": {
    question: "Sejauh Mana Jabatan Akademik dan Sertifikasi Dosen Terpenuhi?",
    deck: (v) =>
      `Sebanyak ${v.format(v.lecturersWithoutPosition)} dari ${v.format(v.lecturers)} dosen (${v.format(v.lecturersWithoutPositionShare, 2)}%) belum memiliki jabatan akademik—masih di bawah ambang 10%—sementara ${v.format(v.lecturersCertifiedShare, 1)}% dosen telah mengantongi sertifikat pendidik profesional.`,
  },
  "5.2": {
    question: "Bagaimana Kesiapan Fasilitas Kampus Inklusif dan Ramah Disabilitas?",
    deck: (v) =>
      `Komitmen mewujudkan lingkungan kampus yang inklusif diwujudkan melalui penyediaan ${v.format(v.disabilityFacilities)} unit fasilitas ramah disabilitas, melampaui target tahunan (${v.format(v.disabilityTarget)} unit). Penerapan standar fasilitas fisik yang ramah lingkungan dan aksesibel terus diperkuat berkoordinasi dengan universitas.`,
  },
  "5.3": {
    question: "Bagaimana Hasil Pemantauan Kesehatan Dosen dan Tenaga Kependidikan?",
    deck: (v) =>
      `Pemeriksaan kesehatan berkala melalui Posbindu HPU mencatat ${v.format(v.posbinduYearVisits)} kunjungan dosen dan tenaga kependidikan sepanjang lima tahun (${v.posbinduFirstYear}–${v.posbinduLastYear}). Parameter ${v.posbinduTopRisk.toLowerCase()} menjadi faktor risiko yang paling banyak teridentifikasi (${v.format(v.posbinduTopRiskShare)}% peserta), sementara proporsi peserta dengan risiko tekanan darah meningkat dari ${v.format(v.posbinduTensionFirst)}% menjadi ${v.format(v.posbinduTensionLast)}%, sehingga menuntut perhatian bersama melalui program promosi kesehatan kerja.`,
  },
  "6.1": {
    question: "Bagaimana Komposisi Mahasiswa FMIPA UGM Lintas Jenjang Pendidikan?",
    deck: (v) =>
      `Basis data akademik per 2 September 2026 mendokumentasikan riwayat ${v.format(v.studentsTotal)} mahasiswa dari enam angkatan (${v.studentsFirstYear}–${v.studentsLastYear}), mencakup ${v.format(v.studentsUndergraduate)} mahasiswa sarjana (S1), ${v.format(v.studentsMasters)} magister (S2), ${v.format(v.studentsDoctoral)} doktor (S3), serta ${v.format(v.studentsAllNonDegree)} peserta program non-gelar.`,
  },
  "6.2": {
    question: "Bagaimana Sebaran Geografis Daerah Asal Mahasiswa FMIPA UGM?",
    deck: (v) =>
      `Akses pendidikan di FMIPA UGM menjangkau putra-putri dari seluruh tanah air: daerah asal mahasiswa kini meluas dari ${v.format(v.studentsProvincesFirst)} menjadi ${v.format(v.studentsProvincesLast)} provinsi. Proporsi mahasiswa dari luar Pulau Jawa sempat menyentuh puncaknya sebesar ${v.format(v.studentsOutsideJavaPeak, 1)}% pada angkatan ${v.studentsOutsideJavaPeakYear}, dan berada di angka ${v.format(v.studentsOutsideJavaLast, 1)}% pada angkatan ${v.studentsLastYear}.`,
  },
  "6.3": {
    question: "Bagaimana Komposisi Gender Mahasiswa di Setiap Program Studi?",
    deck: (v) =>
      `Pada tingkat fakultas, perbandingan gender tergolong seimbang dengan proporsi mahasiswa perempuan sebesar ${v.format(v.studentsWomenShareLast, 1)}%. Pola peminatan bervariasi antardisiplin ilmu: Program Studi ${v.studentsWomenTopProgramme} mencatat proporsi perempuan tertinggi (${v.format(v.studentsWomenTopShare, 1)}%), sedangkan Program Studi ${v.studentsWomenLowProgramme} mencatat ${v.format(v.studentsWomenLowShare, 1)}%.`,
  },
  "6.4": {
    question: "Melalui Jalur Apa Saja Mahasiswa Masuk ke FMIPA UGM?",
    deck: (v) =>
      `Jalur seleksi ${v.studentsTopPathway} menjadi pintu masuk terbesar yang menyaring ${v.format(v.studentsTopPathwayShare, 1)}% mahasiswa baru. Di samping seleksi nasional berbasis prestasi (SNBP) dan tes (SNBT), kelas internasional (IUP) konsisten menerima sekitar ${v.format(v.studentsIup)} mahasiswa per angkatan, didampingi jalur afirmasi wilayah 3T dan alih program.`,
  },
  "6.5": {
    question: "Bagaimana Latar Belakang Profesi Orang Tua atau Wali Mahasiswa?",
    deck: (v) =>
      `Keberagaman latar belakang keluarga tecermin dari profesi orang tua/wali mahasiswa yang didominasi oleh ${v.studentsGuardianTop.toLowerCase()} (${v.format(v.studentsGuardianTopShare, 1)}%), disusul pegawai swasta dan aparatur sipil negara. Sebanyak ${v.format(v.studentsGuardianUnreported)} data belum merinci spesifikasi pekerjaan, sehingga catatan ini berfungsi sebagai potret keragaman latar belakang keluarga dan bukan ukuran kemampuan ekonomi.`,
  },
  "6.6": {
    question: "Dari Sekolah dan Perguruan Tinggi Mana Saja Mahasiswa Berasal?",
    deck: (v) =>
      `Jejaring institusi asal mahasiswa kini mencakup ${v.format(v.studentsSchoolUnique)} SMA/MA bagi mahasiswa sarjana, ${v.format(v.studentsMasterOrigins)} universitas asal bagi mahasiswa magister, serta ${v.format(v.studentsDoctorOrigins)} perguruan tinggi asal bagi mahasiswa doktor. Pemutakhiran basis data ini melengkapi informasi asal pendidikan untuk seluruh angkatan 2021–2026.`,
  },
  "6.6p": {
    question: "Seberapa Luas Jejaring Sekolah Mitra yang Baru Dibangun?",
    deck: (v) =>
      `Penandatanganan nota kesepahaman pada Juli 2026 menjangkau ${v.format(v.mouSchools)} sekolah, dan ${v.format(v.mouNewSchools)} di antaranya merupakan jejaring baru yang belum pernah mengirimkan mahasiswa pada enam angkatan terakhir.`,
  },
  "6.7": {
    question: "Bagaimana Perjalanan Kemajuan Studi Mahasiswa dari Masuk hingga Lulus?",
    deck: (v) =>
      `Perjalanan studi mahasiswa memperlihatkan ritme akademik yang teratur: setelah menempuh masa perkuliahan lima tahun, sebanyak ${v.format(v.studentsCohortGraduated)} mahasiswa angkatan ${v.studentsFirstYear} telah resmi menyandang gelar sarjana. Perbedaan median IPK antartahun angkatan merupakan hal wajar yang sejalan dengan tahapan semester dan penyelesaian tugas akhir yang sedang dijalani.`,
  },
  "7.1": {
    question: "Evaluasi dan Agenda Strategis yang Memerlukan Percepatan",
    deck: (v) =>
      `Sebagai wujud akuntabilitas, laporan ini memetakan secara terbuka ${v.format(v.tckBehind)} indikator yang perlu diakselerasi, penyelarasan integrasi data lulusan dan keselamatan kerja (K3L), serta langkah antisipatif untuk merawat keberlanjutan pendanaan riset ke depan.`,
  },
  "7.2": {
    question: "Estafet Kepemimpinan: Fondasi Data untuk Melangkah Maju",
    deck: "Rekam jejak capaian tridharma selama lima tahun telah terdokumentasi secara tertib, terverifikasi, dan transparan—menjadi modal berharga dan pijakan yang kokoh bagi kepemimpinan fakultas periode berikutnya untuk terus melangkah maju.",
  },
} satisfies Record<string, Scene>;

export type SceneKey = keyof typeof scenes;

/** Resolve a scene deck, running the volatile ones against the current data. */
export function deckOf(key: SceneKey, values: SceneValues): string {
  const { deck } = scenes[key] as Scene;
  return typeof deck === "function" ? deck(values) : deck;
}
