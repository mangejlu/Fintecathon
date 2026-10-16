# Decisions

Decided October 15, 2026. These settle open points in `PLAN.md`. Where a decision here differs from `PLAN.md`, this file wins.

## Data and the calculator

1. **Placeholder numbers until the real sheets arrive.** Changed October 15, 2026, to follow PLAN Step 1. `backend/data/rules.json` holds placeholder numbers with source `"placeholder"`, confidence `low` and an empty `date_checked`. Placeholders are never presented as real rules: the empty date makes every one stale, so the app always adds "verify with your bank". They are replaced row by row as the rules sheet arrives. Real values that can't be found stay empty, meaning unknown.
2. **Unknown values.** A route with an unknown fee, minimum or limit stays available and shows "cost unknown" for that line. It ranks after every fully known route and gets a "verify with your bank" note. An unknown limit never makes a route unavailable.
3. **Exchange rates.**
   - Every rate is CNY per 1 unit of foreign currency (for example 1 USD = 7.10 CNY).
   - The markup cost is the absolute gap between the offered rate and the mid rate, so it is never negative.
   - Costs are shown in CNY, with the home-currency amount next to them. Both come from the calculator.
4. **Fee rule columns.** The free-text "fee rule" column becomes `fee_threshold_cny`, `fee_percent_over_threshold`, `fee_fixed_cny` and `fee_note` (the original wording). Any of them can be empty, meaning unknown. The Google Sheet uses the same columns.
5. **Clock and history.** `quote_routes` takes an optional `today` (defaults to the real date; tests pass a fixed one). "Card charges today" are counted from sandbox payments in the SQLite log, plus optional seed charges in `profile.json` for demos.
6. **Routes in `rules.json`.** Alipay (foreign card), WeChat Pay (foreign card), card direct and bank transfer. A remittance service is added later if the sheet has one.

## Safety and control

7. **Confirm flow.** A run ends at "waiting for your confirmation". `POST /confirm/{id}` records the student's tap, and code calls `confirm_and_run` directly. The AI never triggers a payment.
8. **AI tool list.** The AI cannot call `log_event` or `confirm_and_run`. The loop logs every tool call itself. The AI gets level 1 and 2 tools only.
9. **Heads-up rule order.** Every rule is evaluated. The card takes the worst color (red, then yellow, then green) and lists every matched reason, worst first. Rule 6 adds a "verify with your bank" note on top of any color.
10. **Payee matching.**
    - Red if the name matches a known payee but the account differs, or the account matches but the name differs.
    - Yellow if neither matches anything.
    - Green only if both match exactly.

    Names are compared after normalizing case and spaces. Accounts must match exactly.
11. **Thresholds.**
    - "Large amount" means at or above 80% of the route's per-payment limit in `rules.json`.
    - The limit runway warns at 80% of the annual limit in `rules.json`.
    - A rule is stale when `date_checked` is more than 90 days old.
    - "Many large transfers in a short time" means 3 or more large payments within 7 days.
    - The 80%, 90-day and 3-in-7-days values are app defaults, labeled as such in `app_settings.json`, and the student can change them.
    - If a limit is unknown, that check says "unknown" instead of guessing.
12. **Scenario colors.** The large tuition payment (scenario 7) and the 80% annual limit warning (scenario 8) are both yellow, under heads-up rule 4.
13. **Duplicate payments.** `prepare_payment` creates an id, and `confirm_and_run` runs each id once. A second identical request (same payee, amount and reference) within 10 minutes reuses the first draft.

## API and frontend

14. **Event format.** `{run_id, seq, type, step_label, status, color, reason, timestamp, data}`.
    - `seq` lets the screen ask for events after a given number.
    - `data` holds the card payload. Its shape depends on `type`, for example `route_quote`, `heads_up`, `charge_detective` or `final_answer`.
15. **Live steps.** The screen polls `GET /runs/{id}/events?after=<seq>` every 0.5 s. Server-sent events only if there is spare time; the event format stays the same either way.
16. **Endpoints not in the PLAN table.**
    - Add now: `GET /settings` and `GET /home` (balances, incoming money, runway, savings).
    - Add with their feature: `/guides/{task}`, `/move-on` and `/family`.
    - Cashier translation goes through `/chat`.
    - The monthly cost review and the savings counter join the cut list.
17. **API timing.**
    - Friday: `POST /chat` and `GET /runs/{id}/events` working on the happy path.
    - Saturday morning: `/confirm`, `/log` and `/settings`.

## Tests

18. **Scenarios.** `pytest -q` runs unit tests only, with no API key and no network. A separate command runs `scenarios.yaml` against the live AI and prints the pass rate. Each scenario checks facts, not wording: which tools were called, the heads-up color, route ranking, confirmation state, and required phrases such as "I'm not sure".
19. **AI-backed tools.** `read_document`, `draft_message`, `explain_charge` and `settings_health_check` take the AI client as a parameter. Unit tests pass a fake client and check the plain-code parts: schema validation, the "show what I read and ask to confirm" path, and knowledge base entry ids.
20. **Wallet knowledge base.** All entries go in the system prompt with their ids, for general wallet questions. `explain_charge` also matches symptom keywords in plain code and returns ranked entry ids, so the charge detective card is built from data. The AI must cite an entry id or say "I'm not sure".

## Privacy, files and hosting

21. **Real payment numbers.** The savings analysis stays in the team's own sheet. The repo and the deck get only rounded totals, with no dates, merchants or account details. The demo profile uses fake transactions.
22. **Extra data files** beyond the CLAUDE.md list:
    - `sending_routes.json`
    - `messages.json` (messages, bank notices and the answer key)
    - `content/` (task guides, move-on items, cashier phrases)
    - `app_settings.json` (the defaults from decision 11)
23. **Hosting.** On startup the database is rebuilt and seeded from the data files. The log resetting on each redeploy goes on the known-risk list. Execution evidence is exported from local runs, and replays back up the live demo.

## AI provider

24. **AI provider.** Decided October 15, 2026. Replaces the Claude / Anthropic SDK in `PLAN.md`.
    - **Provider:** Zhipu's free Flash models through Z.ai's OpenAI-compatible API: GLM-4.5-Flash for chat and tools, GLM-4.6V-Flash for reading images.
    - **Why:** it is free, it is a Chinese provider reachable from China (judges, the Shenzhen final), and it supports tool calling.
    - **How:** `backend/llm.py` is the only file that talks to the provider, using the `openai` package. Provider, URL and models come from `.env`.
    - **Backup:** Alibaba Model Studio's free quota (Singapore region). Switching to it changes only `.env`, no code.
    - **Honesty:** free models are smaller and less reliable at following rules. The scenario pass rate is reported as measured, and the known-risk list says so. Free-tier terms can change, so check them on docs.z.ai.
    - **Still to verify:** the free status of both models, the base URL, and that z.ai is reachable from mainland China. If it is not, switch `LLM_BASE_URL` to `https://open.bigmodel.cn/api/paas/v4`.
