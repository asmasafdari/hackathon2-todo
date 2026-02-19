const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

// Auth token management
let _authToken: string | null = null;

export function setAuthToken(token: string | null) {
  _authToken = token;
}

function getAuthHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (_authToken) {
    headers["Authorization"] = `Bearer ${_authToken}`;
  }
  return headers;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  tool_calls?: ToolCall[];
  created_at: string;
}

export interface ToolCall {
  tool: string;
  parameters: Record<string, unknown>;
  result?: Record<string, unknown>;
}

export interface ChatResponse {
  conversation_id: string;
  response: string;
  tool_calls?: ToolCall[];
}

export interface SendMessageRequest {
  userId: string;
  message: string;
  conversationId?: string;
}

export async function sendMessage({
  userId,
  message,
  conversationId,
}: SendMessageRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/${userId}/chat`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({
      conversation_id: conversationId,
      message,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || "Failed to send message");
  }

  return response.json();
}

export async function getConversations(userId: string): Promise<Conversation[]> {
  const response = await fetch(`${API_BASE_URL}/api/${userId}/conversations`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error("Failed to fetch conversations");
  }

  return response.json();
}

export async function getConversationMessages(
  userId: string,
  conversationId: string
): Promise<ChatMessage[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/${userId}/conversations/${conversationId}/messages`,
    { headers: getAuthHeaders() }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch messages");
  }

  return response.json();
}

export interface Conversation {
  id: string;
  user_id: string;
  title?: string;
  created_at: string;
  updated_at: string;
  message_count?: number;
}
