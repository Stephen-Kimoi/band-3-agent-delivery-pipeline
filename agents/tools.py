"""Filesystem tools shared by the Planner, Engineer, and Reviewer agents.

All three agents read and write the same local ``workspace/`` directory, which
plays the role of a shared repo checkout. Each tool follows Pydantic AI's tool
signature -- ``ctx: RunContext[...]`` first, then typed arguments with a
docstring Pydantic AI turns into the tool schema the model sees.
"""

from __future__ import annotations

import asyncio
import subprocess
import sys
from pathlib import Path
from typing import Any

from pydantic_ai import RunContext

WORKSPACE_DIR = (Path(__file__).resolve().parent.parent / "workspace").resolve()
WORKSPACE_DIR.mkdir(exist_ok=True)


def _resolve(path: str) -> Path:
    candidate = (WORKSPACE_DIR / path).resolve()
    if candidate != WORKSPACE_DIR and WORKSPACE_DIR not in candidate.parents:
        raise ValueError(f"Path '{path}' escapes the workspace directory")
    return candidate


async def read_file(ctx: RunContext[Any], path: str) -> str:
    """Read a text file from the shared workspace.

    Args:
        path: Path relative to the workspace root, e.g. "plan.md" or "app/main.py".
    """
    target = _resolve(path)
    if not target.exists():
        return f"Error: '{path}' does not exist in the workspace."
    if not target.is_file():
        return f"Error: '{path}' is not a file."
    return target.read_text()


async def write_file(ctx: RunContext[Any], path: str, content: str) -> str:
    """Write a text file in the shared workspace, creating parent directories as needed.

    Args:
        path: Path relative to the workspace root, e.g. "plan.md" or "app/main.py".
        content: Full contents to write. Overwrites any existing file at this path.
    """
    target = _resolve(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
    return f"Wrote {len(content)} characters to {path}"


async def list_files(ctx: RunContext[Any], path: str = ".") -> str:
    """List files and directories under a path in the shared workspace.

    Args:
        path: Path relative to the workspace root. Defaults to the workspace root.
    """
    target = _resolve(path)
    if not target.exists():
        return f"Error: '{path}' does not exist in the workspace."
    entries = sorted(
        p.relative_to(WORKSPACE_DIR).as_posix() + ("/" if p.is_dir() else "")
        for p in target.rglob("*")
    )
    return "\n".join(entries) if entries else "(empty)"


async def run_tests(ctx: RunContext[Any], path: str = "app") -> str:
    """Run pytest against a directory in the shared workspace and return its output.

    Args:
        path: Path relative to the workspace root containing the code and tests.
            Defaults to "app".
    """
    target = _resolve(path)
    if not target.exists():
        return f"Error: '{path}' does not exist in the workspace."

    def _run() -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "pytest", str(target), "-v"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=WORKSPACE_DIR,
        )

    result = await asyncio.to_thread(_run)
    return f"$ pytest {path}\n\n{result.stdout}\n{result.stderr}".strip()
