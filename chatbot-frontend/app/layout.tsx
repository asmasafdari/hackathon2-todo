import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";
import { NavAuth } from "@/components/NavAuth";
import "./globals.css";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Todo AI Chatbot",
  description: "AI-powered chatbot for managing your todos",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body className="antialiased">
          <nav className="bg-white shadow-sm border-b border-gray-200 px-6 py-3 flex justify-between items-center">
            <h1 className="text-lg font-semibold text-gray-900">Todo AI Assistant</h1>
            <NavAuth />
          </nav>
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}
