"""SpecKit MCP Server — exposes .claude/commands/ as MCP prompts."""
from pathlib import Path
from mcp.server.fastmcp import FastMCP

PROJECT_ROOT = Path(__file__).parent.parent.parent
COMMANDS_DIR = PROJECT_ROOT / ".claude" / "commands"
CONSTITUTION_FILE = PROJECT_ROOT / ".specify" / "memory" / "constitution.md"
SPECS_DIR = PROJECT_ROOT / "specs"

mcp = FastMCP("speckit")


@mcp.resource("speckit://constitution")
def get_constitution() -> str:
    """Return the project constitution."""
    return CONSTITUTION_FILE.read_text(encoding="utf-8") if CONSTITUTION_FILE.exists() else "Not found."


@mcp.resource("speckit://specs")
def list_specs() -> str:
    """Return directory listing of specs/."""
    if not SPECS_DIR.exists():
        return "specs/ not found."
    return "\n".join(
        f"{'[dir]' if p.is_dir() else '[file]'} {p.name}"
        for p in sorted(SPECS_DIR.iterdir())
    )


def _register_prompts():
    """Register one prompt per .md file in .claude/commands/."""
    for md_file in sorted(COMMANDS_DIR.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        slug = md_file.stem.replace(".", "-")          # sp.plan → sp-plan

        def make_fn(text: str):
            def prompt_fn(args: str = "") -> str:
                return text if not args else f"{text}\n\n---\nArgs: {args}"
            return prompt_fn

        mcp.prompt(name=slug)(make_fn(content))


_register_prompts()

if __name__ == "__main__":
    mcp.run()
