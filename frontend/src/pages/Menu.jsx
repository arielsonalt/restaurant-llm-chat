import React, { useEffect, useState } from "react";
import { api } from "../api";
import ChatWidget from "../components/ChatWidget";

export default function Menu({ tokens }) {
  const [items, setItems] = useState([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    api("/menu")
      .then(setItems)
      .catch((e) => setErr(e.message));
  }, []);

  return (
    <div style={{ display: "grid", gap: 12 }}>
      <h3>Menu</h3>
      {err && <div style={{ color: "crimson" }}>{err}</div>}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12 }}>
        {items.map((i) => (
          <div key={i.id} style={{ border: "1px solid #ddd", borderRadius: 8, padding: 12 }}>
            <strong>{i.name}</strong>
            <div>{i.category}</div>
            <div style={{ marginTop: 6, opacity: 0.85 }}>{i.description || ""}</div>
            <div style={{ marginTop: 10 }}>${i.price.toFixed(2)}</div>

            <div style={{ marginTop: 10, fontSize: 12, opacity: 0.8 }}>
              Customization UI goes here (size/toppings/sides/spice/remove).
            </div>
          </div>
        ))}
      </div>

      {tokens ? (
        <ChatWidget token={tokens.access_token} />
      ) : (
        <div style={{ opacity: 0.7 }}>Login to use the private chat assistant.</div>
      )}
    </div>
  );
}
