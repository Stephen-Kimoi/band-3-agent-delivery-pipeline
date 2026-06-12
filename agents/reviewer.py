"""Run the Reviewer agent.

Usage:
    python -m agents.reviewer
"""

from agents.runner import main

if __name__ == "__main__":
    main(agent_key="reviewer", prompt_file="reviewer.md", model_env_var="REVIEWER_MODEL")
