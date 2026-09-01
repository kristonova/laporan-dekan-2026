/**
 * Chart colour constants.
 *
 * SVG marks receive their colour as a prop that ends up in a `fill`/`stroke`
 * attribute, so the value has to be a literal the pages can pass around — a CSS
 * custom property alone would not survive every place these are used. This
 * module is the single place those literals live; `src/styles/tokens.css` holds
 * the same values for everything that is styled in CSS. Change both together.
 *
 * Brand values follow the UGM Design System (`UGM Design System/tokens/`).
 * The data-series ramps follow PRD section 9.2, which the Design System does
 * not cover: it defines no palette for charts.
 */

/** UGM Blue — PANTONE P111-16C. Headings, hero fields, the default series. */
export const UGM_BLUE = "#01416b";
/** UGM Yellow — PANTONE P7-8C. Accent only; never a data series (1.4:1 on light). */
export const UGM_GOLD = "#fdd402";
/** Cold-open and dark-mode surface, derived from UGM Blue (PRD section 9.6). */
export const UGM_BLUE_DEEP = "#0b1f2e";
export const UGM_BLUE_SKY = "#1c75bc";

/**
 * Department series. The order is permanent and never rotated, so a colour
 * means the same department on every scene of the page.
 */
export const DEPT = {
  fisika: "#2a78d6",
  ike: "#eb6834",
  kimia: "#1baf7a",
  matematika: "#4a3aa7",
  unmapped: "#73716c",
} as const;

/** Sequential blue ramp, light to dark. */
export const SEQ = {
  100: "#cde2fb",
  250: "#86b6ef",
  400: "#3987e5",
  550: "#1c5cab",
  700: "#0d366b",
} as const;

/**
 * Categorical accents for series that are not departments — graduation levels,
 * competition tiers, health bands. Distinct from DEPT so the two never read as
 * the same encoding, and distinct from STATUS so neither borrows the other.
 */
export const ACCENT = {
  navy: UGM_BLUE,
  teal: "#1baf7a",
  orange: "#eb6834",
  amber: "#a97400",
  crimson: "#a32020",
  slate: "#73716c",
  mist: "#c6c9cb",
} as const;

/** TCK indicator status. Never reused as a data-series palette. */
export const STATUS = {
  tercapai: "#2e7d52",
  mendekati: "#a97400",
  tertinggal: "#b44a00",
  meleset: "#a32020",
} as const;

export type DepartmentKey = keyof typeof DEPT;
