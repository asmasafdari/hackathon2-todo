"use client";

import { SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/nextjs";

export function NavAuth() {
  return (
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
  );
}
