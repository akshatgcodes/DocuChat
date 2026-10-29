import type { Answer, Doc } from "./types";

// Empty in dev (Vite proxies /api). Set VITE_API_URL when the API is elsewhere.
export const BASE = import.meta.env.VITE_API_URL ?? "";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE}${path}`, { ...init, credentials: "include" });
  } catch {
    throw new ApiError(0, "Can't reach the DocuChat server");
  }
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const msg = typeof body.detail === "string" ? body.detail : res.statusText;
    throw new ApiError(res.status, msg);
  }
  return res.status === 204 ? (undefined as T) : res.json();
}

const json = (method: string, body?: unknown): RequestInit => ({
  method,
  headers: { "Content-Type": "application/json" },
  body: body === undefined ? undefined : JSON.stringify(body),
});

export const api = {
  me: () => request<{ owner: boolean }>("/api/auth/me"),
  login: (password: string) => request("/api/auth/login", json("POST", { password })),
  logout: () => request("/api/auth/logout", json("POST")),

  documents: () => request<Doc[]>("/api/documents"),
  document: (id: number) => request<Doc>(`/api/documents/${id}`),
  upload: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<Doc>("/api/documents", { method: "POST", body: form });
  },
  remove: (id: number) => request<void>(`/api/documents/${id}`, { method: "DELETE" }),

  ask: (id: number, question: string) => request<Answer>(`/api/documents/${id}/ask`, json("POST", { question })),
  messages: (id: number) => request<Answer[]>(`/api/documents/${id}/messages`),
  clear: (id: number) => request<void>(`/api/documents/${id}/messages`, { method: "DELETE" }),

  pageUrl: (id: number, page: number, chunk?: number) =>
    `${BASE}/api/documents/${id}/pages/${page}.png${chunk !== undefined ? `?chunk=${chunk}` : ""}`,
};
