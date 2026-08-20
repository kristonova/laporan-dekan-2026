const id = new Intl.NumberFormat("id-ID");
const idOneDecimal = new Intl.NumberFormat("id-ID", {
  minimumFractionDigits: 0,
  maximumFractionDigits: 1,
});

export function number(value: number): string {
  return id.format(value);
}

export function decimal(value: number): string {
  return idOneDecimal.format(value);
}

export function percent(value: number, valueIsRatio = false): string {
  return `${idOneDecimal.format(valueIsRatio ? value * 100 : value)}%`;
}

export function rupiahCompact(value: number): string {
  if (Math.abs(value) >= 1_000_000_000) return `Rp${idOneDecimal.format(value / 1_000_000_000)} miliar`;
  if (Math.abs(value) >= 1_000_000) return `Rp${idOneDecimal.format(value / 1_000_000)} juta`;
  return `Rp${id.format(value)}`;
}

export function csvDataUri(rows: Record<string, unknown>[]): string {
  if (!rows.length) return "data:text/csv;charset=utf-8,";
  const keys = Object.keys(rows[0]);
  const escape = (value: unknown) => `"${String(value ?? "").replaceAll('"', '""')}"`;
  const csv = [keys.map(escape).join(","), ...rows.map((row) => keys.map((key) => escape(row[key])).join(","))].join("\n");
  return `data:text/csv;charset=utf-8,${encodeURIComponent(csv)}`;
}
