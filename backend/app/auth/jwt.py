from datetime import datetime, timedelta, timezone
from jose import jwt
from app.settings import settings

ALGO = "HS256"

def _now():
    return datetime.now(timezone.utc)

def create_access_token(user_id: int) -> str:
    exp = _now() + timedelta(minutes=settings.ACCESS_TOKEN_TTL_MIN)
    payload = {"sub": str(user_id), "iss": settings.JWT_ISSUER, "exp": exp}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGO)

def create_refresh_token(user_id: int) -> str:
    exp = _now() + timedelta(days=settings.REFRESH_TOKEN_TTL_DAYS)
    payload = {"sub": str(user_id), "iss": settings.JWT_ISSUER, "exp": exp, "typ": "refresh"}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGO)

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGO], issuer=settings.JWT_ISSUER)
