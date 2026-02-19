"""Clerk authentication dependency for FastAPI.

Verifies Clerk JWT tokens and extracts the authenticated user ID.
Uses PyJWT with RS256 to validate tokens against Clerk's JWKS endpoint.
"""

import os
import jwt
import httpx
from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from functools import lru_cache

from database import get_session
from models.user import User

security = HTTPBearer(auto_error=False)

# Cache JWKS keys to avoid fetching on every request
_jwks_cache: Optional[dict] = None


def _get_clerk_issuer() -> str:
    """Get Clerk issuer URL from environment."""
    clerk_domain = os.getenv("CLERK_DOMAIN", "")
    if not clerk_domain:
        raise ValueError("CLERK_DOMAIN environment variable is required")
    # Clerk issuer format: https://<your-clerk-domain>
    if not clerk_domain.startswith("http"):
        clerk_domain = f"https://{clerk_domain}"
    return clerk_domain


async def _get_jwks() -> dict:
    """Fetch Clerk's JWKS (JSON Web Key Set) for token verification."""
    global _jwks_cache
    if _jwks_cache is not None:
        return _jwks_cache

    issuer = _get_clerk_issuer()
    jwks_url = f"{issuer}/.well-known/jwks.json"

    async with httpx.AsyncClient() as client:
        response = await client.get(jwks_url, timeout=10.0)
        response.raise_for_status()
        _jwks_cache = response.json()
        return _jwks_cache


def _get_signing_key(jwks: dict, token: str) -> str:
    """Extract the correct signing key from JWKS based on token header."""
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")

    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            from jwt.algorithms import RSAAlgorithm
            return RSAAlgorithm.from_jwk(key)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unable to find signing key",
    )


async def verify_clerk_token(token: str) -> dict:
    """Verify a Clerk JWT token and return the payload."""
    try:
        jwks = await _get_jwks()
        signing_key = _get_signing_key(jwks, token)
        issuer = _get_clerk_issuer()

        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            issuer=issuer,
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )


async def get_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> str:
    """Extract and verify the Clerk user ID from the Authorization header.

    Returns the Clerk user_id (sub claim from JWT).
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = await verify_clerk_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID",
        )
    return user_id


async def get_or_create_user(
    clerk_user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Get existing user or create a new one from Clerk user ID.

    Clerk manages user profiles externally. We store a local User record
    linked by the Clerk user_id for database relationships.
    """
    # Look up user by Clerk ID stored in email field (as identifier)
    statement = select(User).where(User.email == f"{clerk_user_id}@clerk.local")
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    if not user:
        # Auto-create local user record on first authenticated request
        user = User(
            email=f"{clerk_user_id}@clerk.local",
            name=None,
            is_active=True,
            hashed_password="clerk-managed",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user
