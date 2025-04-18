import asyncio
import httpx
import os
from cachetools import TTLCache
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError


KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "reports-realm")
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://keycloak:8080")
KEYCLOAK_JWKS_URL = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"
REQUIRED_ROLE = os.getenv("REQUIRED_ROLE", "prothetic_user")
ALGORITHM = "RS256"


security = HTTPBearer()


async def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        kid = get_kid_from_token(token)
        keys = await get_cached_public_keys()
        key_data = next((k for k in keys if k["kid"] == kid), None)

        if not key_data:
            raise HTTPException(status_code=401, detail="Invalid token header")

        payload = jwt.decode(token, key_data, algorithms=[ALGORITHM])

        roles = payload.get("realm_access", {}).get("roles", [])
        if REQUIRED_ROLE not in roles:
            raise HTTPException(status_code=403, detail="Missing required role")

        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_kid_from_token(token: str):
    unverified_header = jwt.get_unverified_header(token)
    return unverified_header["kid"]


key_cache = TTLCache(maxsize=10, ttl=3600)


async def get_cached_public_keys():
    if "jwks" in key_cache:
        return key_cache["jwks"]
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(KEYCLOAK_JWKS_URL)
        jwks = resp.json()
        key_cache["jwks"] = jwks["keys"]
        return key_cache["jwks"]
