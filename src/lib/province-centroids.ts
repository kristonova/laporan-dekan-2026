export const provinceCentroids: Record<string, [number, number]> = {
  aceh: [4.7, 96.7],
  "sumatera utara": [2.1, 99.5],
  "sumatera barat": [-0.7, 100.8],
  riau: [0.5, 101.8],
  "kepulauan riau": [3.9, 108.1],
  jambi: [-1.6, 103.6],
  bengkulu: [-3.8, 102.3],
  "sumatera selatan": [-3.2, 104.8],
  "kepulauan bangka belitung": [-2.7, 106.3],
  lampung: [-4.9, 105.0],
  banten: [-6.4, 106.1],
  jakarta: [-6.2, 106.8],
  "dki jakarta": [-6.2, 106.8],
  "jawa barat": [-6.9, 107.6],
  "jawa tengah": [-7.15, 110.1],
  "di yogyakarta": [-7.8, 110.37],
  "daerah istimewa yogyakarta": [-7.8, 110.37],
  "jawa timur": [-7.5, 112.2],
  bali: [-8.4, 115.1],
  "nusa tenggara barat": [-8.65, 117.5],
  "nusa tenggara timur": [-8.7, 121.0],
  "kalimantan barat": [-0.1, 111.0],
  "kalimantan tengah": [-1.6, 113.4],
  "kalimantan selatan": [-3.1, 115.3],
  "kalimantan timur": [0.5, 116.4],
  "kalimantan utara": [3.2, 116.2],
  "sulawesi utara": [0.8, 124.0],
  gorontalo: [0.7, 122.4],
  "sulawesi tengah": [-1.4, 121.4],
  "sulawesi barat": [-2.8, 119.2],
  "sulawesi selatan": [-3.7, 120.0],
  "sulawesi tenggara": [-4.1, 122.0],
  maluku: [-3.2, 129.0],
  "maluku utara": [1.5, 127.8],
  papua: [-3.9, 138.0],
  "papua barat": [-1.3, 133.0],
  "papua barat daya": [-1.0, 131.3],
  "papua tengah": [-3.5, 136.5],
  "papua pegunungan": [-4.0, 139.2],
  "papua selatan": [-7.5, 139.5],
};

export function normalizeProvinceName(value: string | null | undefined): string {
  return String(value ?? "")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/^provinsi\s+/, "")
    .replace(/\./g, "")
    .replace(/\s+/g, " ")
    .trim();
}

export function centroidForProvince(value: string | null | undefined): [number, number] | undefined {
  return provinceCentroids[normalizeProvinceName(value)];
}
