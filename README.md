# Band 3-Agent Software Delivery Pipeline (prototype)

A minimal **Planner -> Engineer -> Reviewer** pipeline built with [Band SDK](https://docs.band.ai)
and [AI/ML API](https://aimlapi.com). Three independent Python processes join a shared Band room,
collaborate over chat (`@mentions`), and read/write a shared local `workspace/` directory to plan,
build, and review a tiny FastAPI feature.

This is the working prototype behind the tutorial *"Build a 3-Agent Software Delivery Pipeline
with Band SDK and AI/ML API"*.

## Architecture

```
            Band platform (app.band.ai) -- shared chat room
                 |            |             |
            +---------+  +----------+  +----------+
            | Planner |  | Engineer |  | Reviewer |
            +---------+  +----------+  +----------+
                 \            |             /
                  \           |            /
                   v          v           v
                  workspace/ (shared local directory)
                    plan.md, app/, review.md
```

- Each agent is a `band.Agent` using `PydanticAIAdapter`.
- Model calls go through **AI/ML API** via `OPENAI_BASE_URL` + `OPENAI_API_KEY` -- no
  framework-specific API wiring needed.
- Agents coordinate by `@mention`ing each other in the Band room; the actual plan, code, and
  review live as files in `workspace/`.

## Prerequisites

- Python 3.11+
- A [Band](https://app.band.ai) account with **three remote agents** created (Planner, Engineer,
  Reviewer) -- each gives you an Agent ID + API key.
- An [AI/ML API](https://aimlapi.com/app/keys) account and API key.

## Setup

1. **Install dependencies** (from this `prototype/` directory):

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure your AI/ML API key**:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set `OPENAI_API_KEY` to your AI/ML API key. `OPENAI_BASE_URL` is already
   pointed at AI/ML API.

   By default all three agents use **DeepSeek V3** (`openai-chat:deepseek-chat`) via AI/ML API.
   Because everything routes through AI/ML API's OpenAI-compatible endpoint, swapping models is
   just an env var change -- set `DEFAULT_MODEL`, or `PLANNER_MODEL` / `ENGINEER_MODEL` /
   `REVIEWER_MODEL` individually, to any AI/ML API model ID prefixed with `openai-chat:` (e.g.
   `openai-chat:gpt-4o-mini`). No code changes needed.

3. **Register three agents on Band** (https://app.band.ai), one each for Planner, Engineer, and
   Reviewer, then:

   ```bash
   cp agent_config.yaml.example agent_config.yaml
   ```

   Paste each agent's `agent_id` and `api_key` into the matching section.

## Run it

Open three terminals (from `prototype/`, with the venv activated in each):

```bash
python -m agents.planner
python -m agents.engineer
python -m agents.reviewer
```

Each process connects to Band and waits in its agent's rooms.

Then, in the Band web app (https://app.band.ai):

1. Create a new room.
2. Add your three agents (Planner, Engineer, Reviewer) as participants.
3. Send a message describing a small feature, e.g.:

   ```
   @Planner We need a new FastAPI endpoint: POST /tasks to create a task
   (title: str, done: bool = false) and GET /tasks to list all tasks, stored
   in memory. Please write a plan.
   ```

Watch the room: the Planner writes `workspace/plan.md` and hands off to the Engineer, the
Engineer writes `workspace/app/main.py` + `workspace/app/test_main.py` and runs the tests, and the
Reviewer checks the result and writes `workspace/review.md` before approving or requesting
changes.

## Trying the result

Once the Reviewer approves, run the generated app:

```bash
uvicorn workspace.app.main:app --reload
```

## Project layout

```
prototype/
├── agents/
│   ├── runner.py     # shared bootstrap: model wiring, tools, Band connection
│   ├── tools.py       # read_file / write_file / list_files / run_tests
│   ├── planner.py     # entrypoint: python -m agents.planner
│   ├── engineer.py    # entrypoint: python -m agents.engineer
│   └── reviewer.py    # entrypoint: python -m agents.reviewer
├── prompts/
│   ├── planner.md      # Planner system prompt
│   ├── engineer.md     # Engineer system prompt
│   └── reviewer.md      # Reviewer system prompt
├── workspace/           # shared scratch space (gitignored, created at runtime)
├── agent_config.yaml    # Band agent_id/api_key per role (gitignored)
└── .env                 # AI/ML API key + model overrides (gitignored)
```
