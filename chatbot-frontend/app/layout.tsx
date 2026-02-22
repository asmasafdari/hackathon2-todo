import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";
import { NavAuth } from "@/components/NavAuth";
import "./globals.css";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Tidylist AI",
  description: "Chat with AI to manage your tasks naturally.",
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
          <nav className="bg-white border-b border-pink-100 px-6 py-4 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span className="text-pink-400 text-lg">✦</span>
              <h1 className="text-lg font-semibold text-gray-800 tracking-tight">Tidylist AI</h1>
            </div>
            <NavAuth />
          </nav>
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}
