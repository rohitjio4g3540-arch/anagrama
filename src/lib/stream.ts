import { API_URL } from "./api";
import type { ChatRequest, StreamEvent } from "./types";

export async function streamChat(
  body: ChatRequest,
  onEvent: (event: StreamEvent) => void
) {
  const response = await fetch(`${API_URL}/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error(`Stream failed: ${response.status}`);
  }

  if (!response.body) {
    throw new Error("Missing response body");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();

    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    const chunks = buffer.split(/\n\s*\n/);
    buffer = chunks.pop() ?? "";

    for (const chunk of chunks) {
      const line = chunk
        .split("\n")
        .find((l) => l.startsWith("data:"));

      if (!line) continue;

      const event = JSON.parse(line.slice(5).trim()) as StreamEvent;
      onEvent(event);
    }
  }
}
