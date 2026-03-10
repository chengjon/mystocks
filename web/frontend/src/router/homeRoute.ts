export const HOME_ROUTE_NAME = "dashboard"
export const HOME_ROUTE_PATH = "/dashboard"
export const LEGACY_HOME_ROUTE_PATH = "/dealing-room"

export function normalizeLegacyHomeRedirect(path: string): string {
  try {
    const url = new URL(path, "http://localhost")

    if (/^\/dealing-room\/?$/.test(url.pathname)) {
      url.pathname = HOME_ROUTE_PATH
    }

    return `${url.pathname}${url.search}${url.hash}`
  } catch {
    return path
  }
}
