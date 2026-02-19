"""Desktop Todo Application - A simple task management CLI."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Status(Enum):
    PENDING = "pending"
    COMPLETED = "completed"


@dataclass
class Task:
    """Represents a single task."""
    id: int
    title: str
    description: str = ""
    status: Status = Status.PENDING
    created_at: datetime = field(default_factory=datetime.now)

    def mark_complete(self) -> None:
        self.status = Status.COMPLETED

    def mark_pending(self) -> None:
        self.status = Status.PENDING


class TaskManager:
    """Manages the in-memory list of tasks."""

    def __init__(self) -> None:
        self._tasks: list[Task] = []
        self._next_id: int = 1

    def add_task(self, title: str, description: str = "") -> Task:
        """Add a new task with the given title and description."""
        if not title.strip():
            raise ValueError("Task title cannot be empty")
        task = Task(id=self._next_id, title=title.strip(), description=description.strip())
        self._tasks.append(task)
        self._next_id += 1
        return task

    def update_task(self, task_id: int, title: str | None = None, description: str | None = None) -> Task:
        """Update a task's title and/or description."""
        task = self.get_task(task_id)
        if title is not None:
            if not title.strip():
                raise ValueError("Task title cannot be empty")
            task.title = title.strip()
        if description is not None:
            task.description = description.strip()
        return task

    def get_task(self, task_id: int) -> Task:
        """Get a task by ID."""
        for task in self._tasks:
            if task.id == task_id:
                return task
        raise ValueError(f"Task with ID {task_id} not found")

    def delete_task(self, task_id: int) -> None:
        """Delete a task by ID."""
        task = self.get_task(task_id)
        self._tasks.remove(task)

    def toggle_task(self, task_id: int) -> Task:
        """Toggle a task's completion status."""
        task = self.get_task(task_id)
        if task.status == Status.COMPLETED:
            task.mark_pending()
        else:
            task.mark_complete()
        return task

    def list_tasks(self) -> list[Task]:
        """Return all tasks."""
        return self._tasks.copy()


def print_table(tasks: list[Task]) -> None:
    """Print tasks in a formatted table."""
    if not tasks:
        print("\n  No tasks found.\n")
        return

    # Table header
    print()
    print(f"{'ID':<5} {'Status':<8} {'Title':<30} {'Description':<25} {'Created':<16}")
    print("-" * 84)

    # Table rows
    for task in tasks:
        status_icon = "[x]" if task.status == Status.COMPLETED else "[ ]"
        created = task.created_at.strftime("%Y-%m-%d %H:%M")
        title = task.title[:28] + ".." if len(task.title) > 30 else task.title
        desc = task.description[:23] + ".." if len(task.description) > 25 else task.description
        print(f"{task.id:<5} {status_icon:<8} {title:<30} {desc:<25} {created:<16}")

    print()


def print_menu() -> None:
    """Print the CLI menu."""
    print("=" * 40)
    print("       DESKTOP TODO APPLICATION")
    print("=" * 40)
    print("  1. List all tasks")
    print("  2. Add a new task")
    print("  3. Update a task")
    print("  4. Toggle task completion")
    print("  5. Delete a task")
    print("  6. Exit")
    print("=" * 40)


def get_input(prompt: str) -> str:
    """Get user input with validation."""
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        return ""


def main() -> None:
    """Main CLI menu loop."""
    manager = TaskManager()

    while True:
        print_menu()
        choice = get_input("Select an option (1-6): ")

        if choice == "1":
            print_table(manager.list_tasks())

        elif choice == "2":
            title = get_input("Enter task title: ")
            if not title:
                print("\n  Error: Task title cannot be empty.\n")
                continue
            description = get_input("Enter task description (optional): ")
            try:
                task = manager.add_task(title, description)
                print(f"\n  Task #{task.id} added successfully.\n")
            except ValueError as e:
                print(f"\n  Error: {e}\n")

        elif choice == "3":
            task_id_str = get_input("Enter task ID to update: ")
            if not task_id_str:
                print("\n  Error: Task ID cannot be empty.\n")
                continue
            try:
                task_id = int(task_id_str)
                task = manager.get_task(task_id)
                print(f"\n  Current title: {task.title}")
                print(f"  Current description: {task.description or '(none)'}\n")
                new_title = get_input("Enter new title (press Enter to keep current): ")
                new_desc = get_input("Enter new description (press Enter to keep current): ")
                manager.update_task(
                    task_id,
                    title=new_title if new_title else None,
                    description=new_desc if new_desc else None
                )
                print(f"\n  Task #{task_id} updated successfully.\n")
            except ValueError as e:
                if "invalid literal" in str(e):
                    print("\n  Error: Please enter a valid number.\n")
                else:
                    print(f"\n  Error: {e}\n")

        elif choice == "4":
            task_id_str = get_input("Enter task ID to toggle: ")
            if not task_id_str:
                print("\n  Error: Task ID cannot be empty.\n")
                continue
            try:
                task_id = int(task_id_str)
                task = manager.toggle_task(task_id)
                status_text = "completed" if task.status == Status.COMPLETED else "pending"
                print(f"\n  Task #{task_id} marked as {status_text}.\n")
            except ValueError as e:
                if "invalid literal" in str(e):
                    print("\n  Error: Please enter a valid number.\n")
                else:
                    print(f"\n  Error: {e}\n")

        elif choice == "5":
            task_id_str = get_input("Enter task ID to delete: ")
            if not task_id_str:
                print("\n  Error: Task ID cannot be empty.\n")
                continue
            try:
                task_id = int(task_id_str)
                manager.delete_task(task_id)
                print(f"\n  Task #{task_id} deleted successfully.\n")
            except ValueError as e:
                if "invalid literal" in str(e):
                    print("\n  Error: Please enter a valid number.\n")
                else:
                    print(f"\n  Error: {e}\n")

        elif choice == "6":
            print("\n  Goodbye!\n")
            break

        else:
            print("\n  Invalid option. Please select 1-6.\n")


if __name__ == "__main__":
    main()
