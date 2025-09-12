import os
import jwt
import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_JWT_AUD = os.getenv("SUPABASE_JWT_AUD", "authenticated")
SUPABASE_JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"

security = HTTPBearer()

def get_supabase() -> Client:
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise RuntimeError("Missing Supabase env vars")
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# cache jwks (naif)
_jwks = None
def _get_jwks():
    global _jwks
    if _jwks is None:
        resp = requests.get(SUPABASE_JWKS_URL, timeout=5)
        resp.raise_for_status()
        _jwks = resp.json()
    return _jwks

def _decode_jwt(token: str):
    jwks = _get_jwks()
    try:
        return jwt.decode(
            token,
            key=jwt.PyJWKClient(SUPABASE_JWKS_URL).get_signing_key_from_jwt(token).key,
            algorithms=["RS256"],
            audience=SUPABASE_JWT_AUD,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {e}")

def get_current_user_id(creds: HTTPAuthorizationCredentials = Depends(security)) -> str:
    payload = _decode_jwt(creds.credentials)
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="No sub in token")
    return sub
