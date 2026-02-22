import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";
import NavBar from "@/components/NavBar";
import "./globals.css";

export const metadata: Metadata = {
  title: "Tidylist",
  description: "A minimal, beautiful way to track your daily tasks.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body className="bg-pink-50 min-h-screen">
          <NavBar />
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}
