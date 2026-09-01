#!/usr/bin/env node
// Run pipeline stages through the project virtualenv so `npm run data` never
// depends on whichever `python3` happens to be first on PATH.
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PIPELINE_DIR = dirname(fileURLToPath(import.meta.url));
const APP_ROOT = resolve(PIPELINE_DIR, "..");

const SETUP_HINT = [
  "Virtualenv pipeline belum siap. Jalankan dari direktori aplikasi:",
  "",
  "  python -m venv .venv",
  "  .venv/Scripts/python.exe -m pip install -r pipeline/requirements.txt   # Windows",
  "  .venv/bin/python -m pip install -r pipeline/requirements.txt           # macOS/Linux",
].join("\n");

function interpreters() {
  const venv = [
    join(APP_ROOT, ".venv", "Scripts", "python.exe"),
    join(APP_ROOT, ".venv", "bin", "python"),
  ].filter((candidate) => existsSync(candidate));
  return { venv, fallback: ["python3", "python"] };
}

function hasDependencies(python) {
  const probe = spawnSync(python, ["-c", "import pandas, openpyxl, xlrd"], { stdio: "ignore" });
  return probe.status === 0;
}

function resolvePython() {
  const { venv, fallback } = interpreters();
  for (const candidate of venv) {
    if (hasDependencies(candidate)) return candidate;
  }
  if (venv.length > 0) {
    console.error(`Virtualenv ditemukan di ${join(APP_ROOT, ".venv")} tetapi dependensi belum lengkap.\n\n${SETUP_HINT}`);
    process.exit(1);
  }
  for (const candidate of fallback) {
    if (hasDependencies(candidate)) return candidate;
  }
  console.error(SETUP_HINT);
  process.exit(1);
}

const args = process.argv.slice(2);
if (args.length === 0) {
  console.error("Pemakaian: node pipeline/run-python.mjs <skrip.py|-c 'kode'> [...]");
  process.exit(1);
}

const python = resolvePython();

// `-c "..."` and other raw flags are forwarded verbatim; bare arguments are
// treated as pipeline scripts and run in order, stopping at the first failure.
if (args[0].startsWith("-")) {
  const result = spawnSync(python, args, { stdio: "inherit", cwd: PIPELINE_DIR });
  process.exit(result.status ?? 1);
}

for (const script of args) {
  const target = join(PIPELINE_DIR, script);
  if (!existsSync(target)) {
    console.error(`Skrip pipeline tidak ditemukan: ${target}`);
    process.exit(1);
  }
  const result = spawnSync(python, [target], { stdio: "inherit", cwd: PIPELINE_DIR });
  if (result.status !== 0) process.exit(result.status ?? 1);
}
