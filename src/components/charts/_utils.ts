/* Fallbacks mirror src/lib/palette.ts and src/styles/tokens.css. */
export const SERIES_COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#657786", "#9a5b13"];

export const STATUS_COLORS: Record<string, string> = {
  tercapai: "var(--status-tercapai, #2e7d52)",
  mendekati: "var(--status-mendekati, #a97400)",
  tertinggal: "var(--status-tertinggal, #b44a00)",
  meleset: "var(--status-meleset, #a32020)",
};

export const STATUS_SYMBOLS: Record<string, string> = {
  tercapai: "✓",
  mendekati: "≈",
  tertinggal: "!",
  meleset: "×",
};

export function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

export function finite(value: unknown, fallback = 0): number {
  const number = typeof value === "number" ? value : Number(value);
  return Number.isFinite(number) ? number : fallback;
}

export function slugify(input: string): string {
  const slug = input
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 56);
  return slug || "grafik";
}

export function scaleLinear(
  value: number,
  domainMin: number,
  domainMax: number,
  rangeMin: number,
  rangeMax: number,
): number {
  if (domainMax === domainMin) return (rangeMin + rangeMax) / 2;
  const ratio = (value - domainMin) / (domainMax - domainMin);
  return rangeMin + ratio * (rangeMax - rangeMin);
}

export function niceMax(value: number, tickCount = 4): number {
  if (!Number.isFinite(value) || value <= 0) return 1;
  const roughStep = value / Math.max(1, tickCount);
  const power = 10 ** Math.floor(Math.log10(roughStep));
  const error = roughStep / power;
  const factor = error >= 5 ? 10 : error >= 2 ? 5 : error >= 1 ? 2 : 1;
  return Math.ceil(value / (factor * power)) * factor * power;
}

export function ticks(min: number, max: number, count = 4): number[] {
  if (count <= 0 || min === max) return [min];
  return Array.from({ length: count + 1 }, (_, index) => min + ((max - min) * index) / count);
}

export function formatNumber(value: number, maximumFractionDigits = 1): string {
  return new Intl.NumberFormat("id-ID", { maximumFractionDigits }).format(value);
}

export function formatCompact(value: number): string {
  const absolute = Math.abs(value);
  if (absolute >= 1_000_000_000) return `${formatNumber(value / 1_000_000_000, 1)} M`;
  if (absolute >= 1_000_000) return `${formatNumber(value / 1_000_000, 1)} jt`;
  if (absolute >= 1_000) return `${formatNumber(value / 1_000, 1)} rb`;
  return formatNumber(value, Number.isInteger(value) ? 0 : 1);
}

/**
 * Wrap a label to at most `maxLines` lines of about `maxCharacters` each,
 * ellipsising only what genuinely does not fit.
 *
 * A word longer than the budget is kept whole rather than broken mid-word.
 */
export function textLines(text: string, maxCharacters = 34, maxLines = 2): string[] {
  const words = text.trim().split(/\s+/);
  const lines: string[] = [];
  let line = "";
  let consumed = 0;

  for (const word of words) {
    const candidate = line ? `${line} ${word}` : word;
    if (candidate.length <= maxCharacters || !line) {
      line = candidate;
      consumed += 1;
      continue;
    }
    /* The word needs a new line. If the current one is already the last we
       are allowed, stop here and let the ellipsis below say so. */
    if (lines.length + 1 >= maxLines) break;
    lines.push(line);
    line = word;
    consumed += 1;
  }

  if (line) lines.push(line);
  if (consumed < words.length && lines.length) {
    lines[lines.length - 1] = `${lines[lines.length - 1].replace(/[.,;:]?$/, "")}…`;
  }
  return lines;
}

/**
 * Push labels apart so they never overlap.
 *
 * Takes the ideal y of each label — normally the y of the mark it names — and
 * returns the y it should actually be drawn at, keeping at least `gap` between
 * neighbours and the whole run inside [minY, maxY]. Order is preserved, so a
 * label never crosses past the one it started above.
 *
 * Used by every chart that writes labels directly next to its marks: slope
 * endpoints, line-end series names. Draw a leader line whenever the returned y
 * differs from the mark's own y, so the reader can still tell what points where.
 */
export function spreadLabels(
  values: { index: number; y: number }[],
  minY: number,
  maxY: number,
  gap = 21,
): Map<number, number> {
  const sorted = [...values].sort((a, b) => a.y - b.y).map((item) => ({ ...item }));

  for (let index = 1; index < sorted.length; index += 1) {
    sorted[index].y = Math.max(sorted[index].y, sorted[index - 1].y + gap);
  }

  if (sorted.length && sorted.at(-1)!.y > maxY) {
    sorted[sorted.length - 1].y = maxY;
    for (let index = sorted.length - 2; index >= 0; index -= 1) {
      sorted[index].y = Math.min(sorted[index].y, sorted[index + 1].y - gap);
    }
  }

  if (sorted.length && sorted[0].y < minY) {
    const shift = minY - sorted[0].y;
    sorted.forEach((item) => { item.y += shift; });
  }

  return new Map(sorted.map((item) => [item.index, item.y]));
}

/**
 * Approximate rendered width of a label, in user units.
 *
 * Gama Sans is not measurable at build time, so this uses the average advance
 * of a humanist sans. It is only ever used to reserve space, and it errs wide.
 */
export function approxTextWidth(text: string, fontSize = 12, bold = false): number {
  return text.length * fontSize * (bold ? 0.6 : 0.56);
}

/**
 * Lay legend entries out as a flow rather than as equal columns.
 *
 * Dividing the plot into n equal slots collides as soon as one label is longer
 * than its share ("Ilmu Komputer dan Elektronika" against "Fisika"). Here each
 * entry takes the width it needs and the row wraps when it runs out, so the
 * caller can add the extra rows to its stage height.
 */
export function flowLegend(
  labels: string[],
  maxWidth: number,
  options: { fontSize?: number; keyWidth?: number; gap?: number; rowHeight?: number } = {},
): { positions: { x: number; y: number }[]; rows: number; rowHeight: number } {
  const { fontSize = 12, keyWidth = 25, gap = 26, rowHeight = 24 } = options;
  const positions: { x: number; y: number }[] = [];
  let x = 0;
  let row = 0;

  for (const label of labels) {
    const entryWidth = keyWidth + approxTextWidth(label, fontSize);
    if (x > 0 && x + entryWidth > maxWidth) {
      row += 1;
      x = 0;
    }
    positions.push({ x, y: row * rowHeight });
    x += entryWidth + gap;
  }

  return { positions, rows: row + 1, rowHeight };
}

export function roundedEndBarPath(x: number, y: number, width: number, height: number, radius = 4): string {
  const safeWidth = Math.max(0, width);
  const r = Math.min(radius, safeWidth / 2, height / 2);
  if (safeWidth <= 0) return "";
  return `M ${x} ${y} H ${x + safeWidth - r} Q ${x + safeWidth} ${y} ${x + safeWidth} ${y + r} V ${
    y + height - r
  } Q ${x + safeWidth} ${y + height} ${x + safeWidth - r} ${y + height} H ${x} Z`;
}

export function getValue(row: Record<string, unknown>, key: string): unknown {
  return row[key];
}

export function stringifyCell(value: unknown): string {
  if (value === null || value === undefined || value === "") return "—";
  if (typeof value === "number") return Number.isFinite(value) ? formatNumber(value, 2) : "—";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}
