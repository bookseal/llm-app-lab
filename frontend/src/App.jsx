import { useEffect, useState } from "react";

export default function App() {
  const [message, setMessage] = useState("");
  const [error, setError] = useState(null);

  useEffect(() => {
    // fetch는 네트워크 실패에서만 reject하므로 res.ok로 HTTP 에러도 잡는다.
    async function loadMessage() {
      try {
        const res = await fetch("/api/hello");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        setMessage(data.message);
      } catch (err) {
        setError(err.message);
      }
    }

    loadMessage();
  }, []);

  return (
    <main style={{ fontFamily: "system-ui", padding: "2rem" }}>
      <h1>Hello Full-Stack</h1>
      {error ? (
        <p style={{ color: "crimson" }}>Error: {error}</p>
      ) : (
        <p>{message || "Loading…"}</p>
      )}
    </main>
  );
}
