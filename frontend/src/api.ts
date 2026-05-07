// Связь с FastAPI backend
export const API_BASE = 'http://127.0.0.1:8000';

export async function fetchDefaultConfig() {
  const r = await fetch(`${API_BASE}/api/config/default`);
  if (!r.ok) throw new Error(`Config fetch failed: ${r.status}`);
  return r.json();
}

export async function calcAll(inputs: Record<string, unknown>) {
  const r = await fetch(`${API_BASE}/api/calc/all`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(inputs),
  });
  if (!r.ok) {
    const txt = await r.text();
    throw new Error(`Calc failed: ${r.status} — ${txt}`);
  }
  return r.json();
}
