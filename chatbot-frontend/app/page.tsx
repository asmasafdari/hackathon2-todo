"use client";

import { useAuth, SignInButton, SignedIn, SignedOut } from "@clerk/nextjs";
import { ChatInterface } from "@/components/ChatInterface";

export default function Home() {
  const { userId } = useAuth();

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto py-8 px-4">
        <SignedOut>
          <div className="text-center py-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Todo AI Assistant</h2>
            <p className="text-gray-600 mb-8">Sign in to chat with AI and manage your tasks</p>
            <SignInButton mode="modal">
              <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-lg">
                Get Started
              </button>
            </SignInButton>
          </div>
        </SignedOut>

        <SignedIn>
          <header className="mb-8 text-center">
            <p className="text-gray-600">
              Chat with AI to manage your tasks naturally
            </p>
          </header>

          <ChatInterface userId={userId || ""} />

          <footer className="mt-8 text-center text-sm text-gray-500">
            <p>Try saying: &quot;Add a task to buy groceries&quot; or &quot;Show my pending tasks&quot;</p>
          </footer>
        </SignedIn>
      </div>
    </main>
  );
}
