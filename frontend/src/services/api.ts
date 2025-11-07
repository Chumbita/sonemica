// src/services/api.ts
const BASE = import.meta.env.VITE_API_BASE || "";

export async function getAuthStatus(){
  try{
    const r = await fetch(`${BASE}/api/auth/status`, { credentials: "include" });
    if(!r.ok) return { connected:false };
    return r.json();
  }catch{
    return { connected:false };
  }
}

export function loginSpotify(){
  const redirect = encodeURIComponent(`${window.location.origin}/loading`);
  window.location.href = `${BASE}/api/auth/login?redirect=${redirect}`;
}

// PARA QUE PUEDAN INTEGRAR EL BACK
/*
const BASE = import.meta.env.VITE_API_BASE || ""; // o pegá acá la URL

type JSONValue = any;

export async function apiGet<T = JSONValue>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    credentials: "include",
    headers: { "Accept": "application/json" },
  });
  if (!res.ok) throw new Error(await res.text().catch(() => "GET failed"));
  return res.json();
}

export async function apiPost<T = JSONValue>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json", "Accept": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(await res.text().catch(() => "POST failed"));
  return res.status === 204 ? (undefined as T) : res.json();
}

export function buildRedirect(to = "/loading") {
  return encodeURIComponent(`${window.location.origin}${to}`);
}
*/