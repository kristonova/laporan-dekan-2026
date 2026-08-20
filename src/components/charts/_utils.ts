export const SERIES_COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#657786", "#9a5b13"];

export const STATUS_COLORS: Record<string, string> = {
  tercapai: "var(--status-tercapai, #147a55)",
  mendekati: "var(--status-mendekati, #806000)",
  tertinggal: "var(--status-tertinggal, #a85a0a)",
  meleset: "var(--status-meleset, #b42318)",
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

export function textLines(text: string, maxCharacters = 34, maxLines = 2): string[] {
  const words = text.trim().split(/\s+/);
  const lines: string[] = [];
  let line = "";

  for (const word of words) {
    const candidate = line ? `${line} ${word}` : word;
    if (candidate.length <= maxCharacters || !line) {
      line = candidate;
      continue;
    }
    lines.push(line);
    line = word;
    if (lines.length === maxLines - 1) break;
  }

  if (line && lines.length < maxLines) lines.push(line);
  const included = lines.join(" ").split(/\s+/).length;
  if (included < words.length && lines.length) {
    lines[lines.length - 1] = `${lines[lines.length - 1].replace(/[.,;:]?$/, "")}…`;
  }
  return lines;
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
