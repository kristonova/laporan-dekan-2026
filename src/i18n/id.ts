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
    title: "Potret & Capaian Kinerja FMIPA",
    description:
      "Gambaran menyeluruh berbasis data resmi institusi: profil sivitas akademika, pencapaian target kinerja utama, serta aspek strategis yang terus diperkuat hingga Agustus 2026.",
  },
  journey: {
    number: "Bagian II",
    title: "Rekam Jejak Transformasi Lima Tahun",
    description:
      "Capaian kinerja bermakna saat ditinjau sebagai ikhtiar berkelanjutan. Melalui lima pilar utama, tergambar lompatan prestasi, dinamika riset dan pengabdian, profil mahasiswa, serta ruang evaluasi ke depan.",
  },
  handover: {
    number: "Bagian III",
    title: "Estafet Kepemimpinan & Agenda Strategis",
    description:
      "Pertanggungjawaban yang transparan tidak hanya mendokumentasikan capaian, melainkan juga meletakkan peta jalan dan basis data yang teruji bagi kepemimpinan periode berikutnya.",
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
    question: "Bagaimana Komposisi dan Struktur FMIPA Saat Ini?",
    deck: (v) =>
      `Empat departemen dan ${v.format(v.studyProgrammes)} program studi ditopang oleh ${v.format(v.lecturers)} dosen, ${v.format(v.academicStaff)} tenaga kependidikan, ${v.format(v.laboratories)} laboratorium terpadu, serta ${v.format(v.activeStudents)} mahasiswa sarjana aktif.`,
  },
  "1.2": {
    question: "Bagaimana Ketercapaian Target Kinerja Fakultas?",
    deck: (v) =>
      `Sebanyak ${v.format(v.tckAchieved)} dari ${v.format(v.tckTotal)} indikator telah memenuhi target berjalan, sementara ${v.format(v.tckBehind)} indikator lainnya terus diakselerasi pemenuhannya—seluruhnya disajikan secara transparan beserta catatan teknis datanya.`,
  },
  "1.3": {
    question: "Alur Transformasi: Dari Sumber Daya Menuju Dampak Nyata",
    deck: "Dalam lima tahun terakhir, alokasi pendanaan dan komitmen tridharma bertransformasi secara berkelanjutan menjadi riset unggulan, publikasi bereputasi, program pengabdian, dan manfaat nyata bagi bangsa.",
  },
  "2.1": {
    question: "Bagaimana Lompatan Sitasi dan Reputasi Riset Global?",
    deck: "Jumlah sitasi tahunan melonjak lebih dari tiga kali lipat, dari 4.129 sitasi (2019) menjadi 12.629 sitasi (2024); data 2025 masih terus bertambah seiring proses pemutakhiran berkala di Scopus.",
  },
  "2.2": {
    question: "Bagaimana Distribusi Publikasi Ilmiah Antardepartemen?",
    deck: "Pemetaan berbasis ID Scopus berhasil mengidentifikasi afiliasi departemen untuk 94,2% artikel ilmiah periode 2020–2025, sementara 157 artikel lainnya tetap dicatat dan ditelusuri secara berkelanjutan.",
  },
  "2.3": {
    question: "Apa Saja Bidang dan Topik Riset Unggulan di FMIPA?",
    deck: "Sebanyak 528 klaster topik memperlihatkan cakupan riset yang luas dan interdisipliner, mulai dari sains material, energi terbarukan, kecerdasan buatan, hingga biosains dan pemantauan lingkungan.",
  },
  "2.4": {
    question: "Sejauh Mana Jangkauan Kolaborasi Riset Internasional?",
    deck: "Jejaring kemitraan telah menjangkau peneliti di 61 negara. Proporsi publikasi bersama mitra internasional meningkat dari 18,4% pada 2021 menjadi 27,7% pada 2025.",
  },
  "2.5": {
    question: "Bagaimana Komposisi Jenjang Jabatan Fungsional Dosen?",
    deck: (v) =>
      `Dari total ${v.format(v.lecturers)} dosen tetap aktif, sebanyak 42 orang (20,7%) telah mengemban jabatan fungsional Guru Besar.`,
  },
  "2.6": {
    question: "Aspek Apa yang Menjadi Fokus Penguatan Reputasi Akademik?",
    deck: "Pemerataan produktivitas publikasi antardepartemen terus didorong, diiringi peningkatan publikasi mahasiswa program doktor dan perluasan jejaring riset internasional.",
  },
  "3.1": {
    question: "Berapa Besar Perolehan Dana Riset FMIPA?",
    deck: "Perolehan dana riset melonjak hingga 22,7 kali lipat, dari Rp3,30 miliar pada 2021 menjadi puncaknya Rp74,91 miliar pada 2024, sebelum mengalami penyesuaian pada 2025.",
  },
  "3.2": {
    question: "Bagaimana Jangkauan Pengabdian kepada Masyarakat di Nusantara?",
    deck: "Kegiatan Pengabdian kepada Masyarakat (PkM) meningkat pesat dari 109 menjadi 445 kegiatan per tahun. Sepanjang 2021–2025, sebanyak 921 dari 1.481 kegiatan telah terpetakan sebarannya di berbagai provinsi.",
  },
  "3.3": {
    question: "Bagaimana Kontribusi Riset terhadap Agenda Berkelanjutan (SDGs)?",
    deck: "Kegiatan tridharma berkontribusi kuat pada pilar industri dan inovasi, kesehatan, konsumsi-produksi bertanggung jawab, serta air bersih; integrasi pencatatan untuk pilar SDGs lainnya terus diperluas.",
  },
  "3.4": {
    question: "Bagaimana Diseminasi Ilmu Melalui Jurnal Berkala Ilmiah?",
    deck: "Empat jurnal ilmiah terbitan FMIPA telah mempublikasikan 461 artikel terindeks bereputasi. Selain itu, liputan inovasi di media massa mulai dihimpun secara terstruktur sejak 2023.",
  },
  "3.5": {
    question: "Seberapa Luas Jejaring Kemitraan Strategis yang Dibangun?",
    deck: (v) =>
      `Sebanyak ${v.format(v.partnershipTotal)} dokumen kerja sama disepakati sepanjang 2021–2026, dengan ${v.format(v.partnershipInternational)} dokumen di antaranya melibatkan mitra luar negeri dari ${v.format(v.partnershipCountries)} negara.`,
  },
  "3.6": {
    question: "Tantangan Apa yang Menjadi Prioritas pada Pilar Kontribusi?",
    deck: (v) =>
      `Pilar ini memiliki target paling dinamis: ${v.format(v.contributionAchieved)} dari ${v.format(v.contributionTotal)} indikator telah memenuhi target triwulan berjalan, dengan prioritas percepatan pada hilirisasi luaran tridharma dan publikasi capaian SDGs.`,
  },
  "4.1": {
    question: "Bagaimana Daya Serap dan Kiprah Karier Lulusan FMIPA?",
    deck: (v) =>
      `Survei penelusuran lulusan (tracer study) terhadap ${v.format(v.tracerRespondents)} responden mencatat sektor ${v.tracerTopSector} sebagai bidang kerja utama, disusul sektor keuangan dan pendidikan-riset.`,
  },
  "4.2": {
    question: "Berapa Rata-rata Masa Tunggu Kerja Lulusan?",
    deck: (v) =>
      `Sebanyak ${v.format(v.tracerWithinSixMonths)} dari ${v.format(v.tracerRespondents)} responden memperoleh pekerjaan dalam waktu enam bulan setelah lulus, dan ${v.format(v.tracerBeforeGraduation)} orang di antaranya bahkan telah bekerja sebelum resmi diwisuda.`,
  },
  "4.3": {
    question: "Bagaimana Kesiapan Karier Mahasiswa Sebelum Lulus?",
    deck: "Partisipasi mahasiswa dalam program MBKM melampaui target tahunan, diperkuat oleh deretan prestasi kompetisi, program fast track, serta perluasan jejaring karier profesional.",
  },
  "4.4": {
    question: "Bagaimana Capaian Internasionalisasi Mahasiswa?",
    deck: (v) =>
      `Tercatat ${v.format(v.foreignCredit)} mahasiswa asing mengikuti program credit-earning dan ${v.format(v.foreignNonCredit)} mahasiswa pada program non-kredit, yang terus dipacu menuju pemenuhan target akhir tahun.`,
  },
  "4.5": {
    question: "Bagaimana Tingkat Kelulusan Tepat Waktu Mahasiswa?",
    deck: "Persentase kelulusan tepat waktu di jenjang Sarjana, Magister, maupun Doktor melampaui target berjalan. Evaluasi mengacu pada data Triwulan II yang lengkap persentasenya, mengingat pencatatan Triwulan III pada dokumen sumber masih berupa jumlah orang.",
  },
  "4.6": {
    question: "Bagaimana Dinamika Seleksi Masuk dan Minat Calon Mahasiswa?",
    deck: (v) =>
      `Jumlah pendaftar bergerak dari ${v.format(v.admissionsApplicantsFirst)} orang pada ${v.admissionsFirstYear} menjadi ${v.format(v.admissionsApplicants)} orang pada ${v.admissionsLastYear}, diiringi perluasan daya tampung menjadi ${v.format(v.admissionsSeats)} kursi sehingga rasio keketatan seleksi menjadi 1 : ${v.format(v.admissionsTightnessLast, 1)} (dari sebelumnya 1 : ${v.format(v.admissionsTightnessFirst, 1)}). Komitmen studi tetap tinggi dengan ${v.format(v.admissionsYieldLast, 1)}% calon mahasiswa yang diterima melakukan registrasi ulang (naik dari ${v.format(v.admissionsYieldFirst, 1)}%).`,
  },
  "4.7": {
    question: "Bagaimana Profil Lulusan dan Prestasi Mahasiswa?",
    deck: (v) =>
      `Jumlah lulusan sarjana mencapai ${v.format(v.graduatesLatest)} orang pada tahun akademik terakhir, sementara ${v.format(v.achievementsTotal)} prestasi kompetisi diraih mahasiswa sejak 2022 dengan ${v.format(v.achievementsInternational)} capaian di tingkat internasional.`,
  },
  "4.3p": {
    question: "Seberapa Besar Keterlibatan Mahasiswa dalam Riset Dosen?",
    deck: "Sebanyak 182 judul riset tercatat secara aktif melibatkan mahasiswa Sarjana sebagai asisten peneliti, dengan peningkatan tertinggi pada kurun waktu 2023–2024.",
  },
  "5.1": {
    question: "Bagaimana Pengembangan Karier dan Kualifikasi SDM?",
    deck: (v) =>
      `Sebanyak ${v.format(v.welfareAchieved)} dari ${v.format(v.welfareTotal)} indikator pilar tata kelola dan kesejahteraan telah memenuhi target berjalan, didorong oleh percepatan kenaikan jabatan akademik dan perolehan rekognisi internasional.`,
  },
  "5.2": {
    question: "Bagaimana Penguatan Fasilitas Kampus Inklusif dan Berkelanjutan?",
    deck: (v) =>
      `Penyediaan ${v.format(v.disabilityFacilities)} unit fasilitas ramah disabilitas telah melampaui target tahunan (${v.format(v.disabilityTarget)} unit). Sementara itu, verifikasi data penerapan gedung ramah lingkungan (green building) terus dikoordinasikan bersama universitas.`,
  },
  "5.3": {
    question: "Bagaimana Penjaminan Kesehatan dan Ruang Aman Sivitas?",
    deck: (v) =>
      `Program Health Promoting University mencatat ${v.format(v.posbinduLecturers)} pemeriksaan dosen dan ${v.format(v.posbinduStaff)} pemeriksaan tenaga kependidikan dalam ${v.format(v.posbinduSessions)} sesi Posbindu sepanjang 2026. Parameter ${v.posbinduTopRisk} menjadi temuan utama, dengan ${v.format(v.posbinduTopRiskShare)}% peserta berada pada kategori berisiko.`,
  },
  "6.1": {
    question: "Siapa yang Belajar di FMIPA UGM?",
    deck: (v) =>
      `Sebanyak ${v.format(v.studentsTotal)} mahasiswa tercatat dalam enam angkatan (${v.studentsFirstYear}\u2013${v.studentsLastYear}), dengan ${v.format(v.studentsUndergraduate)} orang di antaranya menempuh studi di ${v.format(v.studentsProgrammes)} program sarjana. Sementara itu, peserta program non-gelar (pertukaran mahasiswa dan MBKM) tercatat ${v.format(v.studentsNonDegreeLast)} orang.`,
  },
  "6.2": {
    question: "Dari Mana Saja Wilayah Asal Mahasiswa FMIPA?",
    deck: (v) =>
      `Jangkauan asal daerah mahasiswa meluas dari ${v.format(v.studentsProvincesFirst)} menjadi ${v.format(v.studentsProvincesLast)} provinsi. Proporsi mahasiswa dari luar Jawa sempat mencapai puncaknya sebesar ${v.format(v.studentsOutsideJavaPeak, 1)}% pada angkatan ${v.studentsOutsideJavaPeakYear}, dan berada di angka ${v.format(v.studentsOutsideJavaLast, 1)}% pada angkatan ${v.studentsLastYear}.`,
  },
  "6.3": {
    question: "Bagaimana Komposisi Gender Mahasiswa Antarprogram Studi?",
    deck: (v) =>
      `Proporsi mahasiswa perempuan berada di angka ${v.format(v.studentsWomenShareLast, 1)}% pada angkatan ${v.studentsLastYear}, dibandingkan ${v.format(v.studentsWomenShareFirst, 1)}% pada angkatan ${v.studentsFirstYear}. Variasi terlihat antarbidang keilmuan: Program Studi ${v.studentsWomenTopProgramme} memiliki proporsi perempuan tertinggi (${v.format(v.studentsWomenTopShare, 1)}%), sedangkan ${v.studentsWomenLowProgramme} berada di angka ${v.format(v.studentsWomenLowShare, 1)}%.`,
  },
  "6.4": {
    question: "Bagaimana Sebaran Jalur Masuk Penerimaan Mahasiswa?",
    deck: (v) =>
      `Jalur ${v.studentsTopPathway} menjadi pintu masuk terbesar dengan kontribusi ${v.format(v.studentsTopPathwayShare, 1)}% dari total mahasiswa. Jalur kelas internasional (IUP) stabil di kisaran ${v.format(v.studentsIup)} mahasiswa per angkatan, didampingi jalur seleksi nasional dan afirmasi.`,
  },
  "6.5": {
    question: "Bagaimana Profil Latar Belakang Keluarga Mahasiswa?",
    deck: (v) =>
      `Latar belakang pekerjaan orang tua/wali didominasi oleh ${v.studentsGuardianTop} (${v.format(v.studentsGuardianTopShare, 1)}%), disusul karyawan swasta dan pegawai negeri sipil. Sebanyak ${v.format(v.studentsGuardianUnreported)} data tidak mencantumkan pekerjaan, sehingga informasi ini dibaca sebagai gambaran umum dan bukan ukuran kemampuan ekonomi keluarga.`,
  },
  "6.6": {
    question: "Bagaimana Sebaran Sekolah Asal dan Keberagaman Mahasiswa?",
    deck: (v) =>
      `Mahasiswa angkatan 2023\u20132026 berasal dari ${v.format(v.studentsSchoolUnique)} sekolah menengah, dengan ${v.format(v.studentsSchoolDiyShare, 1)}% di antaranya menyelesaikan studi di Daerah Istimewa Yogyakarta. Sivitas mahasiswa juga mencerminkan keberagaman latar belakang keyakinan.`,
  },
  "6.7": {
    question: "Bagaimana Dinamika Perjalanan Studi Satu Angkatan?",
    deck: (v) =>
      `Setelah lima tahun masa studi, sebanyak ${v.format(v.studentsCohortGraduated)} mahasiswa angkatan ${v.studentsFirstYear} telah menyelesaikan studi (lulus) dan ${v.format(v.studentsCohortWithdrew)} mahasiswa mengundurkan diri. Perbedaan median IPK antarangkatan dipengaruhi oleh jumlah semester yang telah ditempuh dan belum mencerminkan capaian kelulusan akhir.`,
  },
  "7.1": {
    question: "Evaluasi Capaian dan Agenda Akselerasi Kinerja",
    deck: (v) =>
      `Pemetaan komprehensif terhadap ${v.format(v.tckBehind)} indikator yang memerlukan percepatan, penguatan integrasi sistem data lulusan dan keselamatan kerja, serta strategi menjaga kesinambungan pendanaan riset ke depan.`,
  },
  "7.2": {
    question: "Pijakan Data bagi Kepemimpinan Periode Berikutnya",
    deck: "Seluruh data capaian tridharma kini terdokumentasi secara transparan dan akuntabel sebagai fondasi awal bagi kepemimpinan fakultas periode berikutnya.",
  },
} satisfies Record<string, Scene>;

export type SceneKey = keyof typeof scenes;

/** Resolve a scene deck, running the volatile ones against the current data. */
export function deckOf(key: SceneKey, values: SceneValues): string {
  const { deck } = scenes[key] as Scene;
  return typeof deck === "function" ? deck(values) : deck;
}
