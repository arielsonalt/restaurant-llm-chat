import React, { useEffect, useState } from "react";
import { api } from "../api";

export default function ChatWidget({ token }) {
  const [conversationId, setConversationId] = useState(null);
  const [text, setText] = useState("");
  const [messages, setMessages] = useState([]);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api("/chat/conversations", { method: "POST", token })
      .then((d) => setConversationId(d.conversation_id))
      .catch(() => {});
  }, [token]);

  async function send() {
    if (!text.trim() || !conversationId) return;
    const userMsg = { role: "user", content: text };
    setMessages((m) => [...m, userMsg]);
    setText("");
    setBusy(true);

    try {
      const out = await api(`/chat/conversations/${conversationId}`, {
        method: "POST",
        token,
        body: { message: userMsg.content },
      });
      setMessages((m) => [...m, { role: "assistant", content: out.response }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={{ border: "1px solid #ddd", borderRadius: 10, padding: 12 }}>
      <strong>Private Assistant (per-user chat)</strong>
      <div style={{ height: 220, overflow: "auto", marginTop: 10, padding: 8, background: "#fafafa" }}>
        {messages.map((m, idx) => (
          <div key={idx} style={{ marginBottom: 10 }}>
            <b>{m.role}:</b> {m.content}
          </div>
        ))}
      </div>

      <div style={{ display: "flex", gap: 8, marginTop: 10 }}>
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Ask about delivery, reservations, menu, info..."
          style={{ flex: 1 }}
        />
        <button onClick={send} disabled={busy || !conversationId}>
          Send
        </button>
      </div>
    </div>
  );
}
