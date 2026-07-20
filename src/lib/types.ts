export type ChatRequest = {
  message: string;
  project_id?: string | null;
  conversation_id?: string | null;
};

export type Citation = {
  title: string;
  source_id: string;
};

export type StreamEvent =
  | {
      type: "tool";
      name: string;
    }
  | {
      type: "handoff";
      from: string;
      to: string;
    }
  | {
      type: "delta";
      content: string;
    }
  | {
      type: "complete";
      specialist: string;
      citations: Citation[];
    }
  | {
      type: "error";
      message: string;
    };
