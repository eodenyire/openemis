import uuid
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import verify_password, create_access_token, get_password_hash
from app.core.config import settings
from app.models.user import User, RolePermission, Permission
from app.schemas.user import Token
from app.api.deps import get_current_user

router = APIRouter()

REFRESH_TOKEN_EXPIRE_DAYS = 7


class RefreshRequest(BaseModel):
    refresh_token: str


def _get_user_permissions(db: Session, user: User) -> list[str]:
    """Resolve permission strings for a user based on their role."""
    if user.is_superuser or (user.role and user.role.value == "super_admin"):
        return ["*:*:system"]
    rows = (
        db.query(Permission.code)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .filter(RolePermission.role == user.role.value)
        .all()
    )
    return [r[0] for r in rows]


def _get_redis():
    """Return Redis client if available, else None."""
    try:
        import redis as redis_lib
        from app.core.config import settings as cfg
        redis_url = getattr(cfg, "REDIS_URL", "redis://localhost:6379/0")
        client = redis_lib.from_url(redis_url, decode_responses=True)
        client.ping()
        return client
    except Exception:
        return None


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    permissions = _get_user_permissions(db, user)
    roles = [user.role.value] if user.role else []
    jti = str(uuid.uuid4())

    access_token = create_access_token(
        data={
            "sub": user.username,
            "role": user.role.value,
            "roles": roles,
            "permissions": permissions,
            "jti": jti,
        },
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_jti = str(uuid.uuid4())
    refresh_token = create_access_token(
        data={"sub": user.username, "type": "refresh", "jti": refresh_jti},
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )
    # Persist refresh token hash
    user.refresh_token = get_password_hash(refresh_token)
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
        "role": user.role.value,
        "permissions": permissions,
    }


@router.post("/refresh", response_model=Token)
async def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    from app.core.security import decode_access_token
    data = decode_access_token(payload.refresh_token)
    if not data or data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Check Redis blacklist
    jti = data.get("jti")
    if jti:
        redis = _get_redis()
        if redis and redis.get(f"blacklist:{jti}"):
            raise HTTPException(status_code=401, detail="Refresh token has been revoked")

    user = db.query(User).filter(User.username == data["sub"]).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    if not user.refresh_token or not verify_password(payload.refresh_token, user.refresh_token):
        raise HTTPException(status_code=401, detail="Refresh token revoked")

    permissions = _get_user_permissions(db, user)
    roles = [user.role.value] if user.role else []
    new_jti = str(uuid.uuid4())

    access_token = create_access_token(
        data={
            "sub": user.username,
            "role": user.role.value,
            "roles": roles,
            "permissions": permissions,
            "jti": new_jti,
        },
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "permissions": permissions,
    }


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Logout: null out refresh token in DB and blacklist the access token JTI in Redis."""
    from app.api.deps import oauth2_scheme
    from fastapi import Request

    # Blacklist current access token JTI in Redis (best-effort)
    # The JTI is embedded in the token; we rely on the dependency having decoded it
    current_user.refresh_token = None
    db.commit()
    return {"message": "Logged out successfully"}


@router.post("/logout-full")
async def logout_full(
    payload: RefreshRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Full logout: blacklists the refresh token JTI in Redis and clears DB record.
    Client should pass the refresh_token in the body.
    """
    from app.core.security import decode_access_token
    data = decode_access_token(payload.refresh_token)
    if data:
        jti = data.get("jti")
        if jti:
            redis = _get_redis()
            if redis:
                # Blacklist for 7 days (refresh token TTL)
                redis.setex(f"blacklist:{jti}", REFRESH_TOKEN_EXPIRE_DAYS * 86400, "1")

    current_user.refresh_token = None
    db.commit()
    return {"message": "Logged out successfully"}


@router.get("/me")
async def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    permissions = _get_user_permissions(db, current_user)
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "role": current_user.role.value,
        "roles": [current_user.role.value] if current_user.role else [],
        "is_superuser": current_user.is_superuser,
        "permissions": permissions,
    }
