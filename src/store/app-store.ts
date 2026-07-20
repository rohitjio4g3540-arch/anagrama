import { create } from "zustand";
import type { Citation, StreamEvent } from "./types";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

type AppState = {
  messages: Message[];
  activeTool: string | null;
  currentAgent: string | null;
  citations: Citation[];
  isStreaming: boolean;

  addUserMessage: (content: string) => void;
  startAssistantMessage: () => void;
  appendAssistant: (text: string) => void;
  handleEvent: (event: StreamEvent) => void;
};

export const useAppStore = create<AppState>((set) => ({
  messages: [],
  activeTool: null,
  currentAgent: null,
  citations: [],
  isStreaming: false,

  addUserMessage: (content) =>
    set((state) => ({
      messages: [
        ...state.messages,
        { id: crypto.randomUUID(), role: "user", content },
      ],
    })),

  startAssistantMessage: () =>
    set((state) => ({
      isStreaming: true,
      messages: [
        ...state.messages,
        { id: crypto.randomUUID(), role: "assistant", content: "" },
      ],
    })),

  appendAssistant: (text) =>
    set((state) => {
      const messages = [...state.messages];
      const last = messages[messages.length - 1];

      if (last?.role === "assistant") {
        last.content += text;
      }

      return { messages };
    }),

  handleEvent: (event) =>
    set((state) => {
      switch (event.type) {
        case "tool":
          return { activeTool: event.name };

        case "handoff":
          return { currentAgent: event.to };

        case "complete":
          return {
            citations: event.citations,
            isStreaming: false,
            activeTool: null,
          };

        default:
          return state;
      }
    }),
}));
