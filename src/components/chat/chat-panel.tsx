"use client";

import { useState } from "react";
import { streamChat } from "@/lib/stream";
import { useAppStore } from "@/store/app-store";

export function ChatPanel() {
  const [input, setInput] = useState("");

  const {
    messages,
    addUserMessage,
    startAssistantMessage,
    appendAssistant,
    handleEvent,
  } = useAppStore();

  async function send() {
    if (!input.trim()) return;

    addUserMessage(input);
    startAssistantMessage();

    await streamChat(
      {
        message: input,
      },
      (event) => {
        if (event.type === "delta") {
          appendAssistant(event.content);
        } else {
          handleEvent(event);
        }
      }
    );

    setInput("");
  }

  return (
    <div>
      <div>
        {messages.map((m) => (
          <div key={m.id}>{m.content}</div>
        ))}
      </div>

      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />

      <button onClick={send}>
        Send
      </button>
    </div>
  );
}
