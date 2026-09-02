/**
 * Country lookup tables shared by every scene that draws a world map.
 *
 * Three separate problems live here, and they are kept together because a fix
 * to one is almost always a fix to the others:
 *
 * 1. The derived data carries an `iso3` column that is empty for a good number
 *    of rows, so a join on ISO3 alone silently drops countries.
 * 2. `src/data/geo/world-countries.json` is Natural Earth 1:110m. It holds 177
 *    polygons and spells several countries differently from the source data
 *    ("Czechia", "United States of America", "Russia"), and it has no polygon
 *    at all for the smallest states — Singapore and Hong Kong among them.
 * 3. The page writes country names in Indonesian, and until now two ad-hoc
 *    dictionaries in `src/pages/index.astro` did that job independently.
 */

/**
 * Source spelling → ISO 3166-1 alpha-3.
 *
 * Only entries the data actually needs: names whose `iso3` column is blank in
 * `collab_countries.json` / `partnership_partners.json`, plus the abbreviated
 * forms used by the student-mobility workbook ("UK", "German", "Swedia").
 */
export const COUNTRY_ISO3: Record<string, string> = {
  Algeria: "DZA",
  Australia: "AUS",
  Austria: "AUT",
  Bangladesh: "BGD",
  Belgium: "BEL",
  Brazil: "BRA",
  Brunei: "BRN",
  "Brunei Darussalam": "BRN",
  Cambodia: "KHM",
  Canada: "CAN",
  Chile: "CHL",
  China: "CHN",
  Croatia: "HRV",
  Cuba: "CUB",
  Czechia: "CZE",
  "Czech Republic": "CZE",
  Denmark: "DNK",
  Egypt: "EGY",
  Ethiopia: "ETH",
  Finland: "FIN",
  France: "FRA",
  German: "DEU",
  Germany: "DEU",
  Greece: "GRC",
  "Hong Kong": "HKG",
  Hungary: "HUN",
  India: "IND",
  Indonesia: "IDN",
  Iran: "IRN",
  Iraq: "IRQ",
  Ireland: "IRL",
  Italy: "ITA",
  Japan: "JPN",
  Kazakhstan: "KAZ",
  Libya: "LBY",
  Malaysia: "MYS",
  Morocco: "MAR",
  Netherlands: "NLD",
  "New Zealand": "NZL",
  Nigeria: "NGA",
  Norway: "NOR",
  Pakistan: "PAK",
  Panama: "PAN",
  Philippines: "PHL",
  Poland: "POL",
  Qatar: "QAT",
  Romania: "ROU",
  Russia: "RUS",
  "Russian Federation": "RUS",
  "Saudi Arabia": "SAU",
  Singapore: "SGP",
  Slovakia: "SVK",
  "South Africa": "ZAF",
  "South Korea": "KOR",
  Spain: "ESP",
  "Sri Lanka": "LKA",
  Sweden: "SWE",
  Swedia: "SWE",
  Switzerland: "CHE",
  Taiwan: "TWN",
  Tanzania: "TZA",
  Thailand: "THA",
  "Timor-Leste": "TLS",
  Turkey: "TUR",
  Ukraine: "UKR",
  UK: "GBR",
  "United Arab Emirates": "ARE",
  "United Kingdom": "GBR",
  "United States": "USA",
  "United States of America": "USA",
  "Viet Nam": "VNM",
  Vietnam: "VNM",
};

/** Source spelling → the Indonesian name the report prints. */
export const COUNTRY_NAME_ID: Record<string, string> = {
  Algeria: "Aljazair",
  Australia: "Australia",
  Austria: "Austria",
  Bangladesh: "Bangladesh",
  Belgium: "Belgia",
  Brazil: "Brasil",
  Brunei: "Brunei Darussalam",
  "Brunei Darussalam": "Brunei Darussalam",
  Cambodia: "Kamboja",
  Canada: "Kanada",
  Chile: "Cile",
  China: "Tiongkok",
  Croatia: "Kroasia",
  Cuba: "Kuba",
  Czechia: "Ceko",
  "Czech Republic": "Ceko",
  Denmark: "Denmark",
  Egypt: "Mesir",
  Ethiopia: "Etiopia",
  Finland: "Finlandia",
  France: "Prancis",
  German: "Jerman",
  Germany: "Jerman",
  Greece: "Yunani",
  "Hong Kong": "Hong Kong",
  Hungary: "Hungaria",
  India: "India",
  Indonesia: "Indonesia",
  Iran: "Iran",
  Iraq: "Irak",
  Ireland: "Irlandia",
  Italy: "Italia",
  Japan: "Jepang",
  Kazakhstan: "Kazakhstan",
  Libya: "Libia",
  Malaysia: "Malaysia",
  Morocco: "Maroko",
  Netherlands: "Belanda",
  "New Zealand": "Selandia Baru",
  Nigeria: "Nigeria",
  Norway: "Norwegia",
  Pakistan: "Pakistan",
  Panama: "Panama",
  Philippines: "Filipina",
  Poland: "Polandia",
  Qatar: "Qatar",
  Romania: "Rumania",
  Russia: "Rusia",
  "Russian Federation": "Rusia",
  "Saudi Arabia": "Arab Saudi",
  Singapore: "Singapura",
  Slovakia: "Slowakia",
  "South Africa": "Afrika Selatan",
  "South Korea": "Korea Selatan",
  Spain: "Spanyol",
  "Sri Lanka": "Sri Lanka",
  Sweden: "Swedia",
  Swedia: "Swedia",
  Switzerland: "Swiss",
  Taiwan: "Taiwan",
  Tanzania: "Tanzania",
  Thailand: "Thailand",
  "Timor-Leste": "Timor-Leste",
  Turkey: "Turki",
  Ukraine: "Ukraina",
  UK: "Britania Raya",
  "United Arab Emirates": "Uni Emirat Arab",
  "United Kingdom": "Britania Raya",
  "United States": "Amerika Serikat",
  "United States of America": "Amerika Serikat",
  "Viet Nam": "Vietnam",
  Vietnam: "Vietnam",
};

/**
 * Marker positions, as [longitude, latitude], for countries Natural Earth
 * 1:110m draws no polygon for. Without these the country vanishes from the map
 * entirely — Singapore is the second-largest student mobility destination, so
 * losing it would be a real error, not a rounding one.
 */
export const COUNTRY_FALLBACK_COORDS: Record<string, [number, number]> = {
  SGP: [103.82, 1.35],
  HKG: [114.17, 22.32],
  QAT: [51.18, 25.29],
  BHR: [50.58, 26.07],
  MLT: [14.44, 35.9],
  MUS: [57.55, -20.35],
  MDV: [73.51, 4.18],
  BRB: [-59.54, 13.19],
};

/** Yogyakarta, the origin every collaboration arc is drawn from. */
export const ORIGIN_COORD: [number, number] = [110.37, -7.8];

/** Resolve a source row to an ISO3 code, preferring the column when present. */
export function iso3Of(name: string, declared?: string | null): string {
  const trimmed = (declared ?? "").trim().toUpperCase();
  if (trimmed.length === 3) return trimmed;
  return COUNTRY_ISO3[name.trim()] ?? "";
}

/** Indonesian display name, falling back to the source spelling. */
export function countryNameId(name: string): string {
  return COUNTRY_NAME_ID[name.trim()] ?? name;
}
