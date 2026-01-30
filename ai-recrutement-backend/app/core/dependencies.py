from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.services.auth_service import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme), authorization: str | None = Header(None)):
    # Debug: afficher l'en-tête Authorization et le token reçu (temporaire)
    try:
        auth_header = authorization
        print("[DEBUG] Authorization header:", auth_header)
        print("[DEBUG] OAuth2 token param:", token)

        payload = decode_token(token)
        print("[DEBUG] Decoded token payload:", payload)
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Missing sub")
    except Exception as e:
        print(f"[DEBUG] get_current_user error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication")

    user = get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive or unknown user")
    return user


def get_current_user_optional(
    db: Session = Depends(get_db),
    token: str | None = Depends(oauth2_scheme_optional),
):
    """Retourne l'utilisateur connecté ou None si pas de token / token invalide."""
    if not token:
        return None
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            return None
        user = get_user_by_id(db, user_id)
        return user if user and user.is_active else None
    except Exception:
        return None


def require_roles(*roles: str):
    def _checker(user=Depends(get_current_user)):
        role_value = user.role.value if hasattr(user.role, "value") else str(user.role)
        if role_value not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden (role)")
        return user

    return _checker
