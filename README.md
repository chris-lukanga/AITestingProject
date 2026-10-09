# LLM Integrity Lab

**An AI testing assistant for software testers.**

Connect your AI application's API, describe what it should do, and watch the agents research, plan, generate tests, capture responses and evaluate the results.

## Start

Double-click **Start-Lab.cmd** on Windows. On macOS/Linux, run `python3 setup_lab.py`.

You need Python 3.12+. The launcher installs missing dependencies on first use, then opens:

- **Testing workspace:** http://127.0.0.1:8000
- **Example student assistant:** http://127.0.0.1:8001

For live AI agents, copy `.env.example` to `.env`, add a Gemini, OpenRouter, Groq or xKiro key, and restart. No model-provider endpoint is needed. A Tavily key enables live web research; otherwise research uses bundled references.

Free-only routing is enforced. Gemini and Groq accounts must stay on their Free plans; OpenRouter and xKiro catalogs are filtered for zero token prices. Optional Groq and xKiro keys provide fallback when earlier providers hit limits. A Groq key saved under `GROK_API_KEY` is recognized; direct xAI Grok is excluded because its API models are paid.

## Test your application

1. Click **New test run**. Enter your application's chat API URL and expected behaviour. Include policy facts and action permissions so the agent can judge answers against a clear contract.
2. Click **Test connection**, then review the context, case count and limits. Choose **Live AI** for generated tests and model evaluation, or the **Local catalog** for general probes.
3. Start the run. Open an agent card to see its actions, decisions and quality checks. Open a case's **Evidence** to inspect the input, actual HTTP response, timing and evaluation.
4. Review findings, export HTML or JSON, and compare later runs in History.

The workspace supports simple JSON, chat-completion APIs and custom request/response mappings. Authentication and advanced mappings stay in connection settings. Remote URLs require the server's endpoint allowlist; see the [connection guide](docs/API.md).

Choose **20, 50, 100 or 200 cases**. Live runs consume provider quota and may take several minutes. Cost limits use your supplied reservation rate, not a verified invoice estimate. Generic local checks needing a model judgment are reported as **inconclusive**, so they cannot create a false passing result.

## Watch the agents work

The control room shows the researcher, planner, generator, executor, evaluator, reporter, advisor, scope checker and quality reviewer. The decision stream records research queries, sources, generated batches, captured responses and evaluation confidence. Quality review applies explicit contract, coverage and evidence checks. Saved runs retain this activity after restart.

## Try the bundled example

Expand **Example target: CampusHelp** on the overview to run 50, 100 or 200 checks against its vulnerable or protected version. This local comparison needs no key.

CampusHelp answers from 12 fictional handbook topics, cites its sources and creates in-memory tickets after confirmation. Try “Can I pay fees in instalments?” or “Create a support ticket: I cannot access my timetable.” Select **Live AI** in the student app to use your configured model. In **Advanced demo setup**, the answer engine and testing-agent mode can be selected independently.

Student identities, records and policies are synthetic. A passing report establishes only the checks actually executed.

Developer checks: `python -m pytest -q` (browser checks need Chrome or Playwright Chromium). See [verification notes](docs/VERIFICATION.md) for measured runs.
