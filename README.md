# Landed

A web app with an AI assistant that makes money in China make sense for international students. FinTechathon 2026, Topic C. Sandbox only: no real money.

See `PLAN.md` for the spec and `docs/decisions.md` for decisions that refine it. New teammates: start with `docs/team-setup.md`.

## Setup

Needs Python 3.11 and Node 20+.

```bash
python3.11 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
cp .env.example .env   # then add your LLM_API_KEY (from z.ai)
cd frontend && npm install
```

## Run

```bash
.venv/bin/uvicorn backend.main:app --reload   # API on http://localhost:8000
cd frontend && npm run dev                    # app on http://localhost:3000
```

## Test

```bash
.venv/bin/pytest -q
```
