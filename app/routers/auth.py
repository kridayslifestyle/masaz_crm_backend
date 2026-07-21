from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.database import get_db
from app.models import User

from app.schemas.auth import (
    LoginRequest
)

from app.services.security import (
    verify_password
)

from app.services.jwt_service import (
    create_access_token
)

from app.dependencies.auth import (
    get_current_user
)

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(
            User.username == form_data.username
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(
        form_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token(
        {
            "sub": user.username,
            "role": user.role.value
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role.value
    }

@router.get("/me")
def me(
    current_user=Depends(
        get_current_user
    )
):
    return current_user

@router.post("/token")
def token_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    print("USERNAME:", form_data.username)

    user = (
        db.query(User)
        .filter(User.username == form_data.username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(
        form_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token(
        {
            "sub": user.username,
            "role": user.role.value
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role.value
    }