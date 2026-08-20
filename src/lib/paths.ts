const configuredBase = import.meta.env.BASE_URL || "/";

/**
 * The deployment subpath without a trailing slash. An application served from
 * the origin root uses an empty prefix.
 */
export const basePath = configuredBase === "/"
  ? ""
  : `/${configuredBase.replace(/^\/+|\/+$/g, "")}`;

/** Prefix an application-root URL with Astro's configured base path. */
export function withBase(url: string): string {
  if (!url.startsWith("/") || url.startsWith("//")) return url;

  if (
    basePath
    && (
      url === basePath
      || url.startsWith(`${basePath}/`)
      || url.startsWith(`${basePath}#`)
      || url.startsWith(`${basePath}?`)
    )
  ) {
    return url;
  }

  return `${basePath}${url}`;
}

/** Remove the deployment prefix so route comparisons remain host-agnostic. */
export function stripBase(pathname: string): string {
  if (!basePath) return pathname || "/";
  if (pathname === basePath) return "/";
  if (pathname.startsWith(`${basePath}/`)) return pathname.slice(basePath.length) || "/";
  return pathname || "/";
}
