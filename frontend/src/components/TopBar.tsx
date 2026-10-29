import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { Logo, useLogout } from "./RequireOwner";

export default function TopBar({ children }: { children?: ReactNode }) {
  const logout = useLogout();
  return (
    <header className="topbar">
      <Link to="/" className="logo">
        <Logo /> <span className="logo-text">DocuChat</span>
      </Link>
      <div className="topbar-mid">{children}</div>
      <button className="link-btn" onClick={logout}>
        Log out
      </button>
    </header>
  );
}
