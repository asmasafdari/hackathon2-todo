"use client";

import { SignInButton, SignedIn, SignedOut, UserButton } from "@clerk/nextjs";

export default function NavBar() {
  return (
    <nav className="bg-white border-b border-pink-100 px-6 py-4 flex justify-between items-center">
      <div className="flex items-center gap-2">
        <span className="text-pink-400 text-lg">✦</span>
        <h1 className="text-lg font-semibold text-gray-800 tracking-tight">Tidylist</h1>
      </div>
      <div>
        <SignedOut>
          <SignInButton mode="modal">
            <button className="px-4 py-2 bg-pink-400 text-white rounded-full hover:bg-pink-500 text-sm font-medium transition-colors">
              Sign In
            </button>
          </SignInButton>
        </SignedOut>
        <SignedIn>
          <UserButton afterSignOutUrl="/" />
        </SignedIn>
      </div>
    </nav>
  );
}
