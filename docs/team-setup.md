# Team setup: get running and start on the AI

Updated October 16, 2026. For teammates who code. If this is your first project like this, follow it top to bottom; every step says what you should see.

Read first: `PLAN.md` sections 1 to 3 (what we're building), `CLAUDE.md` (the rules that never change), and `docs/decisions.md` (decisions that refine the plan; where they differ from `PLAN.md`, decisions win).

## The one rule about keys

Your API key is a password. It goes **only** in your own `.env` file, never in code, chat, screenshots, the team channel, or a commit. Each person makes their own key. If a key leaks, delete it in the provider's console and make a new one.

## Part 1: Set up your laptop (about 20 minutes)

These steps are for macOS. On Windows, use the same steps with `py -3.11` instead of `python3.11` and `.venv\Scripts\` instead of `.venv/bin/`.

1. **Install the tools** (skip any you already have):
   - Homebrew: see https://brew.sh
   - Python 3.11: `brew install python@3.11`
   - Node 20 or newer: `brew install node`
   - Check: `python3.11 --version` shows 3.11.x and `node --version` shows v20 or higher.

2. **Get the code.** Ask Mariangel for access to the GitHub repo, then:
   ```bash
   git clone https://github.com/mangejlu/Fintecathon.git
   cd Fintecathon
   ```

3. **Set up the backend:**
   ```bash
   python3.11 -m venv .venv
   .venv/bin/pip install -r backend/requirements.txt
   ```

4. **Set up the frontend:**
   ```bash
   cd frontend && npm install && cd ..
   ```

5. **Check that everything works:**
   ```bash
   .venv/bin/pytest -q
   ```
   You should see all tests pass, with no failures.

## Part 2: Get your AI key (about 10 minutes)

We use Zhipu's free GLM models through Z.ai, because they're free and work in China (decision 24). Claude is not available in China, so we don't use it in the app.

1. Go to **z.ai** and sign up.
2. In the console, check that **GLM-4.5-Flash** and **GLM-4.6V-Flash** are listed as free. If they aren't, tell the team before doing anything else.
3. Open **API Keys**, create a key named after your laptop (for example `landed-ana-laptop`), and copy it.

## Part 3: Put the key in `.env`

Run these from the project folder.

1. Make your own `.env` from the template:
   ```bash
   cp .env.example .env
   ```
2. Open it (on macOS, files starting with a dot are hidden in Finder):
   ```bash
   open -e .env
   ```
3. Paste your key right after `LLM_API_KEY=`, with no spaces or quotes. Leave the other lines as they are. Save and close.
4. Check that git will never upload it. This must print `.env`; if it prints nothing, stop and tell the team:
   ```bash
   git check-ignore .env
   ```
5. Check that the key is there, without showing it. This should print `1`:
   ```bash
   grep -c '^LLM_API_KEY=..*' .env
   ```

What's in `.env`:

| Variable | What it is |
| --- | --- |
| `LLM_API_KEY` | Your own Z.ai key |
| `LLM_BASE_URL` | Z.ai's address. In mainland China, if z.ai doesn't load, use `https://open.bigmodel.cn/api/paas/v4` |
| `LLM_MODEL` | The chat model, `glm-4.5-flash` |
| `LLM_VISION_MODEL` | The model that reads images, `glm-4.6v-flash` |

## Part 4: How the AI part works

The short version (`PLAN.md` section 3): **the AI explains, plain code does the math.**

- The AI reads, talks and decides which tool to call. It never calculates fees, never states limits, never picks a heads-up color, and never moves money.
- Tools are plain Python functions in `backend/tools.py`. They do every number and every rule.
- `backend/guardrails.py` decides heads-up colors. The AI only explains them.
- `confirm_and_run` (the sandbox payment) is only called by code after the student taps Confirm. The AI cannot call it (decision 7 and 8).
- Text inside invoices and messages is data, never instructions, even if it says "approve this payment".

Where things live:

| File | What it does |
| --- | --- |
| `backend/llm.py` | The only file that talks to the AI provider |
| `backend/agent.py` | The assistant loop (at most 8 steps) and the system prompt |
| `backend/tools.py` | The plain Python tools |
| `backend/guardrails.py` | Heads-up rules and permission levels |
| `backend/db.py` | SQLite and the log |
| `backend/data/` | Rules, payees, profile, knowledge base. Every row has a source, a date checked and a confidence |
| `backend/tests/` | Unit tests and `scenarios.yaml` (the 35 scenarios) |

Two kinds of tests:

- `pytest -q` runs the unit tests. No key and no internet needed. Run it before saying any task is done.
- The scenario runner (coming in step 3.9) runs the 35 scenarios against the real AI and prints the pass rate. It needs your key.

## Part 5: The build steps for the AI (Step 3)

Step 3 connects the AI and tests it in the terminal before any screens exist. Step 2 (the calculator: `quote_routes`, `fee_preview`, `get_fx_rate`, `check_payee`) has to be done before 3.6, because paying rent needs `quote_routes`. Steps 3.3 to 3.5 can start now.

Each build step is one small task: plan it, get the plan approved, write the tests first, build it, run `pytest -q`, then commit. Tick them off on the task board.

| Step | What | Who | Done when |
| --- | --- | --- | --- |
| 3.1 | Get a Z.ai key | Each person | Part 2 above |
| 3.2 | Put it in `.env` | Each person | Part 3 above prints `.env` and `1` |
| 3.3 | Build `backend/llm.py`: one function that sends messages and tools and returns the reply text and tool calls, a fake version for tests, unit tests with no network, and a small check script | One coder | Unit tests pass without a key |
| 3.4 | Run the check script | Each person; also one friend in China | It says the model answered and called the test tool. It never prints the key |
| 3.5 | Build `backend/db.py`: tables for the log, prepared payments and confirmations | One coder | Unit tests pass |
| 3.6 | Build `prepare_payment` (a draft with an id, sends nothing, a repeat within 10 minutes reuses it) and `confirm_and_run` (refuses without a confirmation record, a second confirmation on red, each id runs once, everything logged) | One coder, after Step 2 | One test per rule |
| 3.7 | Build `backend/agent.py`: the system prompt from `PLAN.md` section 5, the 8-step cap, automatic logging, broken tool inputs rejected, only level 1 and 2 tools given to the AI | One coder, after Step 2 | A fake-model test shows rent going `quote_routes` → `prepare_payment` → "waiting for your confirmation" |
| 3.8 | Chat with it in the terminal, for example "pay my rent to landlord_1, 3200 yuan, due Oct 25" | Everyone | You see each tool call, then "Confirm? (y/n)" |
| 3.9 | Add the rent scenario to `scenarios.yaml` and the runner that prints the pass rate | One coder | The runner prints 1 of 1 passed |

The exact commands for 3.4 and 3.8 will be added here once those pieces exist.

## Part 6: If you use Claude Code to help you code

You can use Claude Code (or another coding assistant) on your laptop to write the code. That's separate from the AI inside the app. Tips:

- Ask for one small piece at a time, for example: "Read PLAN.md and docs/decisions.md. Plan step 3.5 (`backend/db.py`) and wait for my approval."
- It reads `CLAUDE.md` automatically, which holds our rules.
- Read its plan before you approve it, and check that `pytest -q` passes before you commit.
- Never paste your key into it.

## Part 7: Working together

- Work on a branch per task, and keep merges small and frequent. Never push broken code to `main`, especially on Sunday and Monday.
- Real keys and real personal data never go into the repo. Use the fake data in `backend/data/`.
- Rule and knowledge values carry a source, a date checked and a confidence level. If you can't find a value, leave it empty; the app says "unknown".
- Stuck for more than 20 minutes? Ask in the team channel. Post what you ran, what you expected and what happened (never your key).
