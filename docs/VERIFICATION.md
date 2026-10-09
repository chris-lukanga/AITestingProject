# Verification record

Verified **9 October 2026** on Windows with Python **3.14.8** and installed Google Chrome.

## Automated checks

The full regression run returned **120 passed** in **119.14 seconds**, including five Playwright browser checks. Coverage includes general API configuration, connection probing, 200 unique generic catalog cases, persistent agent traces, output reviews, frozen retests, provider cooldowns and generation recovery. Existing dependency deprecation warnings remain.

Commands:

```text
python -m pytest -q --disable-warnings
python scripts/verify_demo.py
```

The Windows system `python` alias was unavailable, so verification used the installed executable under `%LOCALAPPDATA%/Python/pythoncore-3.14-64/`. `Start-Lab.cmd` now discovers this installation automatically. The actual CMD launcher started both updated websites and both health and HTML endpoints returned HTTP 200. Its owned smoke-test servers were stopped afterward. First-time dependency download was not exercised because dependencies were already installed.

## Independent 200-case process runs

These results came from actual HTTP requests to separately launched servers, not mocked responses in the testing platform.

| Version | Cases | Requests | PASS | FAIL | ERROR | Elapsed |
|---|---:|---:|---:|---:|---:|---:|
| Vulnerable | 200 | 228 | 111 | 89 | 0 | 42.138 s |
| Protected | 200 | 228 | 200 | 0 | 0 | 52.806 s |

Both runs had zero inconclusive or skipped checks and zero provider charges. The comparison found **89 resolved failures**, with no repeated or new failures. Both reports loaded after the platform process was stopped and restarted.

Run IDs:

- Vulnerable: `d666b6b1db0441ae928fb5cd2b480ded`
- Protected: `b2fe885229d24b2a992e39563f69688b`

Evidence is saved in `outputs/verification/summary.json` and `outputs/verification/lab/reports/`. Browser screenshots are under `outputs/campushelp-desktop.png`, `outputs/campushelp-mobile.png` and `outputs/browser-overview.png`. Runtime evidence is ignored by Git.

## What was exercised

- Local handbook retrieval, source citations, natural wording, follow-up context and unknown-policy handling.
- Confirmed ticket creation, cancellation, duplicate confirmation and cross-student isolation.
- Distinct 50/100/200-case suites, request estimates, live generation batching and duplicate rejection.
- One-click 100-case protected execution without endpoint configuration or environment keys; retests preserve the original case definitions.
- Browser one-click execution, evidence inspection, policy browsing, ticket confirmation, downloads and a 390px viewport.
- Live student responses through a mocked shared gateway, rejecting invented evidence without silently falling back.
- Live test planning with and without a Tavily key, using mocked providers and real local target HTTP.

These are results for a fictional campus and deliberately selected application protections. The suites include variants of shared risks. They do not establish production security or a real model's vulnerability rate. The earlier local comparison did not use provider calls. The live verification below separately exercised model providers and web research. Provider billing was not verified.

## General workflow and live provider verification

The redesigned workspace uses general HTTP connections as its main workflow. CampusHelp is an optional example. A separate workspace-policy HTTP fixture was exercised through the connection form, connection probe, run control, all nine agent cards, review gates and captured-response dialog. Generic catalog cases remain INCONCLUSIVE when their subjective contract cannot be judged locally. The catalog produced 200 distinct cases with retrieval, tools and memory disabled.

A real live run used the **general HTTP adapter** against the local student application's live answer endpoint. Planning and generation used actual model calls and Tavily research: **9 queries, 20 sources**. The first 50-case generation attempt stopped after repeated inputs, retaining **30 validated cases**. That experience led to bounded repair, preservation of valid partial batches and saved-suite retesting; regression checks cover those behaviours.

The retained 30-case suite was then executed with fresh live evaluation:

| Run | Cases | PASS | FAIL | ERROR | INCONCLUSIVE | Target requests | Testing-model attempts | Elapsed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| General HTTP / live | 30 | 23 | 0 | 7 | 0 | 30 | 26 | 80.274 s |

Run: `ac333f22289e4230a82199bd0e6df873`. Generation source: `7558b43fc98d42dea8a07acd9fa57089`.

Judgments include actual Gemini and OpenRouter responses alongside deterministic assertions. The target's successful live answers used Gemini; some application-controlled refusals used its local guardrails. Seven HTTP 503 responses reported that the target could not produce verified policy evidence. They remain ERROR, without a security conclusion. Gemini also reported exhausted daily quota during earlier preparation; the gateway now cools down those models and preserves fallback history.

The completed execution reserved **$0.663615** at the configured ceiling; this is not an invoice amount. Its preparation run has separate recorded usage. Evidence, source activity and the report are saved under `outputs/verification/general-live/`. Desktop/mobile console screenshots are `outputs/general-agent-console.png` and `outputs/general-agent-console-mobile.png`.

This verifies a local owned application through the general adapter, not an arbitrary production endpoint. The fresh 50-case run below verifies generation after the recovery changes. The 200-case protected/vulnerable local comparison above is a separate measurement.

## Free-only fallbacks and fresh 50-case run

The supplied `GROK_API_KEY` authenticated successfully against Groq; the gateway recognizes that legacy variable when its key has Groq's format. A direct Groq connection returned valid JSON using `qwen/qwen3.8-27b`. A direct xKiro connection returned valid JSON using `mistralai/ministral-14b`, selected from the live catalog's free tier with zero input/output prices. The xKiro catalog exposed 56 eligible free chat models during this check. No key value is stored in the verification artifacts.

Only documented Gemini/Groq free-plan models and verified zero-price OpenRouter/xKiro models are eligible. Paid, premium, unknown-price and direct xAI models are excluded. The UI and API enforce free-only routing. Gemini/Groq accounts must remain on their Free tiers; their APIs do not turn a paid account into a free account. Provider documentation: [Google pricing](https://ai.google.dev/gemini-api/docs/pricing), [Groq free-plan limits](https://console.groq.com/docs/rate-limits), [xKiro model catalog](https://docs.xkiro.com/api/list-models/).

A fresh general-HTTP live run generated **50 distinct inputs**, including repaired partial batches, and evaluated all 50 against the local live student API:

| Cases | PASS | FAIL | ERROR | INCONCLUSIVE | Target requests | Testing-model attempts | Elapsed |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 50 | 44 | 0 | 6 | 0 | 50 | 52 | 376.882 s |

Run: `192a0831f4e2422b8c71529002fbebb3`. It reused the retained 20-source research checkpoint and recorded six agent quality reviews. Successful testing calls used Gemini 3.1 Flash-Lite, 3.5 Flash and 3.5 Flash-Lite. The new backup providers were separately verified; this run did not need to dispatch to them. Six target API errors remain visible as errors. The run reserved **$1.034620**, not a verified invoice amount.

Evidence is under `outputs/verification/general-free-50/`, and free-provider checks are in `outputs/verification/free-fallbacks.json`. The latest report remained available after the apps were restarted. Real-run console screenshots are `outputs/live-free-agent-console.png` and `outputs/live-free-agent-console-mobile.png`.
