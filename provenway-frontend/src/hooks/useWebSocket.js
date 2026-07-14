/**
 * src/hooks/useWebSocket.js
 * ─────────────────────────
 * Generic WebSocket hook with auto-reconnect and cleanup.
 * Used by messaging and notifications.
 */
import { useEffect, useRef } from "react";
import { useAuthStore } from "../stores/authStore";

export function useWebSocket(url, { onMessage, enabled = true } = {}) {
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  useEffect(() => {
    if (!enabled || !url) return;

    function connect() {
      const token = useAuthStore.getState().accessToken;
      // Pass JWT as query param (Channels reads this in scope["query_string"])
      const wsUrl = token ? `${url}?token=${token}` : url;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage?.(data);
        } catch {
          // Non-JSON message — ignore
        }
      };

      ws.onclose = () => {
        // Auto-reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(connect, 3000);
      };
    }

    connect();

    return () => {
      clearTimeout(reconnectTimeoutRef.current);
      wsRef.current?.close();
    };
  }, [url, enabled]); // eslint-disable-line react-hooks/exhaustive-deps

  const send = (data) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  };

  return { send };
}
