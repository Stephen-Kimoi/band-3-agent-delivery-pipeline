"""Run the Engineer agent.

Usage:
    python -m agents.engineer
"""

from agents.runner import main

if __name__ == "__main__":
    main(agent_key="engineer", prompt_file="engineer.md", model_env_var="ENGINEER_MODEL")
