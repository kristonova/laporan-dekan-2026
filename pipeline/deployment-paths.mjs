const trimSlashes = (value = "") => value.replace(/^\/+|\/+$/g, "");

export function getDeploymentConfig(env = process.env) {
  const [githubOwner = "", githubRepo = ""] = (env.GITHUB_REPOSITORY ?? "").split("/", 2);
  const isUserSite = githubOwner && githubRepo.toLowerCase() === `${githubOwner.toLowerCase()}.github.io`;
  const hasConfiguredBase = Object.prototype.hasOwnProperty.call(env, "PUBLIC_BASE_PATH");
  const configuredBase = trimSlashes(env.PUBLIC_BASE_PATH ?? "");
  const inferredBase = githubOwner && githubRepo && !isUserSite ? githubRepo : "";
  const baseSegment = hasConfiguredBase ? configuredBase : inferredBase;
  const base = baseSegment ? `/${baseSegment}` : "";
  const site = env.PUBLIC_SITE_URL || (githubOwner ? `https://${githubOwner}.github.io` : undefined);

  return { base, site };
}

export function withDeploymentBase(pathname, base) {
  if (/^(?:[a-z][a-z\d+.-]*:|\/\/|#)/i.test(pathname)) return pathname;
  const suffix = pathname.replace(/^\/+/, "");
  return suffix ? `${base}/${suffix}` : `${base}/`;
}
