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
      "Potret menyeluruh FMIPA UGM berdasarkan data resmi institusi: profil sumber daya manusia, realisasi target perjanjian kinerja, serta pemetaan objektif atas berbagai capaian strategis fakultas.",
  },
  journey: {
    number: "Bagian II",
    title: "Rekam Jejak Transformasi Lima Tahun",
    description:
      "Capaian lima tahun dipahami secara utuh melalui perjalanan pembuktiannya. Melalui lima pilar tridharma, bagian ini mengulas lompatan riset, jangkauan pengabdian kepada masyarakat, profil mahasiswa dari seluruh penjuru nusantara, hingga penguatan tata kelola kelembagaan.",
  },
  handover: {
    number: "Bagian III",
    title: "Estafet Kepemimpinan & Agenda Strategis",
    description:
      "Laporan pertanggungjawaban ini meletakkan fondasi data yang sahih dan peta jalan yang jelas bagi kepemimpinan fakultas periode berikutnya untuk melangkah lebih jauh.",
  },
};

/**
 * Figures that move whenever a source workbook is refreshed. Any deck sentence
 * that quotes one is written as a function so the copy can never drift from the
 * data the same page renders.
 */
export interface SceneValues {
  citationPublications: number;
  citedPublications: number;
  citedShare: number;
  highlyCitedPublications: number;
  lecturers: number;
  professors: number;
  professorShare: number;
  academicStaff: number;
  studyProgrammes: number;
  laboratories: number;
  activeStudents: number;
  activeStudentPeriod: string;
  activeMasters: number;
  activeDoctoral: number;
  activePostgraduatePeriod: string;
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
    question: "Profil Sumber Daya dan Sivitas Akademika FMIPA UGM",
    deck: (v) =>
      `Denyut tridharma di FMIPA UGM digerakkan oleh ${v.format(v.lecturers)} dosen dan ${v.format(v.academicStaff)} tenaga kependidikan pada empat departemen yang menaungi ${v.format(v.studyProgrammes)} program studi. Ekosistem keilmuan ini diperkuat oleh ${v.format(v.laboratories)} laboratorium dan menjadi rumah belajar bagi ${v.format(v.activeStudents)} mahasiswa sarjana aktif pada semester ${v.activeStudentPeriod}. Pada jenjang pascasarjana, rekap semester ${v.activePostgraduatePeriod} mencatat ${v.format(v.activeMasters)} mahasiswa magister (S2) dan ${v.format(v.activeDoctoral)} mahasiswa doktor (S3) aktif.`,
  },
  "1.2": {
    question: "Realisasi Target Perjanjian Kinerja Fakultas",
    deck: (v) =>
      `Hingga triwulan berjalan tahun 2026, sebanyak ${v.format(v.tckAchieved)} dari ${v.format(v.tckTotal)} indikator kinerja telah melampaui atau memenuhi target. Sebanyak ${v.format(v.tckBehind)} indikator lainnya terus dipacu menjelang akhir tahun anggaran, dengan evaluasi capaian dan catatan konteks data yang disajikan secara transparan.`,
  },
  "1.3": {
    question: "Alur Transformasi: Dari Sumber Daya Menuju Dampak Nyata",
    deck: "Komitmen kerja sivitas dan dukungan pendanaan berbuah nyata di lapangan. Gagasan riset di laboratorium bertumbuh menjadi publikasi ilmiah bereputasi internasional, program pengabdian yang menjangkau masyarakat pelosok, serta kontribusi konkret bagi kemaslahatan publik.",
  },
  "2.1": {
    question: "Jangkauan Sitasi pada Karya Ilmiah FMIPA",
    deck: (v) =>
      `Dari ${v.format(v.citationPublications)} publikasi dalam ekspor SciVal, ${v.format(v.citedPublications)} karya (${v.format(v.citedShare, 1)}%) telah menerima setidaknya satu sitasi. Sebanyak ${v.format(v.highlyCitedPublications)} karya telah dirujuk sedikitnya 100 kali. Sebaran berikut memperlihatkan jangkauan rujukan pada seluruh portofolio publikasi yang tercatat.`,
  },
  "2.2": {
    question: "Peta Produktivitas Publikasi di Empat Departemen",
    deck: (v) =>
      `Sebanyak ${v.format(v.publicationsMappedShare, 1)}% publikasi ilmiah kurun ${v.publicationsFirstYear}–${v.publicationsLastYear} telah terpetakan ke departemen masing-masing, baik melalui basis data fakultas maupun profil Scopus para penulis. Sebanyak ${v.format(v.publicationsUnmapped)} publikasi lainnya belum memiliki atribusi departemen.`,
  },
  "2.2p": {
    question: "Dampak Sitasi per Bidang Ilmu terhadap Rata-Rata Dunia",
    deck: (v) =>
      `Dari ${v.format(v.researchAreas)} bidang keilmuan yang tercatat, ${v.format(v.researchAreasAtWorld)} bidang memiliki dampak sitasi setara atau di atas rata-rata dunia (FWCI ≥ 1,00). Bidang ${v.researchLeadArea} mencatat FWCI tertinggi, sebesar ${v.format(v.researchLeadFwci, 2)}. Perbandingan ini memperhitungkan perbedaan pola sitasi antarbidang.`,
  },
  "2.3": {
    question: "Klaster Riset Unggulan dan Keragaman Keilmuan",
    deck: (v) =>
      `Sebanyak ${v.format(v.topicClusters)} klaster riset memperlihatkan lanskap keilmuan fakultas yang kaya dan lintas disiplin—mulai dari sains material, energi terbarukan, kecerdasan artifisial, biosains, hingga teknologi sensor dan pemantauan lingkungan hidup.`,
  },
  "2.4": {
    question: "Jejaring Kolaborasi Riset Peneliti FMIPA di Panggung Internasional",
    deck: (v) =>
      `Jejaring ilmiah para peneliti FMIPA merambah mitra riset di ${v.format(v.collabCountries)} negara. Porsi karya ilmiah yang digarap bersama mitra internasional melonjak dari ${v.format(v.collabFirstShare, 1)}% pada ${v.collabFirstYear} menjadi ${v.format(v.collabLastShare, 1)}% pada ${v.collabLastYear}.`,
  },
  "2.4p": {
    question: "Keterbukaan Akses Publikasi Ilmiah (Open Access)",
    deck: (v) =>
      `Sekitar separuh dari karya ilmiah fakultas kini dapat diakses bebas oleh publik dunia: tercatat ${v.format(v.openAccessFirstShare, 1)}% pada ${v.openAccessFirstYear} dan ${v.format(v.openAccessLastShare, 1)}% pada ${v.openAccessLastYear}. Sebagian besar terbit melalui jalur Gold Open Access di pihak penerbit, sedangkan ${v.format(v.openAccessGreenLatest)} publikasi tercatat melalui jalur Green Open Access pada ${v.openAccessLastYear}.`,
  },
  "2.5": {
    question: "Struktur Kepakaran dan Jabatan Fungsional Dosen",
    deck: (v) =>
      `Kekuatan akademik fakultas bertumpu pada kualifikasi dosen yang kokoh. Lebih dari seperempat dosen (${v.format(v.professorShare, 1)}% atau ${v.format(v.professors)} dari ${v.format(v.lecturers)} dosen aktif) telah mengemban jabatan akademik tertinggi sebagai Guru Besar.`,
  },
  "2.6": {
    question: "Agenda Strategis Penguatan Reputasi Akademik",
    deck: "Seiring peningkatan produktivitas riset, langkah akselerasi diarahkan pada dua sasaran utama: pemerataan publikasi lintas departemen serta peningkatan luaran ilmiah mahasiswa program doktor bersama mitra penelitian global.",
  },
  "3.1": {
    question: "Pertumbuhan dan Keberlanjutan Dana Riset Fakultas",
    deck: "Perolehan dana penelitian melesat hingga mencapai puncaknya Rp74,91 miliar pada 2024—meningkat lebih dari dua puluh kali lipat dibandingkan Rp3,30 miliar pada 2021. Pada 2025, perolehan dana tercatat sebesar Rp69,51 miliar, menandakan kapasitas riset fakultas kini telah berada pada skala baru yang mapan dan berkesinambungan.",
  },
  "3.2": {
    question: "Jangkauan Pengabdian kepada Masyarakat di Berbagai Daerah Nusantara",
    deck: "Kegiatan Pengabdian kepada Masyarakat (PkM) bertambah lebih dari empat kali lipat, dari 109 kegiatan pada 2021 menjadi 445 kegiatan per tahun. Sepanjang 2021–2025, sebanyak 921 dari 1.481 kegiatan telah terverifikasi dan terpetakan di berbagai provinsi di seluruh Indonesia.",
  },
  "3.3": {
    question: "Kontribusi Nyata Tridharma pada Agenda Berkelanjutan (SDGs)",
    deck: "Kiprah tridharma sivitas berkontribusi langsung pada pencapaian Tujuan Pembangunan Berkelanjutan. Kontribusi terbesar terkonsentrasi pada industri dan inovasi (SDG 9), kesehatan dan kesejahteraan (SDG 3), konsumsi dan produksi bertanggung jawab (SDG 12), serta penyediaan air bersih (SDG 6), seraya terus memperkuat dokumentasi pada pilar SDGs lainnya.",
  },
  "3.4": {
    question: "Peran Jurnal Ilmiah Fakultas dalam Penyebarluasan Ilmu Pengetahuan",
    deck: "Empat jurnal berkala ilmiah yang dikelola FMIPA konsisten menjadi rujukan riset berkualitas dengan menerbitkan 461 artikel terindeks bereputasi. Selain itu, kiprah inovasi sivitas disuarakan ke ranah publik melalui 115 liputan media massa yang terdokumentasi rapi sejak 2023.",
  },
  "3.5": {
    question: "Penguatan Kemitraan Strategis Dalam dan Luar Negeri",
    deck: (v) =>
      `Sepanjang periode 2021–2026, FMIPA UGM telah menandatangani ${v.format(v.partnershipTotal)} naskah kerja sama resmi. Sebanyak ${v.format(v.partnershipInternational)} dokumen di antaranya merupakan kemitraan internasional yang menghubungkan fakultas dengan berbagai institusi terkemuka di ${v.format(v.partnershipCountries)} negara.`,
  },
  "3.5p": {
    question: "Nilai Kontrak Kemitraan dan Penerimaan Pengembangan Institusi",
    deck: (v) =>
      `Kemitraan membawa manfaat nyata bagi kemandirian fakultas. Sepanjang kurun 2022–2026 tercatat ${v.format(v.revenueContracts)} kontrak kerja sama dengan total nilai ${v.format(v.revenueTotal, 2)} miliar rupiah, yang menyumbang ${v.format(v.revenueDpi, 2)} miliar rupiah sebagai Dana Pengembangan Institusi (DPI).`,
  },
  "3.6": {
    question: "Prioritas Percepatan pada Pilar Kontribusi bagi Bangsa",
    deck: (v) =>
      `Dari pilar kontribusi, sebanyak ${v.format(v.contributionAchieved)} dari ${v.format(v.contributionTotal)} indikator telah terpenuhi pada triwulan berjalan. Fokus percepatan kini diarahkan pada hilirisasi hasil riset ke masyarakat dan dunia industri, serta penyempurnaan pencatatan kegiatan berbasis SDGs.`,
  },
  "4.1": {
    question: "Kiprah dan Daya Serap Alumni di Dunia Profesional",
    deck: (v) =>
      `Lulusan sains dan matematika membuktikan keluwesan dan daya saing tinggi di pasar kerja modern. Pelacakan alumni (tracer study) terhadap ${v.format(v.tracerRespondents)} responden mencatat sektor ${v.tracerTopSector} sebagai penyerap terbesar, disusul perbankan dan jasa keuangan, industri teknologi informasi, serta lembaga pendidikan dan penelitian.`,
  },
  "4.2": {
    question: "Kecepatan Keterserapan Kerja dan Singkatnya Masa Tunggu Alumni",
    deck: (v) =>
      `Alumni FMIPA tergolong sangat cepat terserap di dunia kerja. Sebanyak ${v.format(v.tracerWithinSixMonths)} dari ${v.format(v.tracerRespondents)} responden telah bekerja dalam kurun waktu kurang dari enam bulan setelah kelulusan. Bahkan, ${v.format(v.tracerBeforeGraduation)} lulusan telah diterima bekerja sebelum resmi diwisuda.`,
  },
  "4.3": {
    question: "Pembekalan Kesiapan Karier dan Pengalaman Belajar Mahasiswa",
    deck: "Kesiapan kerja mahasiswa diasah sejak dini di dalam maupun di luar kampus. Partisipasi mahasiswa dalam Merdeka Belajar Kampus Merdeka (MBKM) melampaui target tahunan fakultas, diperkaya oleh program percepatan studi (fast track), kompetisi keilmuan, serta pembekalan karier terstruktur.",
  },
  "4.4": {
    question: "Mobilitas Internasional Mahasiswa: Pertukaran Dua Arah",
    deck: (v) =>
      `Internasionalisasi berlangsung dinamis dan dua arah: fakultas menerima ${v.format(v.foreignCredit)} mahasiswa asing pada program perolehan SKS (credit-earning) dan ${v.format(v.foreignNonCredit)} mahasiswa pada program non-kredit, sekaligus mengantarkan mahasiswa FMIPA menimba pengalaman berharga di universitas mitra mancanegara.`,
  },
  "4.5": {
    question: "Tingkat Kelulusan Tepat Waktu di Jenjang Sarjana dan Pascasarjana",
    deck: "Tingkat kelulusan tepat waktu di jenjang Sarjana, Magister, maupun Doktor secara konsisten melampaui target perjanjian kinerja, buah dari pemantauan berkala kemajuan studi dan pendampingan tugas akhir yang intensif.",
  },
  "4.6": {
    question: "Tingginya Minat Pendaftar dan Keketatan Seleksi Mahasiswa Baru",
    deck: (v) =>
      `Minat terhadap program sarjana FMIPA terus menanjak, dari ${v.format(v.admissionsApplicantsFirst)} pendaftar pada ${v.admissionsFirstYear} menjadi ${v.format(v.admissionsApplicants)} pada ${v.admissionsLastYear}. Dengan daya tampung ${v.format(v.admissionsSeats)} kursi, rasio keketatan seleksi berada pada kisaran 1 : ${v.format(v.admissionsTightnessLast, 1)}. Tingkat keseriusan calon mahasiswa juga sangat tinggi, terlihat dari angka daftar ulang yang mencapai ${v.format(v.admissionsYieldLast, 1)}%.`,
  },
  "4.7": {
    question: "Profil Kelulusan dan Prestasi Membanggakan Mahasiswa",
    deck: (v) =>
      `Fakultas meluluskan ${v.format(v.graduatesLatest)} sarjana baru pada tahun akademik terakhir. Di samping ketuntasan akademik, mahasiswa FMIPA menorehkan ${v.format(v.achievementsTotal)} gelar kejuaraan sejak 2022, dengan ${v.format(v.achievementsInternational)} prestasi di antaranya diraih di panggung kompetisi internasional.`,
  },
  "4.3p": {
    question: "Keterlibatan Mahasiswa Sarjana dalam Payung Riset Dosen",
    deck: "Keterlibatan dalam riset dosen menjadi wahana pembelajaran autentik bagi mahasiswa. Sebanyak 182 judul penelitian telah melibatkan langsung mahasiswa sarjana sebagai anggota tim peneliti, dengan peningkatan partisipasi yang signifikan pada kurun 2023–2024.",
  },
  "5.1": {
    question: "Pembinaan Karier dan Peningkatan Kualifikasi Dosen",
    deck: (v) =>
      `Pengelolaan SDM dan jenjang karier tenaga pendidik membuahkan capaian menggembirakan: ${v.format(v.welfareAchieved)} dari ${v.format(v.welfareTotal)} indikator kinerja telah memenuhi target, ditopang oleh kelancaran kenaikan jabatan fungsional serta rekognisi kepakaran di tingkat dunia.`,
  },
  "5.1p": {
    question: "Akselerasi Regenerasi dan Pertumbuhan Jumlah Guru Besar",
    deck: (v) =>
      `Regenerasi kepakaran tertinggi berlangsung pesat: sebanyak ${v.format(v.professorsThisPeriod)} dari ${v.format(v.professors)} Guru Besar aktif (${v.format(v.professorsThisPeriodShare, 1)}%) resmi diangkat menjadi Guru Besar dalam masa kepemimpinan 2021–2026.`,
  },
  "5.1q": {
    question: "Pemenuhan Jabatan Fungsional Awal dan Sertifikasi Dosen",
    deck: (v) =>
      `Sebanyak ${v.format(v.lecturersWithoutPosition)} dari ${v.format(v.lecturers)} dosen (${v.format(v.lecturersWithoutPositionShare, 2)}%) tercatat sedang dalam proses pengusulan jabatan fungsional pertama—jauh di bawah batas toleransi 10%. Sementara itu, ${v.format(v.lecturersCertifiedShare, 1)}% dosen telah memperoleh sertifikat pendidik profesional.`,
  },
  "5.2": {
    question: "Mewujudkan Lingkungan Kampus yang Inklusif dan Ramah Disabilitas",
    deck: (v) =>
      `Komitmen terhadap kampus inklusif diwujudkan lewat pengadaan ${v.format(v.disabilityFacilities)} unit fasilitas ramah disabilitas, melampaui target tahunan fakultas (${v.format(v.disabilityTarget)} unit). Standardisasi fasilitas yang mudah diakses dan ramah lingkungan terus disempurnakan bersama universitas.`,
  },
  "5.3": {
    question: "Pemantauan Kesehatan Kerja Dosen dan Tenaga Kependidikan",
    deck: (v) =>
      `Pemeriksaan berkala melalui Posbindu HPU membukukan ${v.format(v.posbinduYearVisits)} kunjungan dosen dan tenaga kependidikan sepanjang lima tahun (${v.posbinduFirstYear}–${v.posbinduLastYear}). Temuan ${v.posbinduTopRisk.toLowerCase()} menjadi faktor risiko yang paling dominan (${v.format(v.posbinduTopRiskShare)}% peserta), sementara proporsi risiko tekanan darah naik dari ${v.format(v.posbinduTensionFirst)}% menjadi ${v.format(v.posbinduTensionLast)}%. Data ini menjadi landasan penting bagi fakultas untuk merancang program kesehatan kerja preventif yang berkesinambungan.`,
  },
  "6.1": {
    question: "Komposisi dan Dinamika Mahasiswa Lintas Jenjang Pendidikan",
    deck: (v) =>
      `Basis data akademik per 2 September 2026 mencatat riwayat ${v.format(v.studentsTotal)} mahasiswa dari enam angkatan (${v.studentsFirstYear}–${v.studentsLastYear}), yang terdiri atas ${v.format(v.studentsUndergraduate)} mahasiswa sarjana (S1), ${v.format(v.studentsMasters)} magister (S2), ${v.format(v.studentsDoctoral)} doktor (S3), serta ${v.format(v.studentsAllNonDegree)} peserta program non-gelar.`,
  },
  "6.2": {
    question: "Pemerataan Akses: Menjangkau Talenta dari Seluruh Penjuru Nusantara",
    deck: (v) =>
      `FMIPA UGM membuka pintu seluas-luasnya bagi putra-putri terbaik dari seluruh tanah air. Daerah asal mahasiswa meluas dari ${v.format(v.studentsProvincesFirst)} menjadi ${v.format(v.studentsProvincesLast)} provinsi. Proporsi mahasiswa asal luar Pulau Jawa mencapai puncaknya ${v.format(v.studentsOutsideJavaPeak, 1)}% pada angkatan ${v.studentsOutsideJavaPeakYear} dan berada di posisi ${v.format(v.studentsOutsideJavaLast, 1)}% pada angkatan ${v.studentsLastYear}.`,
  },
  "6.3": {
    question: "Keseimbangan Gender dan Pola Peminatan Mahasiswa",
    deck: (v) =>
      `Di tingkat fakultas, komposisi gender berada dalam keseimbangan yang sehat dengan proporsi mahasiswa perempuan sebesar ${v.format(v.studentsWomenShareLast, 1)}%. Pilihan bidang keilmuan memperlihatkan dinamika yang menarik: Program Studi ${v.studentsWomenTopProgramme} memiliki proporsi mahasiswi tertinggi (${v.format(v.studentsWomenTopShare, 1)}%), sedangkan Program Studi ${v.studentsWomenLowProgramme} berada pada angka ${v.format(v.studentsWomenLowShare, 1)}%.`,
  },
  "6.4": {
    question: "Ragam Pintu Masuk: Jalur Seleksi Mahasiswa Baru",
    deck: (v) =>
      `Jalur seleksi ${v.studentsTopPathway} menjadi pintu masuk utama yang menyerap ${v.format(v.studentsTopPathwayShare, 1)}% mahasiswa baru. Di samping seleksi nasional berbasis prestasi (SNBP) dan tes (SNBT), International Undergraduate Program (IUP) konsisten menerima sekitar ${v.format(v.studentsIup)} mahasiswa per angkatan, dilengkapi jalur afirmasi wilayah 3T dan alih program.`,
  },
  "6.5": {
    question: "Kemajemukan Latar Belakang Profesi Orang Tua dan Wali Mahasiswa",
    deck: (v) =>
      `Keberagaman latar belakang keluarga terlihat dari rumpun profesi orang tua/wali mahasiswa yang didominasi oleh sektor ${v.studentsGuardianTop.toLowerCase()} (${v.format(v.studentsGuardianTopShare, 1)}%), disusul karyawan swasta dan aparatur sipil negara (ASN). Sebanyak ${v.format(v.studentsGuardianUnreported)} data belum mencantumkan pekerjaan secara terperinci, sehingga catatan ini menyajikan potret keragaman sosial keluarga dan bukan tolok ukur kemampuan ekonomi.`,
  },
  "6.6": {
    question: "Jejaring Sekolah dan Perguruan Tinggi Asal Mahasiswa",
    deck: (v) =>
      `Jejaring institusi pendidikan asal mahasiswa mencakup ${v.format(v.studentsSchoolUnique)} SMA/MA bagi jenjang sarjana, ${v.format(v.studentsMasterOrigins)} universitas asal bagi jenjang magister, serta ${v.format(v.studentsDoctorOrigins)} perguruan tinggi bagi jenjang doktor. Pemutakhiran basis data ini berhasil melengkapi informasi asal sekolah dan kampus untuk seluruh angkatan 2021–2026.`,
  },
  "6.6p": {
    question: "Perluasan Jejaring Kemitraan dengan Sekolah Baru",
    deck: (v) =>
      `Penandatanganan nota kesepahaman (MoU) pada Juli 2026 merangkul ${v.format(v.mouSchools)} sekolah. Sebanyak ${v.format(v.mouNewSchools)} di antaranya merupakan jejaring mitra baru yang belum pernah mengirimkan lulusannya ke FMIPA dalam enam angkatan terakhir.`,
  },
  "6.7": {
    question: "Dinamika Perjalanan Studi Mahasiswa Menuju Kelulusan",
    deck: (v) =>
      `Perjalanan studi mahasiswa memperlihatkan kelancaran akademik yang teratur. Memasuki tahun kelima, sebanyak ${v.format(v.studentsCohortGraduated)} mahasiswa angkatan ${v.studentsFirstYear} telah resmi menyandang gelar sarjana. Perbedaan median IPK antarangkatan mencerminkan tahapan perkuliahan dan penyelesaian tugas akhir yang sedang ditempuh, bukan penurunan mutu akademik.`,
  },
  "7.1": {
    question: "Evaluasi Kinerja dan Agenda Strategis yang Memerlukan Akselerasi",
    deck: (v) =>
      `Sebagai wujud keterbukaan institusional, laporan ini memetakan secara jujur ${v.format(v.tckBehind)} indikator kinerja yang perlu dipacu, penguatan integrasi data lulusan dan sistem keselamatan kerja (K3L), serta langkah antisipatif demi menjaga keberlanjutan pendanaan riset di masa mendatang.`,
  },
  "7.2": {
    question: "Estafet Kepemimpinan: Pijakan Data yang Kokoh Menuju Masa Depan",
    deck: "Rekam jejak capaian tridharma selama lima tahun telah terdokumentasi secara tertib, sahih, dan terbuka. Dokumentasi ini menjadi warisan berharga sekaligus landasan yang kokoh bagi kepemimpinan fakultas periode berikutnya untuk terus melangkah maju membawa FMIPA UGM kian menjulang.",
  },
} satisfies Record<string, Scene>;

export type SceneKey = keyof typeof scenes;

/** Resolve a scene deck, running the volatile ones against the current data. */
export function deckOf(key: SceneKey, values: SceneValues): string {
  const { deck } = scenes[key] as Scene;
  return typeof deck === "function" ? deck(values) : deck;
}
