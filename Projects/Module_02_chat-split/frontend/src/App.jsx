import { useEffect, useState } from "react";

export default function App() {
  const [message, setMessage] = useState("");
  const [time, setTime] = useState("");
  const [error, setError] = useState(null);

  useEffect(() => {
    // 두 엔드포인트는 서로 독립적이라 병렬로 보낸다(Promise.all).
    // fetch는 네트워크 실패에서만 reject하므로 res.ok로 HTTP 에러도 잡는다.
    async function load() {
      try {
        const [helloRes, timeRes] = await Promise.all([
          fetch("/api/hello"),
          fetch("/api/time"),
        ]);
        if (!helloRes.ok) throw new Error(`HTTP ${helloRes.status}`);
        if (!timeRes.ok) throw new Error(`HTTP ${timeRes.status}`);
        const hello = await helloRes.json();
        const t = await timeRes.json();
        setMessage(hello.message);
        setTime(t.time);
      } catch (err) {
        setError(err.message);
      }
    }

    load();
  }, []);

  return (
    <main style={{ fontFamily: "system-ui", padding: "2rem" }}>
      <h1>Hello Full-Stack</h1>
      {error ? (
        <p style={{ color: "crimson" }}>Error: {error}</p>
      ) : (
        <p>
          {message || "Loading…"}
          {time && <span style={{ color: "#888" }}> · 서버 시각: {time}</span>}
        </p>
      )}
    </main>
  );
}
