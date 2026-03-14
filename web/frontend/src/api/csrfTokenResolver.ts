export type CSRFTokenFetcher = () => Promise<string>

export function createCSRFTokenResolver(fetchToken: CSRFTokenFetcher): () => Promise<string> {
  return async () => {
    try {
      return await fetchToken()
    } catch {
      return ""
    }
  }
}
