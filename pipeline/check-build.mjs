import { access, readFile, readdir } from "node:fs/promises";
import { extname, resolve, sep } from "node:path";
import { getDeploymentConfig, withDeploymentBase } from "./deployment-paths.mjs";

const root = resolve("dist");
const failures = [];
const { base } = getDeploymentConfig();

const exists = async (path) => access(path).then(() => true, () => false);
const htmlFiles = (await readdir(root, { recursive: true }))
  .filter((path) => path.endsWith(".html"));

const stripDeploymentBase = (pathname) => {
  const absolutePath = pathname.startsWith("/") ? pathname : `/${pathname}`;
  if (!base) return absolutePath;
  if (absolutePath === base) return "/";
  if (!absolutePath.startsWith(`${base}/`)) return null;
  return absolutePath.slice(base.length) || "/";
};

const routeFile = (pathname) => {
  const localPath = stripDeploymentBase(pathname);
  if (localPath === null) return null;
  if (localPath === "/") return resolve(root, "index.html");

  const clean = localPath.replace(/^\//, "").replace(/\/$/, "");
  const target = extname(clean) ? resolve(root, clean) : resolve(root, clean, "index.html");
  return target.startsWith(`${root}${sep}`) ? target : null;
};

const deploymentPathForFile = (relativePath) => {
  const normalized = relativePath.split(sep).join("/");
  if (normalized === "index.html") return withDeploymentBase("/", base);
  if (normalized.endsWith("/index.html")) {
    return withDeploymentBase(`/${normalized.slice(0, -"index.html".length)}`, base);
  }
  return withDeploymentBase(`/${normalized}`, base);
};

for (const relativePath of htmlFiles) {
  const file = resolve(root, relativePath);
  const html = await readFile(file, "utf8");
  if (!/<html[^>]+lang="id"/.test(html)) failures.push(`${relativePath}: atribut lang=id hilang`);
  if (/>NaN</.test(html)) failures.push(`${relativePath}: nilai NaN terlihat`);
  if (/>2\.(?:019|020|021|022|023|024|025|026)</.test(html)) failures.push(`${relativePath}: tahun diformat sebagai ribuan`);

  for (const match of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
    const href = match[1];
    if (href.startsWith("//") || (!href.startsWith("/") && !href.startsWith("#"))) continue;
    const [rawPath, rawFragment] = href.split("#", 2);
    const pathname = rawPath || deploymentPathForFile(relativePath);
    const target = routeFile(pathname.split("?", 1)[0]);
    if (target === null) {
      failures.push(`${relativePath}: target di luar base deployment ${href}`);
      continue;
    }
    if (!(await exists(target))) {
      failures.push(`${relativePath}: target hilang ${href}`);
      continue;
    }
    if (rawFragment && target.endsWith(".html")) {
      const targetHtml = target === file ? html : await readFile(target, "utf8");
      const fragment = decodeURIComponent(rawFragment);
      if (!targetHtml.includes(`id="${fragment}"`)) failures.push(`${relativePath}: fragmen hilang ${href}`);
    }
  }
}

const sw = await readFile(resolve(root, "sw.js"), "utf8");
// These components once existed and passed type checks while never rendering
// on the story page. Check the public artifact, not just their source files.
const storyHtml = await readFile(resolve(root, "index.html"), "utf8");
for (const id of ["profil-mahasiswa-asing", "rincian-lama-studi", "profil-lulusan-jenjang", "rincian-prestasi", "beasiswa", "rincian-pengalaman-belajar", "rincian-fasilitas-gedung"]) {
  if (!storyHtml.includes(`id="${id}"`)) failures.push(`index.html: bagian rincian ${id} tidak terpasang`);
}
for (const marker of ["data-scholarship-profile", "data-achievement-explorer", "asing-detail-0", "tck-lulus-S3", "profil-lulus-S2", "rincian-fasilitas", "rincian-pembelajaran"]) {
  if (!storyHtml.includes(marker)) failures.push(`index.html: visualisasi rincian ${marker} tidak dirender`);
}
const precacheMatch = sw.match(/const PRECACHE = (\[[\s\S]*?\]);/);
if (!precacheMatch) {
  failures.push("sw.js: daftar precache hilang");
} else {
  const urls = JSON.parse(precacheMatch[1]);
  for (const url of urls) {
    const target = routeFile(url);
    if (target === null) failures.push(`sw.js: target precache di luar base deployment ${url}`);
    else if (!(await exists(target))) failures.push(`sw.js: target precache hilang ${url}`);
  }
}

if (failures.length) {
  console.error(failures.join("\n"));
  process.exit(1);
}

console.log(`Build smoke test lulus: ${htmlFiles.length} halaman, tautan internal dan precache valid.`);
