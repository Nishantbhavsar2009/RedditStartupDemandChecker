# Project Walkthrough - Reddit Startup Demand Checker

This walkthrough details the construction and verification of the Reddit Startup Demand Checker, built autonomously from scraped Reddit ideas.

## Phase 1: Idea Ranking and Selection

The parsed daily report (`13th June 2026.md`) contained 3 ideas:
1. Personal CRM ("Human Hub")
2. Reddit Startup Demand Checker
3. Lightweight macOS Clipboard Utility

Using the user profile criteria (preparing for CS/AI admissions at top US/Canada universities, intermediate Python, web development, systems automation), the ideas were scored:

| Idea | Relevance (25%) | Feasibility (20%) | College Value (25%) | Usefulness (20%) | Originality (10%) | Score |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Reddit Startup Demand Checker** | 10.0 | 8.5 | 9.5 | 9.0 | 8.0 | **9.175** |
| **Personal CRM** | 8.0 | 9.0 | 7.0 | 8.0 | 6.0 | **7.750** |
| **Lightweight macOS Clipboard Utility** | 7.0 | 7.0 | 7.0 | 8.0 | 6.0 | **7.100** |

The **Reddit Startup Demand Checker** was selected for its strong technical depth, relevance to CS/AI admissions (data scraping, NLP heuristics, and optional LLM analysis), and zero-configuration feasibility.

---

## Phase 2: Design Decisions

We applied the **Industrial Utilitarian** design direction:
- **Fonts**: `Share Tech Mono` (Display) and `JetBrains Mono` (Console/Body) to evoke a professional research terminal.
- **Palette**: Dark slate-black panels (`#13161c` and `#0c0d10`) offset by high-contrast amber borders (`#ffaa00`) representing warning/alert status.
- **Micro-interactions**: Hard-bordered hover states, blinking cursor indicators, and a scrolling live system log terminal outputting active server actions.
- **Scanline overlay**: A subtle 4px vertical scanline layer to give the UI a CRT terminal appearance.

---

## Phase 3: File Layout Implementation

The application contains:
1. [app.py](file:///Users/nishantbhavsar/Projects/RedditStartupDemandChecker/app.py): Entry point, FastAPI app, request validation, and routing.
2. [scraper.py](file:///Users/nishantbhavsar/Projects/RedditStartupDemandChecker/scraper.py): Fetches search listings for target subreddits using Reddit's public `.json` search endpoints.
3. [analyzer.py](file:///Users/nishantbhavsar/Projects/RedditStartupDemandChecker/analyzer.py): Rules-based keyword search (frustration metrics, density) and optional Gemini API integration.
4. [database.py](file:///Users/nishantbhavsar/Projects/RedditStartupDemandChecker/database.py): SQLite helper module to initialize a local database (`reports.db`) and store, delete, or load historical demand validation reports.
5. [templates/index.html](file:///Users/nishantbhavsar/Projects/RedditStartupDemandChecker/templates/index.html): Responsive console interface layout, CSS styles, and JavaScript handlers for form submission and rendering.
6. [tests/test_app.py](file:///Users/nishantbhavsar/Projects/RedditStartupDemandChecker/tests/test_app.py): Pytest file for verifying backend APIs and analyzer metrics.

---

## Phase 4: Verification

We verify the implementation by:
1. Setting up the environment.
2. Installing dependencies.
3. Running backend test suites.
4. Running the application locally.
