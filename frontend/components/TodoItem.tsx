"use client";

import { useState } from "react";
import { Todo } from "@/types/todo";

const PRIORITY_STYLES: Record<string, string> = {
  low: "bg-yellow-100 text-yellow-700",
  medium: "bg-green-100 text-green-700",
  high: "bg-pink-100 text-pink-700",
  urgent: "bg-red-100 text-red-600",
};

interface TodoItemProps {
  todo: Todo;
  onToggle: (id: string) => void;
  onUpdate: (id: string, title: string, description: string | null) => void;
  onDelete: (id: string) => void;
}

export default function TodoItem({
  todo,
  onToggle,
  onUpdate,
  onDelete,
}: TodoItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(todo.title);
  const [editDescription, setEditDescription] = useState(todo.description || "");

  const handleSave = () => {
    if (editTitle.trim()) {
      onUpdate(todo.id, editTitle.trim(), editDescription.trim() || null);
      setIsEditing(false);
    }
  };

  const handleCancel = () => {
    setEditTitle(todo.title);
    setEditDescription(todo.description || "");
    setIsEditing(false);
  };

  const formattedDate = new Date(todo.created_at).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  if (isEditing) {
    return (
      <li className="bg-white border border-pink-100 rounded-2xl p-4 shadow-sm">
        <div className="space-y-3">
          <input
            type="text"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            className="w-full px-3 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-pink-300 text-gray-800"
            placeholder="Title"
          />
          <textarea
            value={editDescription}
            onChange={(e) => setEditDescription(e.target.value)}
            className="w-full px-3 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-pink-300 text-gray-800 resize-none"
            placeholder="Description (optional)"
            rows={2}
          />
          <div className="flex gap-2">
            <button
              onClick={handleSave}
              className="px-3 py-1.5 bg-green-400 text-white rounded-lg hover:bg-green-500 text-sm font-medium transition-colors"
            >
              Save
            </button>
            <button
              onClick={handleCancel}
              className="px-3 py-1.5 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 text-sm font-medium transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      </li>
    );
  }

  return (
    <li className="bg-white border border-gray-100 rounded-2xl p-4 shadow-sm flex items-start gap-3 hover:border-pink-100 transition-colors">
      <input
        type="checkbox"
        checked={todo.completed}
        onChange={() => onToggle(todo.id)}
        className="mt-1 h-4 w-4 rounded border-gray-300 text-pink-400 focus:ring-pink-300 cursor-pointer"
      />
      <div className="flex-1 min-w-0">
        <h3
          className={`text-base font-medium ${
            todo.completed ? "line-through text-gray-300" : "text-gray-800"
          }`}
        >
          {todo.title}
        </h3>
        {todo.priority && (
          <span className={`inline-block mt-1.5 px-2 py-0.5 rounded-full text-xs font-medium ${PRIORITY_STYLES[todo.priority]}`}>
            {todo.priority}
          </span>
        )}
        {todo.description && (
          <p
            className={`mt-1 text-sm leading-relaxed ${
              todo.completed ? "text-gray-300" : "text-gray-500"
            }`}
          >
            {todo.description}
          </p>
        )}
        {todo.tags && todo.tags.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {todo.tags.map((tag) => (
              <span key={tag} className="inline-block px-2 py-0.5 bg-yellow-100 text-yellow-700 text-xs rounded-full">
                {tag}
              </span>
            ))}
          </div>
        )}
        {todo.due_date && (
          <p className={`mt-1 text-xs font-medium ${
            !todo.completed && new Date(todo.due_date) < new Date() ? "text-red-400" : "text-gray-400"
          }`}>
            Due: {new Date(todo.due_date).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}
          </p>
        )}
        <p className="mt-2 text-xs text-gray-300">Created {formattedDate}</p>
      </div>
      <div className="flex gap-2">
        <button
          onClick={() => setIsEditing(true)}
          className="text-gray-300 hover:text-green-500 text-sm transition-colors"
        >
          Edit
        </button>
        <button
          onClick={() => {
            if (confirm("Are you sure you want to delete this todo?")) {
              onDelete(todo.id);
            }
          }}
          className="text-gray-300 hover:text-pink-500 text-sm transition-colors"
        >
          Delete
        </button>
      </div>
    </li>
  );
}
