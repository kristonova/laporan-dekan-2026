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
      "Membaca posisi FMIPA UGM hari ini melalui data resmi institusi: kekuatan sivitas akademika, ketercapaian target perjanjian kinerja, serta pemetaan objektif terhadap aspek-aspek strategis fakultas.",
  },
  journey: {
    number: "Bagian II",
    title: "Rekam Jejak Transformasi Lima Tahun",
    description:
      "Sebuah capaian baru terasa maknanya ketika dilihat sebagai perjalanan panjang. Melalui lima pilar tridharma, bab ini menelusuri lonjakan riset, dampak pengabdian bagi masyarakat, profil mahasiswa dari seluruh penjuru negeri, hingga ruang-ruang yang masih perlu terus dibenahi.",
  },
  handover: {
    number: "Bagian III",
    title: "Estafet Kepemimpinan & Agenda Strategis",
    description:
      "Laporan pertanggungjawaban yang baik bukan sekadar mendokumentasikan masa lalu, melainkan meletakkan fondasi data yang kokoh dan peta jalan yang jernih bagi kepemimpinan fakultas berikutnya untuk melangkah lebih jauh.",
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
  format: (value: number, digits?: number) => string;
}

type Deck = string | ((values: SceneValues) => string);

interface Scene {
  question: string;
  deck: Deck;
}

export const scenes = {
  "1.1": {
    question: "Siapa Saja yang Menopang FMIPA UGM Hari Ini?",
    deck: (v) =>
      `Di balik dinamika akademik fakultas, terdapat ${v.format(v.lecturers)} dosen dan ${v.format(v.academicStaff)} tenaga kependidikan yang mengawal ${v.format(v.studyProgrammes)} program studi di empat departemen. Seluruh aktivitas ditopang oleh ${v.format(v.laboratories)} laboratorium terpadu serta menjadi rumah belajar bagi ${v.format(v.activeStudents)} mahasiswa sarjana aktif.`,
  },
  "1.2": {
    question: "Sejauh Mana Target Kinerja Fakultas Telah Terpenuhi?",
    deck: (v) =>
      `Hingga triwulan berjalan, sebanyak ${v.format(v.tckAchieved)} dari ${v.format(v.tckTotal)} indikator kinerja telah berhasil memenuhi target. Sementara itu, pemenuhan ${v.format(v.tckBehind)} indikator lainnya terus dipacu menjelang penutupan tahun anggaran—disajikan secara terbuka dan apa adanya bersama konteks data penjelasnya.`,
  },
  "1.3": {
    question: "Alur Transformasi: Dari Sumber Daya Menuju Dampak Nyata",
    deck: "Setiap rupiah dana riset dan curahan waktu sivitas bermuara pada dampak nyata: dari gagasan di laboratorium menjelma menjadi publikasi bereputasi, pengabdian di pelosok nusantara, serta kemanfaatan luas bagi masyarakat.",
  },
  "2.1": {
    question: "Bagaimana Reputasi Riset FMIPA Melompat di Panggung Global?",
    deck: "Dampak keilmuan sivitas melonjak lebih dari tiga kali lipat dalam enam tahun terakhir: dari 4.129 sitasi pada 2019 menjadi puncaknya 12.629 sitasi pada 2024. Untuk tahun 2025, angka sitasi masih terus bertambah seiring pemutakhiran berkala di pangkalan data Scopus.",
  },
  "2.2": {
    question: "Bagaimana Produktivitas Publikasi Tersebar di Empat Departemen?",
    deck: (v) =>
      `Sebanyak ${v.format(v.publicationsMappedShare, 1)}% artikel ilmiah periode ${v.publicationsFirstYear}–${v.publicationsLastYear} berhasil dipetakan ke departemen masing-masing: sebagian besar melalui penetapan pada basis data fakultas, sisanya melalui identifikasi ID Scopus para penulis. Sebanyak ${v.format(v.publicationsUnmapped)} artikel selebihnya terus ditelusuri untuk melengkapi potret utuh produktivitas fakultas.`,
  },
  "2.2p": {
    question: "Seberapa Kuat Gema Sitasi Karya FMIPA Dibanding Rata-rata Dunia?",
    deck: (v) =>
      `Jumlah karya tumbuh, tetapi gema sitasinya belum sepenuhnya menyusul: dari ${v.format(v.researchAreas)} bidang ilmu yang tercatat, ${v.format(v.researchAreasAtWorld)} bidang berada pada atau di atas rata-rata dunia. Di antara bidang dengan keluaran terbesar, ${v.researchLeadArea} memimpin dengan FWCI ${v.format(v.researchLeadFwci, 2)}. Mutu sitasi inilah agenda yang menuntut perhatian sejajar dengan agenda jumlah.`,
  },
  "2.3": {
    question: "Topik Sains Apa Saja yang Menjadi Ujung Tombak Riset FMIPA?",
    deck: (v) =>
      `Sebanyak ${v.format(v.topicClusters)} klaster topik memperlihatkan peta riset fakultas yang kaya dan lintas disiplin—mulai dari sains material, energi baru terbarukan, kecerdasan buatan, hingga biosains dan teknologi pemantauan lingkungan.`,
  },
  "2.4": {
    question: "Seberapa Luas Jejak Kolaborasi Riset Peneliti FMIPA di Kancah Dunia?",
    deck: (v) =>
      `Jejaring kolaborasi para ilmuwan FMIPA kini menjangkau peneliti di ${v.format(v.collabCountries)} negara. Proporsi publikasi bersama mitra internasional naik dari ${v.format(v.collabFirstShare, 1)}% pada ${v.collabFirstYear} menjadi ${v.format(v.collabLastShare, 1)}% pada ${v.collabLastYear}.`,
  },
  "2.4p": {
    question: "Seberapa Terbuka Akses Publik terhadap Karya Ilmiah FMIPA?",
    deck: (v) =>
      `Sekitar separuh keluaran fakultas dapat dibaca tanpa berbayar: ${v.format(v.openAccessFirstShare, 1)}% pada ${v.openAccessFirstYear} dan ${v.format(v.openAccessLastShare, 1)}% pada ${v.openAccessLastYear}, hampir seluruhnya melalui jalur gold di sisi penerbit. Salinan repositori (green) hanya ${v.format(v.openAccessGreenLatest)} artikel pada ${v.openAccessLastYear}—padahal jalur inilah yang paling terkendali oleh fakultas sendiri.`,
  },
  "2.5": {
    question: "Bagaimana Komposisi dan Kematangan Kepakaran Dosen FMIPA?",
    deck: (v) =>
      `Kapasitas kepakaran fakultas kian matang: satu dari lima dosen tetap aktif (20,7% atau 42 orang dari total ${v.format(v.lecturers)} dosen) kini telah menyandang jabatan fungsional Guru Besar.`,
  },
  "2.6": {
    question: "Agenda Apa yang Perlu Dipercepat di Pilar Reputasi Akademik?",
    deck: "Meski produktivitas riset meningkat pesat, tantangan ke depan bertumpu pada dua hal utama: mendorong pemerataan publikasi lintas departemen serta memacu karya ilmiah mahasiswa program doktor bersama jejaring mitra global.",
  },
  "3.1": {
    question: "Bagaimana Lompatan Dana Riset Mengubah Skala Penelitian Fakultas?",
    deck: "Perolehan dana riset melompat luar biasa hingga 22,7 kali lipat—dari Rp3,30 miliar pada 2021 menembus puncaknya Rp74,91 miliar pada 2024. Pada 2025, perolehan dana berkonsolidasi di angka Rp69,51 miliar, tetap puluhan kali lipat di atas skala awal periode.",
  },
  "3.2": {
    question: "Di Mana Saja Jejak Pengabdian Sivitas FMIPA Membawa Manfaat?",
    deck: "Aktivitas Pengabdian kepada Masyarakat (PkM) tumbuh lebih dari empat kali lipat, dari 109 menjadi 445 kegiatan per tahun. Sepanjang 2021–2025, sebanyak 921 dari 1.481 kegiatan telah terpetakan lokasinya secara presisi di berbagai provinsi di seluruh nusantara.",
  },
  "3.3": {
    question: "Bagaimana Riset FMIPA Menjawab Agenda Pembangunan Berkelanjutan (SDGs)?",
    deck: "Kiprah tridharma memberi sumbangsih langsung pada pilar industri dan inovasi (SDG 9), kesehatan (SDG 3), konsumsi bertanggung jawab (SDG 12), serta penyediaan air bersih (SDG 6), sembari memperluas pencatatan pada pilar-pilar SDGs lainnya.",
  },
  "3.4": {
    question: "Bagaimana Jurnal Ilmiah Berkala FMIPA Merawat Diseminasi Sains?",
    deck: "Empat jurnal berkala ilmiah yang dikelola FMIPA konsisten menjadi wadah diseminasi riset bermutu dengan 461 artikel terindeks bereputasi. Di ruang publik, gaung inovasi sivitas kian meluas dengan dokumentasi liputan media yang tercatat rapi sejak 2023.",
  },
  "3.5": {
    question: "Seberapa Kuat Jejaring Kemitraan Strategis yang Terjalin?",
    deck: (v) =>
      `Sepanjang kurun 2021–2026, fakultas mengikat ${v.format(v.partnershipTotal)} naskah kerja sama resmi, dengan ${v.format(v.partnershipInternational)} dokumen di antaranya merupakan kolaborasi internasional yang menghubungkan FMIPA dengan mitra di ${v.format(v.partnershipCountries)} negara.`,
  },
  "3.6": {
    question: "Langkah Apa yang Menjadi Prioritas Akselerasi Hilirisasi?",
    deck: (v) =>
      `Pilar kontribusi menuntut langkah akselerasi paling nyata: saat ini ${v.format(v.contributionAchieved)} dari ${v.format(v.contributionTotal)} indikator telah memenuhi target triwulan berjalan, dengan fokus utama mempercepat hilirisasi hasil riset ke masyarakat dan industri serta mendokumentasikan capaian SDGs.`,
  },
  "4.1": {
    question: "Ke Mana Para Lulusan FMIPA Melanjutkan Langkah Karier Mereka?",
    deck: (v) =>
      `Lulusan sains dan matematika membuktikan keluwesan daya saing mereka di pasar kerja. Survei penelusuran lulusan terhadap ${v.format(v.tracerRespondents)} alumni mencatat sektor ${v.tracerTopSector} sebagai penyerap terbesar, disusul industri perbankan/keuangan serta dunia pendidikan dan riset.`,
  },
  "4.2": {
    question: "Berapa Cepat Lulusan FMIPA Terserap di Dunia Kerja?",
    deck: (v) =>
      `Masa tunggu lulusan terbilang singkat: sebanyak ${v.format(v.tracerWithinSixMonths)} dari ${v.format(v.tracerRespondents)} responden telah bekerja dalam waktu kurang dari enam bulan setelah lulus. Bahkan, ${v.format(v.tracerBeforeGraduation)} orang di antaranya sudah diterima bekerja sebelum resmi diwisuda.`,
  },
  "4.3": {
    question: "Bagaimana Bekal Pengalaman Karier Mahasiswa Disiapkan Sejak Kuliah?",
    deck: "Pembelajaran di luar ruang kuliah kian diminati: partisipasi mahasiswa dalam program MBKM melampaui target tahunan fakultas, diperkaya program percepatan (fast track), keikutsertaan kompetisi ilmiah, serta pembekalan karier profesional.",
  },
  "4.4": {
    question: "Sejauh Mana Mobilitas Internasional Mahasiswa Berjalan Dua Arah?",
    deck: (v) =>
      `Pertukaran mahasiswa berlangsung dinamis: tercatat ${v.format(v.foreignCredit)} mahasiswa asing mengikuti program berbobot kredit (credit-earning) dan ${v.format(v.foreignNonCredit)} mahasiswa pada program non-kredit, sementara mahasiswa FMIPA terus didorong menimba pengalaman internasional.`,
  },
  "4.5": {
    question: "Bagaimana Ketepatan Waktu Kelulusan di Seluruh Jenjang Studi?",
    deck: "Tingkat kelulusan tepat waktu di jenjang Sarjana, Magister, maupun Doktor berhasil melampaui target institusi, mencerminkan pemantauan masa studi dan pendampingan tugas akhir yang berjalan efektif.",
  },
  "4.6": {
    question: "Seberapa Ketat Persaingan Masuk dan Antusiasme Calon Mahasiswa?",
    deck: (v) =>
      `Minat calon mahasiswa sarjana tumbuh dari ${v.format(v.admissionsApplicantsFirst)} pendaftar pada ${v.admissionsFirstYear} menjadi ${v.format(v.admissionsApplicants)} pada ${v.admissionsLastYear}. Dengan daya tampung ${v.format(v.admissionsSeats)} kursi, rasio keketatan seleksi berada di kisaran 1 : ${v.format(v.admissionsTightnessLast, 1)} (sebelumnya 1 : ${v.format(v.admissionsTightnessFirst, 1)}). Kepastian studi pun sangat kuat, dengan ${v.format(v.admissionsYieldLast, 1)}% calon mahasiswa yang diterima langsung melakukan daftar ulang.`,
  },
  "4.7": {
    question: "Bagaimana Prestasi Mahasiswa dan Hasil Kelulusan Tiap Tahun?",
    deck: (v) =>
      `Fakultas meluluskan ${v.format(v.graduatesLatest)} sarjana baru pada tahun akademik terakhir. Di saat yang sama, mahasiswa menorehkan ${v.format(v.achievementsTotal)} prestasi membanggakan sejak 2022, termasuk ${v.format(v.achievementsInternational)} capaian di panggung kompetisi internasional.`,
  },
  "4.3p": {
    question: "Seberapa Aktif Mahasiswa Terlibat Langsung dalam Riset Dosen?",
    deck: "Keterlibatan mahasiswa dalam penelitian dosen bukan sekadar pelengkap: sebanyak 182 judul riset melibatkan langsung mahasiswa sarjana sebagai asisten peneliti, dengan lonjakan partisipasi paling nyata pada periode 2023–2024.",
  },
  "5.1": {
    question: "Bagaimana Pembinaan Karier dan Kualifikasi Dosen Berjalan?",
    deck: (v) =>
      `Penguatan tata kelola dan kesejahteraan menunjukkan progres paling solid: ${v.format(v.welfareAchieved)} dari ${v.format(v.welfareTotal)} indikator kinerja telah memenuhi target, didorong kelancaran kenaikan jabatan fungsional dosen serta pengakuan kepakaran di tingkat internasional.`,
  },
  "5.2": {
    question: "Sejauh Mana Fasilitas Kampus Ramah Disabilitas dan Inklusif Terwujud?",
    deck: (v) =>
      `Komitmen mewujudkan kampus inklusif diwujudkan melalui penyediaan ${v.format(v.disabilityFacilities)} unit fasilitas ramah disabilitas, melampaui target tahunan (${v.format(v.disabilityTarget)} unit). Standar sarana ramah lingkungan dan aksesibilitas terus diperkuat bersama universitas.`,
  },
  "5.3": {
    question: "Bagaimana Profil Kesehatan Dosen dan Tenaga Kependidikan Terpantau?",
    deck: (v) =>
      `Pemantauan kesehatan berkala melalui Posbindu HPU telah mencatat ${v.format(v.posbinduYearVisits)} kunjungan dosen dan tendik sepanjang lima tahun (${v.posbinduFirstYear}–${v.posbinduLastYear}). Faktor risiko terbanyak ditemukan pada parameter ${v.posbinduTopRisk} (${v.format(v.posbinduTopRiskShare)}% peserta), sementara proporsi peserta dengan risiko tekanan darah meningkat dari ${v.format(v.posbinduTensionFirst)}% menjadi ${v.format(v.posbinduTensionLast)}% sehingga memerlukan perhatian promotif bersama.`,
  },
  "6.1": {
    question: "Siapa Saja yang Menempuh Pendidikan di FMIPA UGM?",
    deck: (v) =>
      `Sumber asal pendidikan per 2 September 2026 memuat ${v.format(v.studentsTotal)} rekaman dari enam angkatan (${v.studentsFirstYear}–${v.studentsLastYear}): ${v.format(v.studentsUndergraduate)} S1, ${v.format(v.studentsMasters)} S2, ${v.format(v.studentsDoctoral)} S3, dan ${v.format(v.studentsAllNonDegree)} non-gelar. Cakupan Pilar 5 kini menjangkau pendidikan sarjana hingga doktor.`,
  },
  "6.2": {
    question: "Dari Mana Saja Asal Daerah Mahasiswa FMIPA UGM?",
    deck: (v) =>
      `Akses pendidikan di FMIPA kian terbuka bagi putra-putri dari seluruh penjuru tanah air: jangkauan asal mahasiswa meluas dari ${v.format(v.studentsProvincesFirst)} menjadi ${v.format(v.studentsProvincesLast)} provinsi. Kehadiran mahasiswa dari luar Jawa sempat menyentuh ${v.format(v.studentsOutsideJavaPeak, 1)}% pada angkatan ${v.studentsOutsideJavaPeakYear}, dan kini berada di kisaran ${v.format(v.studentsOutsideJavaLast, 1)}% pada angkatan ${v.studentsLastYear}.`,
  },
  "6.3": {
    question: "Bagaimana Keseimbangan Gender Terbentuk di Tiap Program Studi?",
    deck: (v) =>
      `Secara keseluruhan di tingkat fakultas, proporsi mahasiswa perempuan relatif seimbang di angka ${v.format(v.studentsWomenShareLast, 1)}%. Namun, tiap disiplin ilmu memiliki karakteristik peminatan yang khas: Program Studi ${v.studentsWomenTopProgramme} mencatat proporsi perempuan tertinggi (${v.format(v.studentsWomenTopShare, 1)}%), sedangkan di ${v.studentsWomenLowProgramme} berada pada kisaran ${v.format(v.studentsWomenLowShare, 1)}%.`,
  },
  "6.4": {
    question: "Lewat Pintu Mana Saja Mahasiswa Masuk ke FMIPA?",
    deck: (v) =>
      `Jalur seleksi ${v.studentsTopPathway} menjadi pintu gerbang utama yang menyaring ${v.format(v.studentsTopPathwayShare, 1)}% mahasiswa. Di samping seleksi nasional berbasis prestasi dan tes, jalur International Undergraduate Program (IUP) konsisten menyambut sekitar ${v.format(v.studentsIup)} mahasiswa per angkatan bersama jalur afirmasi daerah.`,
  },
  "6.5": {
    question: "Seperti Apa Latar Belakang Pekerjaan Keluarga Mahasiswa?",
    deck: (v) =>
      `Keberagaman latar belakang keluarga tecermin dari profesi orang tua/wali mahasiswa yang didominasi oleh ${v.studentsGuardianTop} (${v.format(v.studentsGuardianTopShare, 1)}%), disusul pegawai swasta dan aparatur sipil negara. Sebanyak ${v.format(v.studentsGuardianUnreported)} data tidak mencantumkan spesifikasi pekerjaan, sehingga catatan ini berfungsi sebagai potret umum keberagaman, bukan tolok ukur kemampuan ekonomi.`,
  },
  "6.6": {
    question: "Dari Sekolah dan Universitas Mana Mahasiswa FMIPA Berasal?",
    deck: (v) =>
      `Jejaring pendidikan asal kini mencakup ${v.format(v.studentsSchoolUnique)} nama SMA/MA untuk mahasiswa S1, ${v.format(v.studentsMasterOrigins)} nama universitas S1 untuk mahasiswa magister, dan ${v.format(v.studentsDoctorOrigins)} nama universitas S2 untuk mahasiswa doktor. Sumber baru melengkapi gambaran enam angkatan, termasuk sekolah asal angkatan 2021–2022.`,
  },
  "6.7": {
    question: "Bagaimana Perjalanan Satu Angkatan Mahasiswa Sejak Masuk hingga Lulus?",
    deck: (v) =>
      `Perjalanan satu angkatan memperlihatkan dinamika studi yang nyata: setelah lima tahun masa perkuliahan, sebanyak ${v.format(v.studentsCohortGraduated)} mahasiswa angkatan ${v.studentsFirstYear} telah resmi menyandang gelar sarjana. Variasi median IPK antarangkatan wajar terjadi seiring tahapan semester dan penyelesaian tugas akhir yang sedang ditempuh.`,
  },
  "7.1": {
    question: "Pekerjaan Rumah dan Agenda yang Perlu Dipercepat",
    deck: (v) =>
      `Transparansi adalah kunci perbaikan: laporan ini memetakan secara jujur ${v.format(v.tckBehind)} indikator yang perlu dipercepat pemenuhannya, agenda penyelarasan data lulusan dan keselamatan kerja, serta langkah antisipasi untuk menjaga kesinambungan pendanaan riset ke depan.`,
  },
  "7.2": {
    question: "Estafet Kepemimpinan: Fondasi Data untuk Melangkah Maju",
    deck: "Seluruh rekam jejak tridharma selama lima tahun kini terdokumentasi rapi, transparan, dan teruji—menjadi modal berharga dan pijakan kokoh bagi kepemimpinan fakultas periode berikutnya untuk melangkah lebih jauh.",
  },
} satisfies Record<string, Scene>;

export type SceneKey = keyof typeof scenes;

/** Resolve a scene deck, running the volatile ones against the current data. */
export function deckOf(key: SceneKey, values: SceneValues): string {
  const { deck } = scenes[key] as Scene;
  return typeof deck === "function" ? deck(values) : deck;
}
