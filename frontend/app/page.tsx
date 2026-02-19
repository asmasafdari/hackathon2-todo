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
    <main className="max-w-2xl mx-auto p-6">
      <SignedOut>
        <div className="text-center py-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Welcome to Todo App</h2>
          <p className="text-gray-600 mb-8">Sign in to manage your tasks</p>
          <SignInButton mode="modal">
            <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-lg">
              Get Started
            </button>
          </SignInButton>
        </div>
      </SignedOut>

      <SignedIn>
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Your Todos</h1>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        <TodoForm onSubmit={handleCreate} />

        <div className="mt-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            Tasks ({todos.length})
          </h2>
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
