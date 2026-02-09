from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.auth.jwt import decode_token

bearer = HTTPBearer(auto_error=True)

def get_current_user_id(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
) -> int:
    try:
        payload = decode_token(creds.credentials)
        return int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

def db_dep() -> Session:
    return Depends(get_db)
