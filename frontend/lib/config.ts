/**
 * Central API URL resolver for Graveyard Mining Frontend.
 *
 * Priority:
 * 1. Explicitly configured NEXT_PUBLIC_API_URL environment variable (if present)
 * 2. Automatic detection: If running in a browser on non-localhost domain (e.g. Vercel),
 *    defaults to the deployed Railway API: https://graveyard-mining-api.up.railway.app
 * 3. Localhost fallback: http://localhost:8000
 */
export const getApiUrl = (): string => {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL.replace(/\/$/, '');
  }

  if (
    typeof window !== 'undefined' &&
    window.location.hostname !== 'localhost' &&
    window.location.hostname !== '127.0.0.1'
  ) {
    return 'https://graveyard-mining-api.up.railway.app';
  }

  return 'http://localhost:8000';
};
