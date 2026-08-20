import { defineConfig } from "astro/config";
import { getDeploymentConfig } from "./pipeline/deployment-paths.mjs";

const { base, site } = getDeploymentConfig();

export default defineConfig({
  site,
  base: base || undefined,
  output: "static",
  trailingSlash: "never",
  build: {
    format: "directory",
    inlineStylesheets: "auto",
  },
  vite: {
    build: {
      cssMinify: true,
    },
  },
});
