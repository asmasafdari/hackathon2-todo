"use client";

import { useState, useEffect } from "react";
import { useAuth, SignInButton, SignedIn, SignedOut } from "@clerk/nextjs";
import { Todo } from "@/types/todo";
import {
  fetchTodos,
  createTodo,
  updateTodo,
  deleteTodo,
  toggleTodo,
  setAuthToken,
} from "@/lib/api";
import TodoList from "@/components/TodoList";
import TodoForm from "@/components/TodoForm";

export default function Home() {
  const { isSignedIn, getToken } = useAuth();
  const [todos, setTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadTodos = async () => {
    try {
      setLoading(true);
      setError(null);
      const token = await getToken();
      if (token) setAuthToken(token);
      const data = await fetchTodos();
      setTodos(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load todos");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isSignedIn) {
      loadTodos();
    } else {
      setLoading(false);
    }
  }, [isSignedIn]);

  const handleCreate = async (title: string, description: string | null) => {
    try {
      setError(null);
      const token = await getToken();
      if (token) setAuthToken(token);
      const newTodo = await createTodo({ title, description: description || undefined });
      setTodos((prev) => [newTodo, ...prev]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create todo");
    }
  };

  const handleToggle = async (id: string) => {
    try {
      setError(null);
      const token = await getToken();
      if (token) setAuthToken(token);
      const updated = await toggleTodo(id);
      setTodos((prev) =>
        prev.map((todo) => (todo.id === id ? updated : todo))
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to toggle todo");
    }
  };

  const handleUpdate = async (
    id: string,
    title: string,
    description: string | null
  ) => {
    try {
      setError(null);
      const token = await getToken();
      if (token) setAuthToken(token);
      const updated = await updateTodo(id, { title, description: description || undefined });
      setTodos((prev) =>
        prev.map((todo) => (todo.id === id ? updated : todo))
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update todo");
    }
  };

  const handleDelete = async (id: string) => {
    try {
      setError(null);
      const token = await getToken();
      if (token) setAuthToken(token);
      await deleteTodo(id);
      setTodos((prev) => prev.filter((todo) => todo.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete todo");
    }
  };

  return (
    <main className="max-w-2xl mx-auto px-6 py-10">
      <SignedOut>
        <div className="text-center py-24">
          <div className="inline-flex items-center gap-2 mb-6 px-3 py-1 bg-pink-100 text-pink-500 rounded-full text-sm font-medium">
            ✦ Simple task management
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4 tracking-tight leading-tight">
            Stay organised.<br />Get things done.
          </h1>
          <p className="text-gray-500 mb-10 max-w-sm mx-auto leading-relaxed">
            A minimal, beautiful way to track your daily tasks and keep your mind clear.
          </p>
          <SignInButton mode="modal">
            <button className="px-8 py-3 bg-pink-400 text-white rounded-full hover:bg-pink-500 font-medium transition-colors text-base">
              Get Started
            </button>
          </SignInButton>
        </div>
      </SignedOut>

      <SignedIn>
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">My Tasks</h1>
          <p className="text-gray-500 mt-1 text-sm">Track, organise, and accomplish your daily tasks.</p>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-100 rounded-xl text-red-600 text-sm">
            {error}
          </div>
        )}

        <TodoForm onSubmit={handleCreate} />

        <div className="mt-8">
          <div className="flex items-center gap-2 mb-4">
            <h2 className="text-base font-semibold text-gray-700">Tasks</h2>
            <span className="px-2 py-0.5 bg-yellow-100 text-yellow-700 rounded-full text-xs font-medium">
              {todos.length}
            </span>
          </div>
          <TodoList
            todos={todos}
            loading={loading}
            onToggle={handleToggle}
            onUpdate={handleUpdate}
            onDelete={handleDelete}
          />
        </div>
      </SignedIn>
    </main>
  );
}
