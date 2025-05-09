import React, { useEffect, useState } from "react";

const BACKEND_URL = import.meta.env.VITE_API_URL || "http://localhost:8081";

/**
 * BackendStatusLight component displays a colored indicator showing backend API status.
 *
 * - Polls the backend /health endpoint every 5 seconds
 * - Green (limegreen) if backend is online, gray if offline
 * - Tooltip shows current status
 */
export function BackendStatusLight() {
  const [online, setOnline] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const checkHealth = async () => {
      try {
        const res = await fetch(`${BACKEND_URL.replace(/\/api\/?$/, '')}/health`);
        if (!cancelled) setOnline(res.ok);
      } catch {
        if (!cancelled) setOnline(false);
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 5000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  return (
    <span
      style={{
        display: "inline-block",
        width: 12,
        height: 12,
        borderRadius: "50%",
        background: online ? "limegreen" : "gray",
        marginRight: 8,
        border: "1px solid #222",
        verticalAlign: "middle"
      }}
      title={online ? "Backend online" : "Backend offline"}
    />
  );
} 