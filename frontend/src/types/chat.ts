export interface ChatMessage {
  role: string;
  content: string;
}

export interface ChatRequest {
  model_path: string;
  messages: ChatMessage[];
  temperature?: number;
  max_tokens?: number;
}

export interface ChatResponse {
  role: string;
  content: string;
}

