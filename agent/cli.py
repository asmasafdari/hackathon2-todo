"""CLI entry point for the AI Todo Agent."""

import argparse
import asyncio
import sys

from agent import run_agent
from config import get_settings


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="AI-powered todo management assistant",
        prog="python -m agent.cli",
    )
    parser.add_argument(
        "message",
        nargs="*",
        help="Single command to execute (e.g., 'add buy groceries')",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset conversation context and start fresh",
    )
    parser.add_argument(
        "--session",
        type=str,
        default="default",
        help="Session ID for conversation persistence (default: 'default')",
    )
    return parser.parse_args()


def print_welcome():
    """Print welcome message."""
    print("\nTodo Agent - AI-powered task management")
    print("Type 'quit', 'exit', or 'q' to exit\n")


async def run_single_command(message: str) -> None:
    """Run a single command and exit."""
    try:
        response, _ = await run_agent(message)
        print(response)
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


async def run_interactive() -> None:
    """Run interactive conversation loop."""
    print_welcome()
    context = []
    exit_commands = {"quit", "exit", "q"}

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in exit_commands:
                print("Goodbye!")
                break

            response, context = await run_agent(user_input, context)
            print(f"\nAgent: {response}\n")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")
            # Continue the loop on errors


def main():
    """Main entry point."""
    args = parse_args()

    # Validate environment
    settings = get_settings()
    if not settings.openai_api_key:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it in your environment or create a .env file.")
        sys.exit(1)

    # Reset context if requested
    if args.reset:
        print("Conversation context reset.")

    # Single command mode
    if args.message:
        message = " ".join(args.message)
        asyncio.run(run_single_command(message))
    else:
        # Interactive mode
        asyncio.run(run_interactive())


if __name__ == "__main__":
    main()
