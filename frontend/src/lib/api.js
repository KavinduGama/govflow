// Base URL for every backend call. Set NEXT_PUBLIC_API_URL per environment (e.g. https://api.govflow.lk).
// NEXT_PUBLIC_ vars are inlined into the browser bundle at build time, so changing it needs a rebuild.
export const API_URL = `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/v1`;
