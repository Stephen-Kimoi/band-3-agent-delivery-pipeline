"""Shared bootstrap for the Planner, Engineer, and Reviewer agents.

Each agent is a thin entrypoint (see planner.py / engineer.py / reviewer.py)
that calls ``main()`` with its own ``agent_config.yaml`` key, prompt file, and
model env var. Everything else -- model wiring, tools, and the Band connection
-- is identical across the three roles.
"""

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from band import Agent
from band.adapters import PydanticAIAdapter

from agents.tools import list_files, read_file, run_tests, write_file

PROJECT_ROOT = Path(__file__).resolve().parent.parent

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


async def run_agent(agent_key: str, prompt_file: str, model_env_var: str) -> None:
    load_dotenv(PROJECT_ROOT / ".env")

    model = os.environ.get(model_env_var) or os.environ.get(
        "DEFAULT_MODEL", "openai-chat:deepseek-chat"
    )
    prompt_path = PROJECT_ROOT / "prompts" / prompt_file
    custom_section = prompt_path.read_text()

    adapter = PydanticAIAdapter(
        model=model,
        custom_section=custom_section,
        additional_tools=[read_file, write_file, list_files, run_tests],
    )

    # Only override Band's connection URLs if explicitly set; otherwise
    # Agent.create() defaults to the production Band platform.
    overrides = {}
    if os.environ.get("BAND_REST_URL"):
        overrides["rest_url"] = os.environ["BAND_REST_URL"]
    if os.environ.get("BAND_WS_URL"):
        overrides["ws_url"] = os.environ["BAND_WS_URL"]

    agent = Agent.from_config(
        agent_key,
        adapter=adapter,
        config_path=PROJECT_ROOT / "agent_config.yaml",
        **overrides,
    )

    logger.info("Starting %s agent (model=%s)...", agent_key, model)
    await agent.run()


def main(agent_key: str, prompt_file: str, model_env_var: str) -> None:
    asyncio.run(run_agent(agent_key, prompt_file, model_env_var))
