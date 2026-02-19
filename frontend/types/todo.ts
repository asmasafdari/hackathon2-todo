export type TodoPriority = "low" | "medium" | "high" | "urgent";

export interface Todo {
  id: string;
  title: string;
  description: string | null;
  completed: boolean;
  priority: TodoPriority | null;
  tags: string[] | null;
  due_date: string | null;
  remind_at: string | null;
  recurrence_rule: string | null;
  created_at: string;
}

export interface TodoCreate {
  title: string;
  description?: string;
}

export interface TodoUpdate {
  title?: string;
  description?: string;
}
