"use client";

import { useState } from "react";
import { Todo } from "@/types/todo";

const PRIORITY_STYLES: Record<string, string> = {
  low: "bg-gray-100 text-gray-600",
  medium: "bg-blue-100 text-blue-700",
  high: "bg-orange-100 text-orange-700",
  urgent: "bg-red-100 text-red-700",
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
      <li className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
        <div className="space-y-3">
          <input
            type="text"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Title"
          />
          <textarea
            value={editDescription}
            onChange={(e) => setEditDescription(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Description (optional)"
            rows={2}
          />
          <div className="flex gap-2">
            <button
              onClick={handleSave}
              className="px-3 py-1 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
            >
              Save
            </button>
            <button
              onClick={handleCancel}
              className="px-3 py-1 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 text-sm"
            >
              Cancel
            </button>
          </div>
        </div>
      </li>
    );
  }

  return (
    <li className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm flex items-start gap-3">
      <input
        type="checkbox"
        checked={todo.completed}
        onChange={() => onToggle(todo.id)}
        className="mt-1 h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
      />
      <div className="flex-1 min-w-0">
        <h3
          className={`text-lg font-medium ${
            todo.completed ? "line-through text-gray-400" : "text-gray-900"
          }`}
        >
          {todo.title}
        </h3>
        {todo.priority && (
          <span className={`inline-block mt-1 px-2 py-0.5 rounded-full text-xs font-medium ${PRIORITY_STYLES[todo.priority]}`}>
            {todo.priority}
          </span>
        )}
        {todo.description && (
          <p
            className={`mt-1 text-sm ${
              todo.completed ? "text-gray-400" : "text-gray-600"
            }`}
          >
            {todo.description}
          </p>
        )}
        {todo.tags && todo.tags.length > 0 && (
          <div className="mt-1 flex flex-wrap gap-1">
            {todo.tags.map((tag) => (
              <span key={tag} className="inline-block px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full">
                {tag}
              </span>
            ))}
          </div>
        )}
        {todo.due_date && (
          <p className={`mt-1 text-xs font-medium ${
            !todo.completed && new Date(todo.due_date) < new Date() ? "text-red-500" : "text-gray-400"
          }`}>
            Due: {new Date(todo.due_date).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}
          </p>
        )}
        <p className="mt-2 text-xs text-gray-400">Created: {formattedDate}</p>
      </div>
      <div className="flex gap-2">
        <button
          onClick={() => setIsEditing(true)}
          className="text-gray-400 hover:text-blue-600 text-sm"
        >
          Edit
        </button>
        <button
          onClick={() => {
            if (confirm("Are you sure you want to delete this todo?")) {
              onDelete(todo.id);
            }
          }}
          className="text-gray-400 hover:text-red-600 text-sm"
        >
          Delete
        </button>
      </div>
    </li>
  );
}
