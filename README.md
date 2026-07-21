# MasaZ CRM — Backend Setup

## Prerequisites
- Python 3.11+
- PostgreSQL running locally

---

## Step 1 — Create virtual environment

```bash
cd masaz_crm_backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

## Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

## Step 3 — Create PostgreSQL database

Open pgAdmin or psql and run:
```sql
CREATE DATABASE masaz_crm;
```

## Step 4 — Configure .env

Copy `.env.example` to `.env` and fill in your DB password:
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/masaz_crm
ALLOWED_ORIGINS=http://localhost:3000
```

## Step 5 — Run the server

```bash
uvicorn app.main:app --reload --port 8000
```

Server starts at: http://localhost:8000
API docs (Swagger): http://localhost:8000/docs

---

## Folder Structure

```
masaz_crm_backend/
├── app/
│   ├── main.py              ← FastAPI app entry point
│   ├── database.py          ← SQLAlchemy + DB connection
│   ├── models.py            ← All DB tables (Chair, Store, Collection)
│   ├── routers/
│   │   ├── dashboard.py     ← GET /api/dashboard/summary
│   │   ├── chairs.py        ← GET/POST/PATCH /api/chairs
│   │   ├── stores.py        ← GET/POST/PATCH /api/stores
│   │   ├── collections.py   ← GET/POST/PATCH /api/collections
│   │   └── upload.py        ← POST /api/upload/chairs (Excel)
│   ├── schemas/
│   │   ├── chair.py         ← Pydantic request/response models
│   │   ├── store.py
│   │   └── collection.py
│   └── services/
│       ├── revenue_slab.py  ← Auto % calculation logic
│       └── excel_parser.py  ← Parse uploaded Excel files
├── .env.example
├── requirements.txt
└── README.md
```

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | /api/dashboard/summary | All KPIs for home page |
| GET | /api/chairs | List all chairs |
| POST | /api/chairs | Add a chair |
| PATCH | /api/chairs/{id} | Update chair |
| GET | /api/stores | List all stores |
| POST | /api/stores | Add a store |
| GET | /api/collections | List collections |
| POST | /api/collections | Add collection (auto-calculates %) |
| GET | /api/collections/summary/totals | Revenue totals |
| POST | /api/upload/chairs | Upload Excel to import chairs |