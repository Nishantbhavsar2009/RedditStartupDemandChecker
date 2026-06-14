# Implementation Plan - Reddit Startup Demand Checker

An autonomous tool that scrapes Reddit for validation signals of a startup idea, running heuristic analysis and optional deep AI analysis (via Gemini API) to generate a structured demand report.

## Design Direction Summary (AAS Web App Builder Phase A)
- **Aesthetic Name**: Industrial Utilitarian (Retro-Tech Research Console)
- **DFII Score**: 18 / 15 (Excellent)
- **Key Inspiration**: Terminal dashboards, high-tech industrial warning consoles, and scientific monitoring systems.
- **Differentiation Anchor**: An interactive, scrolling "System Console Log" that outputs real-time step-by-step logs of the scraping and analysis execution.
- **Design System Snapshot**:
  - **Fonts**: `Share Tech Mono` (Display) + `JetBrains Mono` (Body / Console)
  - **Color Palette (CSS Variables)**:
    - `--bg-main`: `#0c0d10` (Deep console black)
    - `--bg-panel`: `#13161c` (Panel grey)
    - `--border-industrial`: `#ffaa00` (Warning amber)
    - `--border-muted`: `#2a313d` (Steel grey)
    - `--text-primary`: `#f1f5f9` (Bright silver)
    - `--text-muted`: `#64748b` (Slate grey)
    - `--accent-ok`: `#10b981` (Console green)
    - `--accent-warn`: `#f59e0b` (Amber alert)
    - `--accent-err`: `#ef4444` (Emergency red)
  - **Motion**: Mechanical grid transitions, blinking cursor animation, hard-line hover highlights (no soft fades).

---

## Technical Stack
- **Backend**: Python 3, FastAPI, `httpx` (for non-authenticated Reddit JSON API calls), `jinja2` (for rendering templates).
- **Frontend**: Single-page application using vanilla HTML, vanilla CSS (utilizing CSS custom properties), and vanilla JavaScript.
- **Data Persistence**: SQLite database (for saving past validation reports) using standard `sqlite3` driver.

---

## File Layout
```text
/Users/nishantbhavsar/Projects/RedditStartupDemandChecker/
├── app.py                     # Main FastAPI server and routing
├── database.py                # Database setup and CRUD operations for saved reports
├── scraper.py                 # Reddit search scraper and text formatting
├── analyzer.py                # Heuristic and optional Gemini AI analysis engine
├── templates/
│   └── index.html             # UI Dashboard (Single file with embedded CSS and JS)
├── tests/
│   └── test_app.py            # Automated tests using pytest
├── requirements.txt           # Python dependencies
├── implementation_plan.md     # This plan
└── README.md                  # Project documentation
```

---

## Build Checklist

### Phase 1: Setup & Foundations
- [ ] Initialize Python virtual environment.
- [ ] Write `requirements.txt` with dependencies (`fastapi`, `uvicorn`, `httpx`, `jinja2`, `google-genai`).
- [ ] Create database schema in `database.py` to store reports (idea, keywords, overall_score, summary, payload_json, timestamp).

### Phase 2: Reddit Scraper
- [ ] Implement `scraper.py` using `httpx` to search target subreddits using Reddit's public `.json` search endpoint.
- [ ] Implement parsing of titles, self-texts, comments, upvote ratios, and links.
- [ ] Include user-agent rotation or clean formatting to prevent Reddit rate-limiting.

### Phase 3: Analysis Engine
- [ ] Implement heuristic scoring algorithm in `analyzer.py` (measuring frustration keywords, engagement metrics, post count).
- [ ] Implement Gemini AI analysis in `analyzer.py` (extracting pain points, gaps, features if `GEMINI_API_KEY` is present).
- [ ] Fall back gracefully to heuristics if no API key is provided.

### Phase 4: Backend API & Server
- [ ] Create FastAPI server in `app.py`.
- [ ] Add endpoints:
  - `GET /` -> Serve template.
  - `POST /analyze` -> Trigger scraping + analysis, return structured report.
  - `GET /reports` -> Fetch list of past saved reports.
  - `GET /reports/{id}` -> Fetch details of a specific saved report.

### Phase 5: Frontend Interface (Industrial Utilitarian UI)
- [ ] Create `templates/index.html` with semantic structure.
- [ ] Implement CSS system with defined variables, terminal screen scanning line, and responsive grid layout.
- [ ] Write JS to handle:
  - Form submission.
  - Real-time logging output in the console.
  - Rendering gauges, lists, and markdown text reports.
  - Local storage caching and past reports sidebar.

### Phase 6: Verification & Polish
- [ ] Write tests in `tests/test_app.py` for API routes and scraping logic.
- [ ] Run audits to ensure responsive layouts and clean semantic HTML.
- [ ] Check performance and error states (e.g. rate-limiting, offline, invalid API key).

---

## Verification Plan
- **Backend Tests**: Run `pytest` to verify API routing and scraper processing.
- **Scraper Mock**: Test scraper using mock Reddit JSON payloads to verify parsing robustness.
- **UI Responsiveness**: Test viewport scales down to mobile widths.
- **Keyboard Navigation**: Ensure inputs and buttons can be fully focused and submitted via keyboard (`Tab` + `Enter`).
- **No-Key Fallback**: Verify application functions successfully without a Gemini API Key.
