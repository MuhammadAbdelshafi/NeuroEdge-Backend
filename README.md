# Neurology Research Aggregator — Technical Overview

A full-stack, multi-user research aggregation platform for neurology professionals. The system automatically fetches, classifies, summarizes, and surfaces relevant medical papers from PubMed and journal RSS feeds, delivered through a polished Next.js frontend and a FastAPI backend.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────┐
│                   Next.js Frontend                    │
│  /dashboard  /admin/users  /admin/papers              │
│  /admin/analytics  /admin/queue                       │
└────────────────────┬─────────────────────────────────┘
                     │ HTTP (Axios, port 3000 → 8001)
┌────────────────────▼─────────────────────────────────┐
│              FastAPI Backend (port 8001)              │
│  /api/v1/auth  /api/v1/papers  /api/v1/admin         │
│  /api/v1/analytics  /api/v1/feed                     │
└────────────────────┬─────────────────────────────────┘
                     │ SQLAlchemy ORM
┌────────────────────▼─────────────────────────────────┐
│              SQLite Database (user_service.db)        │
│  users · user_profiles · papers · paper_summaries    │
│  job_runs · user_events                              │
└──────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 (App Router), TypeScript, shadcn/ui, Axios |
| Backend | FastAPI, Python 3.11+ |
| ORM | SQLAlchemy 2.x |
| Database | SQLite (`user_service.db`) |
| Auth | OAuth2 + JWT (Bearer tokens) |
| AI | OpenAI API (GPT-based summarization & classification) |
| RSS Parsing | `feedparser` + `requests` |
| PubMed | NCBI Entrez E-utilities API |
| Deployment | Railway (backend) + Vercel (frontend) |

---

## Directory Structure

```
user_service/
├── app/
│   ├── db/
│   │   ├── base.py              # SQLAlchemy declarative base
│   │   ├── session.py           # DB session factory
│   │   ├── models/              # ORM models
│   │   │   ├── user.py          # User model
│   │   │   ├── user_profile.py  # Professional profile model
│   │   │   ├── paper.py         # Paper model (pubmed_id nullable)
│   │   │   ├── summary.py       # PaperSummary model
│   │   │   └── job.py           # JobRun tracking model
│   │   └── repositories/        # Data access layer
│   │       ├── paper_repo.py    # incl. get_by_title, get_by_doi
│   │       └── user_repo.py
│   ├── modules/
│   │   ├── admin/               # Admin management module
│   │   │   ├── routes.py        # Admin API endpoints
│   │   │   ├── service.py       # Business logic & DB aggregations
│   │   │   └── schemas.py       # Pydantic response models
│   │   ├── analytics/           # User event tracking
│   │   ├── classification/      # AI paper classification
│   │   │   └── jobs/
│   │   │       └── classification_job.py
│   │   ├── papers/
│   │   │   ├── fetchers/
│   │   │   │   ├── pubmed_fetcher.py   # PubMed E-utilities client
│   │   │   │   └── rss_fetcher.py      # RSS/Atom feed client
│   │   │   ├── jobs/
│   │   │   │   └── fetch_job.py        # Orchestrates both fetchers
│   │   │   └── deduplicator.py         # Deduplication by id/doi/title
│   │   ├── summarization/       # AI summarization pipeline
│   │   ├── feed/                # Personalized user paper feed
│   │   └── user/                # Auth, profile, preferences
├── config/
│   └── rss_feeds.json           # Journal → RSS URL mapping
├── scripts/
│   ├── force_reset_db.py        # Drop & recreate schema
│   ├── process_backlog.py       # Batch classify/summarize pending
│   ├── verify_rss_papers.py     # Validate RSS ingestion
│   └── migrate_pubmed_nullable.py
├── requirements.txt
└── run.py                       # Starts uvicorn on port 8001

frontend/
├── app/
│   ├── (auth)/login/            # Login page
│   ├── dashboard/               # Main user-facing dashboard
│   └── admin/
│       ├── layout.tsx           # Persistent sidebar layout
│       ├── page.tsx             # Redirects → /admin/users
│       ├── users/page.tsx       # Users Management screen
│       ├── papers/page.tsx      # Papers Pipeline screen
│       ├── analytics/page.tsx   # Usage Analytics screen
│       └── queue/page.tsx       # Queue Health screen
└── lib/
    └── api.ts                   # Axios instance (baseURL: :8001)
```

---

## Backend API Reference

### Authentication (`/api/v1/auth`)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/signup` | Register new user + profile |
| POST | `/auth/login` | Returns JWT (OAuth2 form body) |

### Papers (`/api/v1/papers`)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/papers/` | List papers (paginated, filtered) |
| GET | `/papers/{id}` | Single paper detail |

### Admin (`/api/v1/admin`)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/admin/stats/overview` | KPI overview (users, papers, pipeline) |
| GET | `/admin/stats/usage` | Product usage analytics |
| GET | `/admin/stats/journals` | Papers per journal (`start_date`, `end_date` filters) |
| GET | `/admin/stats/fetch-status` | Papers fetched last 24h + daily job status |
| GET | `/admin/users` | All users with enriched UserProfile data |
| GET | `/admin/jobs/recent` | Recent background job run logs |
| POST | `/admin/jobs/trigger/fetch` | Manually trigger 7-day paper scraper |

---

## Key Features Implemented

### 1. Dual-Source Paper Ingestion
Papers are fetched from two complementary sources orchestrated in `fetch_job.py`:

- **PubMedFetcher** (`pubmed_fetcher.py`): Queries NCBI E-utilities API by journal name and date range.
- **RssFetcher** (`rss_fetcher.py`): Parses RSS/Atom feeds from configured journals (`config/rss_feeds.json`) using `feedparser` with `User-Agent` headers for publisher compatibility.

Both fetchers run sequentially. Results are deduplicated before insert.

### 2. Smart Deduplication
`deduplicator.py` checks each incoming paper against the database in priority order:
1. `pubmed_id` — exact PubMed record match
2. `doi` — Digital Object Identifier match
3. `title` — case-insensitive string match (via `get_by_title` in `paper_repo.py`)

On a match, a merge is performed: if an RSS-sourced paper (no `pubmed_id`) later has a PubMed record, the existing DB row is updated with the new `pubmed_id`.

### 3. Database Schema
The `Paper` model's `pubmed_id` column is **nullable** to accommodate RSS-sourced papers that have not yet been indexed by PubMed. The schema was migrated using `scripts/force_reset_db.py`.

### 4. AI Pipeline
Each fetched paper goes through two async stages:
1. **Classification** (`classification_job.py`): Categorizes the paper by neurology subspecialty.
2. **Summarization** (summarization module): Generates a structured AI summary using the OpenAI API.

Pending backlog can be processed with `scripts/process_backlog.py`.

### 5. Admin Dashboard (Multi-Screen)
The admin interface is a full-featured multi-screen portal at `/admin` with a persistent sidebar:

| Screen | Route | Purpose |
|---|---|---|
| **Users** | `/admin/users` | Enriched user table (name, specialty, institution, country, last active) + Total/Active 7D metric cards |
| **Papers** | `/admin/papers` | Lifetime total, papers fetched last 24h, daily fetch status widget, date-range-filtered journal stats table, manual fetch trigger button |
| **Analytics** | `/admin/analytics` | Active users, papers viewed, summaries opened, top searches, top subspecialties |
| **Queue Health** | `/admin/queue` | Paginated log of all background job executions with status and error messages |

---

## Setup & Local Development

### Backend
```bash
cd user_service
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python run.py                # Starts on http://127.0.0.1:8001
```

### Frontend
```bash
cd frontend
npm install
npm run dev                  # Starts on http://localhost:3000
```

### Environment Variables
Create a `.env` file in `user_service/`:
```
DATABASE_URL=sqlite:///./user_service.db
SECRET_KEY=your-jwt-secret
OPENAI_API_KEY=sk-...
```

Create a `.env.local` file in `frontend/`:
```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8001/api/v1
```

### Running Background Jobs Manually
```bash
# Fetch papers from last 7 days (RSS + PubMed)
python -m app.modules.papers.jobs.fetch_job

# Classify all pending papers
python -m app.modules.classification.jobs.classification_job

# Process full pending backlog
python scripts/process_backlog.py
```

---

## RSS Feed Configuration
Edit `config/rss_feeds.json` to add or update journal feeds:
```json
{
  "Neurology": "https://n.neurology.org/rss/current.xml",
  "Brain": "https://academic.oup.com/rss/site_5504/advanceAccess_5504.xml"
}
```

---

## Deployment
- **Backend**: Deployed to [Railway](https://railway.app). Set all environment variables in Railway's dashboard.
- **Frontend**: Deployed to [Vercel](https://vercel.com). Set `NEXT_PUBLIC_API_URL` to the Railway backend URL.
