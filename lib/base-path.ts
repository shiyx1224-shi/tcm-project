/** Public asset prefix for GitHub Pages (`/tcm-project`) or empty in local/dev. */
export function withBasePath(path: string): string {
  const base = process.env.NEXT_PUBLIC_BASE_PATH ?? ""
  if (!path.startsWith("/")) return path
  return `${base}${path}`
}
