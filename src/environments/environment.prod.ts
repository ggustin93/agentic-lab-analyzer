/**
 * Production environment. The API is expected to be served behind the same
 * origin (reverse proxy) so the app ships no hardcoded host and PHI never
 * transits plain HTTP.
 */
export const environment = {
  production: true,
  apiBaseUrl: '/api/v1'
};
