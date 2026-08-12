from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database import engine, Base, SessionLocal

from app.services.scheduler import scheduler
from app.services.revenue_slab import seed_default_slabs
from app.services.seed_admin import seed_admin

from app.routers import (
    chairs,
    stores,
    collections,
    upload,
    dashboard,
    payouts,
    employees,
    employee_performance,
    machine_health,
    maintenance,
    revenue_analytics,
    alerts,
    reports,
    settings,
    auth,
    users,
    service,
    notifications,
    technician,
)

load_dotenv()


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="MasaZ CRM API",
    description="Backend API for MasaZ Massage Chair Revenue Management CRM",
    version="1.0.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://masaz-crm.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# ROUTERS
# =========================================================

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

app.include_router(service.router)
app.include_router(notifications.router)
app.include_router(technician.router)


# =========================================================
# STARTUP
# =========================================================

@app.on_event("startup")
def on_startup():

    # Create database session
    db = SessionLocal()

    try:
        # Seed default revenue slabs
        seed_default_slabs(db)

        # Create default admin if required
        seed_admin(db)

    finally:
        # Always close database session
        db.close()

    # Start background scheduler
    scheduler.start()

    print("Scheduler Started")


# =========================================================
# SHUTDOWN
# =========================================================

@app.on_event("shutdown")
def on_shutdown():

    try:
        scheduler.shutdown()
        print("Scheduler Stopped")

    except Exception as error:
        print("Scheduler shutdown error:", error)


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "MasaZ CRM API is running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }