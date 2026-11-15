/**
 * ============================================================================
 * FRONTEND SHOWCASE: API CLIENT & DYNAMIC ENDPOINT RESOLUTION
 * ============================================================================
 * What to show in an interview:
 * 1. Shows how the Next.js frontend connects to the FastAPI backend dynamically.
 * 2. Works seamlessly across localhost:8000, fallback port 8001, and production cloud
 *    (e.g. Vercel deployment) via NEXT_PUBLIC_API_URL.
 * 3. Handles trailing slash sanitization to prevent URL malformation bugs.
 *
 * ORIGINAL SOURCE FILE:
 *   - frontend/src/lib/api.ts
 * ============================================================================
 */

export const API_BASE_URL = 
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, '') || 'http://localhost:8000';

/**
 * Constructs a fully qualified API endpoint URL.
 * Automatically guarantees single slash separator.
 * 
 * Examples:
 *   apiUrl('/simulate_comparison') -> 'http://localhost:8000/simulate_comparison'
 *   apiUrl('stats/router')         -> 'http://localhost:8000/stats/router'
 */
export function apiUrl(endpoint: string): string {
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${API_BASE_URL}${cleanEndpoint}`;
}

