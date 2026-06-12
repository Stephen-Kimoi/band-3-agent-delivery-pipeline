"""Run the Planner agent.

Usage:
    python -m agents.planner
"""

from agents.runner import main

if __name__ == "__main__":
    main(agent_key="planner", prompt_file="planner.md", model_env_var="PLANNER_MODEL")
