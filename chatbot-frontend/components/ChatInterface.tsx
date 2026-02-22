"use client";

import { useState, useRef, useEffect } from "react";
import { useAuth } from "@clerk/nextjs";
import { sendMessage, setAuthToken, ChatMessage, ChatResponse } from "@/lib/api";

interface ChatInterfaceProps {
  userId: string;
}

export function ChatInterface({ userId }: ChatInterfaceProps) {
  const { getToken } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    setIsLoading(true);

    // Add user message to chat
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now().toString(),
        role: "user",
        content: userMessage,
        created_at: new Date().toISOString(),
      },
    ]);

    try {
      // Get fresh Clerk token for each request
      const token = await getToken();
      if (token) setAuthToken(token);

      const response: ChatResponse = await sendMessage({
        userId,
        message: userMessage,
        conversationId: conversationId || undefined,
      });

      // Store conversation ID for future messages
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      // Add assistant response to chat
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: response.response,
          tool_calls: response.tool_calls,
          created_at: new Date().toISOString(),
        },
      ]);
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: "Sorry, I encountered an error. Please try again.",
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-pink-100 shadow-sm overflow-hidden">
      {/* Chat Messages */}
      <div className="h-[500px] overflow-y-auto p-5 space-y-4 chat-container">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <div className="text-3xl mb-3">✦</div>
            <p className="text-gray-700 font-medium mb-1">How can I help today?</p>
            <p className="text-gray-400 text-sm mb-6">I can add, list, complete, or delete your tasks.</p>
            <div className="inline-flex flex-col gap-2 text-sm text-gray-500">
              <span className="px-3 py-1.5 bg-yellow-100 text-yellow-700 rounded-full">&quot;Add a task to buy groceries&quot;</span>
              <span className="px-3 py-1.5 bg-green-100 text-green-700 rounded-full">&quot;Show my pending tasks&quot;</span>
              <span className="px-3 py-1.5 bg-pink-100 text-pink-600 rounded-full">&quot;Mark the meeting task as done&quot;</span>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${
              message.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm ${
                message.role === "user"
                  ? "bg-pink-400 text-white rounded-br-sm"
                  : "bg-green-50 text-gray-800 rounded-bl-sm border border-green-100"
              }`}
            >
              <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
              {message.tool_calls && message.tool_calls.length > 0 && (
                <div className="mt-2 pt-2 border-t border-pink-200">
                  <p className="text-xs opacity-70">
                    Used: {message.tool_calls.map((t) => t.tool).join(", ")}
                  </p>
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-green-50 border border-green-100 rounded-2xl rounded-bl-sm px-4 py-3">
              <div className="flex space-x-1.5">
                <div className="w-2 h-2 bg-pink-300 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-pink-300 rounded-full animate-bounce delay-100" />
                <div className="w-2 h-2 bg-pink-300 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit} className="border-t border-pink-100 p-4 bg-pink-50">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me anything about your tasks..."
            className="flex-1 px-4 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-pink-300 focus:border-transparent bg-white text-gray-800 placeholder-gray-300 text-sm"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-5 py-2.5 bg-pink-400 text-white rounded-xl hover:bg-pink-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors font-medium text-sm"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}
