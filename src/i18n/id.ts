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
    title: "Potret & Capaian FMIPA Saat Ini",
    description:
      "Gambaran komprehensif berdasarkan basis data resmi: komposisi sivitas akademika, pencapaian indikator kinerja utama, serta aspek strategis yang terus diakselerasi per Agustus 2026.",
  },
  journey: {
    number: "Bagian II",
    title: "Rekam Jejak Transformasi Lima Tahun",
    description:
      "Data kinerja menjadi bermakna saat ditinjau sebagai ikhtiar berkelanjutan. Melalui lima pilar utama, tergambar lompatan capaian, dinamika pertumbuhan, profil mahasiswa yang dididik, serta ruang evaluasi ke depan.",
  },
  handover: {
    number: "Bagian III",
    title: "Estafet Kepemimpinan & Agenda Strategis",
    description:
      "Pertanggungjawaban yang transparan tidak hanya mendokumentasikan keberhasilan, melainkan juga menyerahkan peta kerja dan data dasar yang teruji bagi kepemimpinan berikutnya.",
  },
};

/**
 * Figures that move whenever a source workbook is refreshed. Any deck sentence
 * that quotes one is written as a function so the copy can never drift from the
 * data the same page renders.
 */
export interface SceneValues {
  lecturers: number;
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
  studentsTotal: number;
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
  format: (value: number, digits?: number) => string;
}

type Deck = string | ((values: SceneValues) => string);

interface Scene {
  question: string;
  deck: Deck;
}

export const scenes = {
  "1.1": {
    question: "Bagaimana Komposisi FMIPA Saat Ini?",
    deck: (v) =>
      `Empat departemen dan ${v.format(v.studyProgrammes)} program studi didukung oleh ${v.format(v.lecturers)} dosen, ${v.format(v.academicStaff)} tenaga kependidikan, ${v.format(v.laboratories)} laboratorium terpadu, serta ${v.format(v.activeStudents)} mahasiswa sarjana aktif.`,
  },
  "1.2": {
    question: "Bagaimana Ketercapaian terhadap Target Kinerja?",
    deck: (v) =>
      `Sebanyak ${v.format(v.tckAchieved)} dari ${v.format(v.tckTotal)} indikator telah memenuhi target triwulan berjalan, sementara ${v.format(v.tckBehind)} indikator lainnya masih dalam proses akselerasi—seluruhnya disajikan secara terbuka beserta catatan kualitas datanya.`,
  },
  "1.3": {
    question: "Alur Transformasi: Dari Sumber Daya Menuju Dampak",
    deck: "Dalam lima tahun terakhir, alokasi dana dan dedikasi tridharma bertransformasi menjadi riset unggulan, publikasi bereputasi, pengabdian masyarakat, dan dampak nyata bagi bangsa.",
  },
  "2.1": {
    question: "Bagaimana Pertumbuhan Sitasi dan Reputasi Riset?",
    deck: "Jumlah sitasi tahunan melonjak signifikan dari 4.129 (2019) menjadi 12.629 (2024); data 2025 masih terus bertambah seiring proses pemutakhiran berkala di Scopus.",
  },
  "2.2": {
    question: "Bagaimana Distribusi Publikasi Antardepartemen?",
    deck: "Pemetaan ulang berbasis ID Scopus berhasil mengidentifikasi afiliasi departemen untuk 94,2% publikasi periode 2020–2025, sementara 157 artikel lainnya tetap dicatat sebagai proses penelusuran.",
  },
  "2.3": {
    question: "Apa Saja Bidang dan Topik Riset Unggulan FMIPA?",
    deck: "Sebanyak 528 klaster topik memperlihatkan bentang riset yang luas dan interdisipliner, mulai dari sains material, energi terbarukan, kecerdasan artifisial, hingga biosains dan lingkungan.",
  },
  "2.4": {
    question: "Sejauh Mana Jejaring Kolaborasi Riset Internasional?",
    deck: "Jejaring kemitraan telah menjangkau peneliti di 61 negara. Proporsi publikasi kolaborasi internasional meningkat dari 18,4% pada 2021 menjadi 27,7% pada 2025.",
  },
  "2.5": {
    question: "Bagaimana Komposisi dan Jenjang Jabatan Dosen?",
    deck: (v) =>
      `Dari total ${v.format(v.lecturers)} dosen tetap pada data kepegawaian aktif, sebanyak 42 orang (20,7%) telah mengemban jabatan fungsional Guru Besar.`,
  },
  "2.6": {
    question: "Aspek Apa yang Perlu Ditingkatkan pada Reputasi Akademik?",
    deck: "Pemerataan produktivitas publikasi antarbidang masih perlu didorong, sejalan dengan penguatan publikasi mahasiswa doktor dan perluasan mitra riset internasional.",
  },
  "3.1": {
    question: "Berapa Besar Perolehan Dana Riset FMIPA?",
    deck: "Perolehan dana riset meningkat hingga 22,7 kali lipat, dari Rp3,30 miliar pada 2021 menjadi Rp74,91 miliar pada 2024, sebelum mengalami penyesuaian pada 2025.",
  },
  "3.2": {
    question: "Bagaimana Jangkauan Pengabdian kepada Masyarakat di Nusantara?",
    deck: "Aktivitas Pengabdian kepada Masyarakat (PkM) melonjak dari 109 menjadi 445 kegiatan per tahun. Sepanjang 2021–2025, sebanyak 921 dari 1.481 kegiatan telah terpetakan sebarannya di berbagai provinsi.",
  },
  "3.3": {
    question: "Bagaimana Kontribusi Riset terhadap Agenda SDGs Dunia?",
    deck: "Aktivitas tridharma terfokus kuat pada industri dan inovasi, kesehatan, konsumsi-produksi berkelanjutan, serta air bersih; integrasi pencatatan untuk beberapa pilar SDGs lainnya terus ditingkatkan.",
  },
  "3.4": {
    question: "Bagaimana Diseminasi Ilmu Melalui Jurnal Ilmiah?",
    deck: "Empat jurnal ilmiah terbitan FMIPA telah memuat 461 artikel terindeks. Sementara itu, dokumentasi paparan media massa mulai dihimpun secara terstruktur sejak 2023.",
  },
  "3.5": {
    question: "Seberapa Luas Jejaring Kemitraan yang Dibangun?",
    deck: (v) =>
      `Sebanyak ${v.format(v.partnershipTotal)} dokumen kerja sama ditandatangani sepanjang 2021–2026, ${v.format(v.partnershipInternational)} di antaranya bersama mitra luar negeri dari ${v.format(v.partnershipCountries)} negara.`,
  },
  "3.6": {
    question: "Tantangan Apa yang Dihadapi pada Pilar Kontribusi?",
    deck: (v) =>
      `Pilar ini menghadapi target kinerja paling menantang: ${v.format(v.contributionAchieved)} dari ${v.format(v.contributionTotal)} indikator telah memenuhi target triwulan berjalan, dengan prioritas akselerasi pada luaran tridharma dan pemberitaan ber-SDGs.`,
  },
  "4.1": {
    question: "Bagaimana Daya Serap dan Kiprah Lulusan FMIPA?",
    deck: (v) =>
      `Tracer study mencatat ${v.format(v.tracerRespondents)} responden lulusan; sektor ${v.tracerTopSector} menjadi tujuan karier terbesar, disusul sektor keuangan dan pendidikan.`,
  },
  "4.2": {
    question: "Berapa Rata-rata Masa Tunggu Kerja Lulusan?",
    deck: (v) =>
      `Sebanyak ${v.format(v.tracerWithinSixMonths)} dari ${v.format(v.tracerRespondents)} responden memperoleh pekerjaan dalam enam bulan setelah lulus, dan ${v.format(v.tracerBeforeGraduation)} di antaranya bahkan telah bekerja sebelum tanggal kelulusan.`,
  },
  "4.3": {
    question: "Bagaimana Kesiapan Karier Mahasiswa Sebelum Lulus?",
    deck: "Partisipasi mahasiswa dalam program MBKM melampaui target tahunan, didukung oleh peningkatan prestasi kompetisi, program akselerasi, serta perluasan jejaring karier profesional.",
  },
  "4.4": {
    question: "Bagaimana Capaian Internasionalisasi Mahasiswa Asing?",
    deck: (v) =>
      `Tercatat ${v.format(v.foreignCredit)} mahasiswa asing program credit-earning dan ${v.format(v.foreignNonCredit)} program non-kredit, yang terus dipacu menuju pemenuhan target akhir tahun.`,
  },
  "4.5": {
    question: "Bagaimana Tingkat Kelulusan Tepat Waktu Mahasiswa?",
    deck: "Persentase kelulusan tepat waktu ketiga jenjang melampaui target triwulan berjalan. Angka terkini yang sahih berasal dari Triwulan II karena kolom Triwulan III pada berkas sumber memuat cacah mahasiswa, bukan persentase.",
  },
  "4.6": {
    question: "Seberapa Ketat Seleksi Masuk dan Sekuat Apa Minat Calon Mahasiswa?",
    deck: (v) =>
      `Minat masuk menyusut dari ${v.format(v.admissionsApplicantsFirst)} pelamar pada ${v.admissionsFirstYear} menjadi ${v.format(v.admissionsApplicants)} pada ${v.admissionsLastYear}, sementara daya tampung justru bertambah menjadi ${v.format(v.admissionsSeats)} kursi—keketatan seleksi karena itu melonggar dari 1 : ${v.format(v.admissionsTightnessFirst, 1)} menjadi 1 : ${v.format(v.admissionsTightnessLast, 1)}. Sisi lain menguat: ${v.format(v.admissionsYieldLast, 1)}% yang diterima melakukan registrasi, naik dari ${v.format(v.admissionsYieldFirst, 1)}%.`,
  },
  "4.7": {
    question: "Bagaimana Profil Lulusan dan Prestasi Mahasiswa?",
    deck: (v) =>
      `Lulusan sarjana mencapai ${v.format(v.graduatesLatest)} orang pada tahun akademik terakhir, sementara ${v.format(v.achievementsTotal)} prestasi kompetisi tercatat sejak 2022 dengan ${v.format(v.achievementsInternational)} di antaranya pada tingkat internasional.`,
  },
  "4.3p": {
    question: "Seberapa Besar Keterlibatan Mahasiswa dalam Riset?",
    deck: "Sebanyak 182 judul riset tercatat secara aktif melibatkan mahasiswa Sarjana, dengan peningkatan keterlibatan tertinggi pada kurun waktu 2023–2024.",
  },
  "5.1": {
    question: "Bagaimana Pengembangan Karier dan Kualifikasi SDM?",
    deck: (v) =>
      `Sebanyak ${v.format(v.welfareAchieved)} dari ${v.format(v.welfareTotal)} indikator pilar kesejahteraan dan tata kelola telah memenuhi target triwulan berjalan, didorong oleh akselerasi kenaikan jabatan fungsional dan rekognisi internasional.`,
  },
  "5.2": {
    question: "Bagaimana Penguatan Fasilitas Kampus Inklusif dan Berkelanjutan?",
    deck: (v) =>
      `Penyediaan ${v.format(v.disabilityFacilities)} unit fasilitas ramah disabilitas telah melampaui target tahunan (${v.format(v.disabilityTarget)} unit). Sementara itu, verifikasi data implementasi green building terus dikoordinasikan bersama universitas.`,
  },
  "5.3": {
    question: "Bagaimana Penjaminan Kesehatan dan Ruang Aman Sivitas?",
    deck: (v) =>
      `Program Health Promoting University memeriksa ${v.format(v.posbinduLecturers)} kunjungan dosen dan ${v.format(v.posbinduStaff)} kunjungan tenaga kependidikan pada ${v.format(v.posbinduSessions)} sesi Posbindu sepanjang 2026. ${v.posbinduTopRisk} menjadi temuan terbanyak: ${v.format(v.posbinduTopRiskShare)}% peserta yang diperiksa berada pada ambang berisiko.`,
  },
  "6.1": {
    question: "Siapa yang Belajar di FMIPA?",
    deck: (v) =>
      `Sebanyak ${v.format(v.studentsTotal)} mahasiswa tercatat pada enam angkatan ${v.studentsFirstYear}\u2013${v.studentsLastYear}, ${v.format(v.studentsUndergraduate)} di antaranya menempuh ${v.format(v.studentsProgrammes)} program studi sarjana. Peserta non-gelar\u2014pertukaran masuk dan MBKM\u2014menyusut dari ${v.format(v.studentsNonDegreeFirst)} menjadi ${v.format(v.studentsNonDegreeLast)} orang.`,
  },
  "6.2": {
    question: "Dari Mana Mahasiswa FMIPA Berasal?",
    deck: (v) =>
      `Jangkauan penerimaan meluas dari ${v.format(v.studentsProvincesFirst)} menjadi ${v.format(v.studentsProvincesLast)} provinsi. Porsi mahasiswa dari luar Jawa memuncak pada ${v.format(v.studentsOutsideJavaPeak, 1)}% di angkatan ${v.studentsOutsideJavaPeakYear}, lalu kembali turun ke ${v.format(v.studentsOutsideJavaLast, 1)}% pada angkatan ${v.studentsLastYear}.`,
  },
  "6.3": {
    question: "Bagaimana Komposisi Perempuan dan Laki-laki?",
    deck: (v) =>
      `Porsi mahasiswa perempuan turun dari ${v.format(v.studentsWomenShareFirst, 1)}% pada angkatan ${v.studentsFirstYear} menjadi ${v.format(v.studentsWomenShareLast, 1)}% pada angkatan ${v.studentsLastYear}\u2014titik terendah enam tahun. Jurang terlebar justru antardisiplin: ${v.studentsWomenTopProgramme} ${v.format(v.studentsWomenTopShare, 1)}% perempuan, sedangkan ${v.studentsWomenLowProgramme} hanya ${v.format(v.studentsWomenLowShare, 1)}%.`,
  },
  "6.4": {
    question: "Melalui Pintu Mana Mahasiswa Masuk?",
    deck: (v) =>
      `${v.studentsTopPathway} menjadi pintu masuk terbesar dengan ${v.format(v.studentsTopPathwayShare, 1)}% dari seluruh mahasiswa tercatat. Jalur internasional IUP bertahan pada kisaran ${v.format(v.studentsIup)} mahasiswa per angkatan, sementara mobilitas masuk non-gelar menyusut tajam.`,
  },
  "6.5": {
    question: "Dari Latar Keluarga Seperti Apa?",
    deck: (v) =>
      `Pekerjaan wali terbanyak adalah ${v.studentsGuardianTop} (${v.format(v.studentsGuardianTopShare, 1)}%), diikuti karyawan swasta dan pegawai negeri sipil. Sebanyak ${v.format(v.studentsGuardianUnreported)} rekaman tidak menyebutkan pekerjaan, sehingga potret ini dibaca sebagai sebaran kasar\u2014bukan ukuran kesejahteraan.`,
  },
  "6.6": {
    question: "Dari Sekolah Mana dan Seberapa Beragam?",
    deck: (v) =>
      `Mahasiswa angkatan 2023\u20132026 berasal dari ${v.format(v.studentsSchoolUnique)} sekolah berbeda, namun ${v.format(v.studentsSchoolDiyShare, 1)}% di antaranya bersekolah di Daerah Istimewa Yogyakarta. Keberagaman keyakinan tercatat pada enam agama.`,
  },
  "6.7": {
    question: "Bagaimana Perjalanan Satu Angkatan?",
    deck: (v) =>
      `Lima tahun setelah masuk, ${v.format(v.studentsCohortGraduated)} mahasiswa angkatan ${v.studentsFirstYear} telah lulus dan ${v.format(v.studentsCohortWithdrew)} mengundurkan diri. Median IPK menurun pada angkatan yang lebih muda karena semester yang ditempuh masih sedikit, bukan karena mutu yang merosot.`,
  },
  "7.1": {
    question: "Evaluasi dan Agenda Akselerasi Kinerja",
    deck: (v) =>
      `Pemetaan terhadap ${v.format(v.tckBehind)} indikator yang memerlukan akselerasi, penguatan integrasi sistem data lulusan dan keselamatan, serta strategi antisipasi keberlanjutan pendanaan riset ke depan.`,
  },
  "7.2": {
    question: "Pijakan Data untuk Periode Kepemimpinan Berikutnya",
    deck: "Seluruh data capaian lima pilar kini terdokumentasi secara transparan sebagai basis data awal yang siap ditindaklanjuti dan dikembangkan oleh pimpinan fakultas selanjutnya.",
  },
} satisfies Record<string, Scene>;

export type SceneKey = keyof typeof scenes;

/** Resolve a scene deck, running the volatile ones against the current data. */
export function deckOf(key: SceneKey, values: SceneValues): string {
  const { deck } = scenes[key] as Scene;
  return typeof deck === "function" ? deck(values) : deck;
}
