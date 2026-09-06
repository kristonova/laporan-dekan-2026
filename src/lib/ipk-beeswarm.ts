export interface IpkGroup { angkatan: number; prodi: string; nilai: number[]; }
export interface IpkPoint { ipk: number; angkatan: number; order: number; }
export interface SwarmPoint extends IpkPoint { x: number; y: number; }

export const cohortColors: Record<number, string> = {
  2021: '#2563a6', 2022: '#148579', 2023: '#ce7925', 2024: '#8560ae', 2025: '#cf5271',
};

export function programmePoints(groups: IpkGroup[], programme: string): IpkPoint[] {
  return groups.filter(group => group.prodi === programme).flatMap(group =>
    group.nilai.map((ipk, order) => ({ ipk, angkatan: group.angkatan, order })),
  );
}

// Interleave equal grades deterministically so a cohort is not always packed first.
const tieOrder = (point: IpkPoint) =>
  Math.imul(point.order + 1, 2654435761) ^ Math.imul(point.angkatan, 1597334677);

export function layoutBeeswarm(points: IpkPoint[], width: number, radius = 2.4) {
  const inset = 8;
  const diameter = radius * 2 + 0.55;
  const diameterSquared = diameter * diameter;
  const placed: SwarmPoint[] = [];
  let active: SwarmPoint[] = [];
  const sorted = points.slice().sort((a, b) => a.ipk - b.ipk || tieOrder(a) - tieOrder(b) || a.angkatan - b.angkatan || a.order - b.order);
  let extent = 0;
  for (const point of sorted) {
    const x = inset + point.ipk / 4 * (width - 2 * inset);
    active = active.filter(other => x - other.x < diameter);
    const candidates = [0];
    for (const other of active) {
      const dy = Math.sqrt(Math.max(0, diameterSquared - (x - other.x) ** 2));
      candidates.push(other.y + dy, other.y - dy);
    }
    candidates.sort((a, b) => Math.abs(a) - Math.abs(b) || (placed.length % 2 ? a - b : b - a));
    const y = candidates.find(candidate => active.every(other =>
      (x - other.x) ** 2 + (candidate - other.y) ** 2 >= diameterSquared - 1e-7,
    )) ?? 0;
    const placedPoint = { ...point, x, y };
    placed.push(placedPoint);
    active.push(placedPoint);
    extent = Math.max(extent, Math.abs(y));
  }
  const height = Math.max(96, Math.ceil((extent + radius + 10) * 2));
  return { width, height, radius, points: placed.map(point => ({ ...point, y: point.y + height / 2 })) };
}
