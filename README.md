# Ledger

Receipt and expense tracking system that converts unstructured receipt images into structured, queryable financial data using Google Cloud Vision OCR and OpenAI NLP extraction.

## Overview

Ledger automates the tedious process of manual expense entry. Users photograph receipts, and the system automatically extracts text via OCR, then parses that text into structured expense records (vendor, amount, category, transaction date). The result is a searchable ledger that maintains both the original receipt image and the extracted financial data.

**Target users:** Freelancers tracking business expenses, individuals managing personal finances, or anyone tired of shoebox receipt management.

## Architecture

Ledger follows a clean architecture pattern with strict layer boundaries:

```
app/
├── main.py              # FastAPI application entry point
├── routers/             # API layer — HTTP parsing, auth extraction, response formatting
├── services/            # Business logic — orchestrates operations across repos and clients
├── repos/               # Data access — all database reads/writes
├── clients/             # External APIs — Google Cloud Vision, OpenAI, cloud storage
├── models/              # SQLAlchemy ORM models (User, Receipt, Expense)
└── schemas/             # Pydantic request/response schemas
db/
└── migrations/          # SQL migration files
web/                     # React + TypeScript frontend (Vite)
tests/
├── unit/                # Pure function tests
├── integration/         # Database repository tests
└── api/                 # FastAPI endpoint tests
```

### Layer Rules

| Layer | Can Call | Cannot Import |
|-------|---------|---------------|
| **Routers** | Services | SQLAlchemy models, DB queries, external API clients |
| **Services** | Repos, Clients | FastAPI, SQL strings, direct HTTP clients |
| **Repos** | Database (SQLAlchemy) | Services, Clients, FastAPI |
| **Clients** | External APIs (httpx) | Database, Services, FastAPI |

## Tech Stack

- **Backend:** Python 3.12+, FastAPI, uvicorn
- **Database:** PostgreSQL 15+ (Neon serverless), asyncpg
- **Frontend:** React 18, TypeScript, Vite
- **OCR:** Google Cloud Vision API
- **NLP:** OpenAI GPT-4o-mini
- **Auth:** JWT (python-jose + passlib/bcrypt)
- **Deployment:** Render (backend web service + frontend static site)

## Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 15+ (or Neon account)
- Google Cloud Platform account with Vision API enabled
- OpenAI API key

## Quick Start

### Using boot script (Windows PowerShell)

```powershell
./boot.ps1
```

This script will:
1. Create a Python virtual environment and install backend dependencies
2. Install frontend dependencies
3. Start the FastAPI backend (uvicorn) and Vite dev server

### Manual Setup

#### Backend

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\Activate.ps1  # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend

```bash
cd web
npm install
npm run dev
```

#### Verify

```bash
# Health check
curl http://localhost:8000/health
# Expected: {"status": "ok"}
```

## Environment Variables

Create a `.env` file in the project root:

```env
# Required
DATABASE_URL=postgresql://user:pass@host/ledger
JWT_SECRET=your-secret-key-here
JWT_REFRESH_SECRET=your-refresh-secret-here
GOOGLE_CLOUD_VISION_CREDENTIALS=/path/to/gcp-key.json
OPENAI_API_KEY=sk-proj-abc123...
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000

# Optional (defaults shown)
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
MAX_UPLOAD_SIZE_MB=10
ALLOWED_IMAGE_TYPES=image/jpeg,image/png,image/webp
ENVIRONMENT=development
LOG_LEVEL=INFO
```

## Running Tests

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all backend tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/api/
```

Frontend tests:

```bash
cd web
npm test
```

## API Endpoints

### Health
- `GET /health` — Health check

### Authentication
- `POST /auth/register` — Create user account
- `POST /auth/login` — Authenticate, returns JWT

### Receipts (requires auth)
- `POST /receipts` — Upload receipt image (triggers OCR)
- `GET /receipts` — List all receipts for user
- `GET /receipts/{id}` — Get receipt details with OCR text
- `DELETE /receipts/{id}` — Delete receipt

### Expenses (requires auth)
- `POST /expenses` — Create expense (auto from receipt or manual)
- `GET /expenses` — List expenses with filters (?category, ?start_date, ?end_date, ?vendor)
- `GET /expenses/{id}` — Get expense details
- `DELETE /expenses/{id}` — Delete expense

## Data Flow

```
Receipt Upload:
  User → POST /receipts (image) → StorageClient → OCRClient → Database

Expense Extraction:
  User → POST /expenses (receipt_id) → NLPClient (OpenAI) → Database

Expense Query:
  User → GET /expenses?filters → Database → Filtered results
```

## Deployment

### Render (Production)

**Backend (Web Service):**
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Frontend (Static Site):**
- Root directory: `web`
- Build command: `npm run build`
- Publish directory: `dist`

**Database:** Neon PostgreSQL (external managed service)

## License

Private — all rights reserved.
