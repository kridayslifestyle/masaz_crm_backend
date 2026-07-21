import os

from sqlalchemy.orm import Session

from app.models import User, UserRole
from app.services.security import hash_password


def seed_admin(db: Session):
    username = os.getenv("ADMIN_USERNAME")
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")

    if not username or not email or not password:
        print("⚠️ Admin credentials not configured.")
        return

    existing = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if existing:
        print("✅ Admin already exists.")
        return

    admin = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        role=UserRole.admin,
        is_active=True,
    )

    db.add(admin)
    db.commit()

    print("✅ Admin created successfully.")