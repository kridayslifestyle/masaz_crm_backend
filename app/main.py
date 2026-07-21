from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from app.services.scheduler import scheduler
from app.database import engine, Base, SessionLocal
from app.routers import chairs, stores, collections, upload, dashboard
from app.services.revenue_slab import seed_default_slabs
from app.routers import payouts
from app.routers import employees
from app.routers import employee_performance
from app.routers import machine_health
from app.routers import maintenance
from app.routers import revenue_analytics
from app.routers import alerts
from app.routers import reports
from app.routers import settings
from app.routers import auth
from app.routers import users
from app.routers import notifications

load_dotenv()

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MasaZ CRM API",
    description="Backend API for MasaZ Massage Chair Revenue Management CRM",
    version="1.0.0",
)

# ── CORS — allow Next.js frontend ─────────────────────────────────────────────
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(dashboard.router)
app.include_router(chairs.router)
app.include_router(stores.router)
app.include_router(collections.router)
app.include_router(upload.router)
app.include_router(payouts.router)
app.include_router(employees.router)
app.include_router(employee_performance.router)
app.include_router(machine_health.router)
app.include_router(maintenance.router)
app.include_router(revenue_analytics.router)
app.include_router(alerts.router)
app.include_router(reports.router)
app.include_router(settings.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(notifications.router)

# ── Startup ────────────────────────────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    # Seed default revenue slabs if DB is empty
    db = SessionLocal()
    try:
        seed_default_slabs(db)
    finally:
        db.close()

    scheduler.start()
    print("Scheduler Started")

@app.on_event("shutdown")
def on_shutdown():

    scheduler.shutdown()

    print("Scheduler Stopped")
# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ok", "message": "MasaZ CRM API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}
