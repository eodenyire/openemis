"""Shared FastAPI dependencies"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole, RolePermission, Permission

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def _get_redis():
    """Return Redis client if available, else None (graceful degradation)."""
    try:
        import redis as redis_lib
        from app.core.config import settings as cfg
        redis_url = getattr(cfg, "REDIS_URL", "redis://localhost:6379/0")
        client = redis_lib.from_url(redis_url, decode_responses=True)
        client.ping()
        return client
    except Exception:
        return None


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if not payload:
        raise exc

    # Check Redis blacklist for token JTI
    jti = payload.get("jti")
    if jti:
        redis = _get_redis()
        if redis and redis.get(f"blacklist:{jti}"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )

    username: str = payload.get("sub")
    if not username:
        raise exc
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise exc
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    admin_roles = {UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN}
    if current_user.role not in admin_roles and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def require_teacher(current_user: User = Depends(get_current_user)) -> User:
    allowed = {UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN,
               UserRole.ACADEMIC_DIRECTOR, UserRole.TEACHER}
    if current_user.role not in allowed and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Teacher or admin access required")
    return current_user


def require_permission(permission_code: str):
    """
    Dependency factory — checks that the current user's role has the given permission.
    Usage: Depends(require_permission("students:write:school"))
    Super admins bypass all permission checks.
    """
    def _check(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        if current_user.is_superuser or current_user.role == UserRole.SUPER_ADMIN:
            return current_user
        # Wildcard system permission
        wildcard = (
            db.query(RolePermission)
            .join(Permission)
            .filter(
                RolePermission.role == current_user.role.value,
                Permission.code == "*:*:system",
            )
            .first()
        )
        if wildcard:
            return current_user
        perm = (
            db.query(RolePermission)
            .join(Permission)
            .filter(
                RolePermission.role == current_user.role.value,
                Permission.code == permission_code,
            )
            .first()
        )
        if not perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission_code}",
            )
        return current_user
    return _check
