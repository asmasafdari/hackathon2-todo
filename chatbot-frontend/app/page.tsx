"use client";

import { useAuth, SignInButton, SignedIn, SignedOut } from "@clerk/nextjs";
import { ChatInterface } from "@/components/ChatInterface";

export default function Home() {
  const { userId } = useAuth();

  return (
    <main className="min-h-screen">
      <div className="max-w-3xl mx-auto py-10 px-4">
        <SignedOut>
          <div className="text-center py-24">
            <div className="inline-flex items-center gap-2 mb-6 px-3 py-1 bg-pink-100 text-pink-500 rounded-full text-sm font-medium">
              ✦ AI-powered task management
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-4 tracking-tight leading-tight">
              Chat with AI.<br />Manage tasks naturally.
            </h1>
            <p className="text-gray-500 mb-10 max-w-sm mx-auto leading-relaxed">
              Ask your assistant to add, complete, or organise your tasks — all in plain conversation.
            </p>
            <SignInButton mode="modal">
              <button className="px-8 py-3 bg-pink-400 text-white rounded-full hover:bg-pink-500 font-medium transition-colors text-base">
                Get Started
              </button>
            </SignInButton>
          </div>
        </SignedOut>

        <SignedIn>
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight">AI Assistant</h1>
            <p className="text-gray-500 mt-1 text-sm">Chat naturally to manage your tasks.</p>
          </div>

          <ChatInterface userId={userId || ""} />
        </SignedIn>
      </div>
    </main>
  );
}
