import { createContext, useContext, useEffect, useState, type FormEvent } from "react";
import { Outlet } from "react-router-dom";
import { api } from "../api";

const LogoutContext = createContext<() => void>(() => {});
export const useLogout = () => useContext(LogoutContext);

export default function RequireOwner() {
  const [owner, setOwner] = useState<boolean | null>(null);
  const [apiDown, setApiDown] = useState(false);

  useEffect(() => {
    api.me().then((r) => setOwner(r.owner)).catch(() => setApiDown(true));
  }, []);

  if (apiDown) return <div className="center error">Can't reach the DocuChat API. Is the backend running on :8000?</div>;
  if (owner === null) return <div className="center muted">Loading…</div>;
  if (!owner) return <LoginScreen onDone={() => setOwner(true)} />;

  const logout = async () => {
    await api.logout();
    setOwner(false);
  };
  return (
    <LogoutContext.Provider value={logout}>
      <Outlet />
    </LogoutContext.Provider>
  );
}

export function Logo({ size = 22 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden>
      <rect width="32" height="32" rx="7" fill="var(--accent)" />
      <path d="M10 7h8l5 5v13H10z" fill="#fff" />
      <path d="M18 7v5h5" fill="none" stroke="var(--accent)" strokeWidth="1.5" />
      <rect x="12.5" y="16" width="8" height="2.4" rx="1" fill="#fbbf24" />
      <rect x="12.5" y="20" width="5" height="2" rx="1" fill="#c7d2fe" />
    </svg>
  );
}

function LoginScreen({ onDone }: { onDone: () => void }) {
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await api.login(password);
      onDone();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    }
  };

  return (
    <main className="center">
      <form className="panel login" onSubmit={submit}>
        <h1 className="logo big">
          <Logo size={28} /> DocuChat
        </h1>
        <p className="muted">Ask questions about a PDF. Answers point to the exact passage, or say the document doesn't cover it.</p>
        <label className="label" htmlFor="pw">
          Password
        </label>
        <input id="pw" type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoFocus required />
        {error && <p className="error">{error}</p>}
        <button className="btn btn-primary" type="submit">
          Log in
        </button>
      </form>
    </main>
  );
}
