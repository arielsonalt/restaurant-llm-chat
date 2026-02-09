import React, { useEffect, useState } from "react";
import { getTokens, logout } from "./auth";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Menu from "./pages/Menu";

export default function App() {
  const [page, setPage] = useState("menu");
  const [tokens, setTokens] = useState(getTokens());

  useEffect(() => setTokens(getTokens()), []);

  return (
    <div style={{ fontFamily: "system-ui", maxWidth: 1000, margin: "0 auto", padding: 16 }}>
      <header style={{ display: "flex", gap: 12, alignItems: "center", justifyContent: "space-between" }}>
        <h2>Restaurant</h2>
        <nav style={{ display: "flex", gap: 8 }}>
          <button onClick={() => setPage("menu")}>Menu</button>
          {!tokens && <button onClick={() => setPage("login")}>Login</button>}
          {!tokens && <button onClick={() => setPage("signup")}>Sign up</button>}
          {tokens && (
            <button
              onClick={() => {
                logout();
                setTokens(null);
              }}
            >
              Logout
            </button>
          )}
        </nav>
      </header>

      <hr />

      {page === "menu" && <Menu tokens={tokens} />}
      {page === "login" && <Login onAuthed={() => setTokens(getTokens())} />}
      {page === "signup" && <Signup onAuthed={() => setTokens(getTokens())} />}
    </div>
  );
}
