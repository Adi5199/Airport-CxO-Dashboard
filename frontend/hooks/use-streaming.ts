"use client";
import { useState, useCallback } from "react";

interface StreamState {
  text: string;
  isStreaming: boolean;
  error: string | null;
}

export function useStreaming() {
  const [state, setState] = useState<StreamState>({ text: "", isStreaming: false, error: null });

  const stream = useCallback(async (query: string, date: string, history: { role: string; content: string }[]) => {
    setState({ text: "", isStreaming: true, error: null });

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, date, conversation_history: history }),
      });

      if (!res.ok) throw new Error(`API error: ${res.status}`);
      if (!res.body) throw new Error("No response body");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let accumulated = "";
      let fullResponse = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        accumulated += decoder.decode(value, { stream: true });
        const lines = accumulated.split("\n");
        accumulated = lines.pop() || "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          try {
            const data = JSON.parse(line.slice(6));
            if (data.token) {
              fullResponse += data.token;
              setState((s) => ({ ...s, text: fullResponse }));
            }
            if (data.done) {
              fullResponse = data.full_response || fullResponse;
              setState({ text: fullResponse, isStreaming: false, error: null });
              return fullResponse;
            }
          } catch {
            // skip parse errors
          }
        }
      }

      setState((s) => ({ ...s, isStreaming: false }));
      return fullResponse;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Stream failed";
      setState({ text: "", isStreaming: false, error: msg });
      return "";
    }
  }, []);

  return { ...state, stream };
}
