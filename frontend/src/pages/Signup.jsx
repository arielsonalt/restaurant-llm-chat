import React, { useState } from "react";
import { api } from "../api";
import { setTokens } from "../auth";

export default function Signup({ onAuthed }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");

  async function submit(e) {
    e.preventDefault();
    setErr("");
    try {
      const tokens = await api("/auth/signup", { method: "POST", body: { email, password } });
      setTokens(tokens);
      onAuthed();
    } catch (e2) {
      setErr(e2.message);
    }
  }

  return (
    <form onSubmit={submit} style={{ display: "grid", gap: 8, maxWidth: 360 }}>
      <h3>Sign up</h3>
      <input placeholder="email" value={email} onChange={(e) => setEmail(e.target.value)} />
      <input placeholder="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      <button type="submit">Create account</button>
      {err && <div style={{ color: "crimson" }}>{err}</div>}
    </form>
  );
}
