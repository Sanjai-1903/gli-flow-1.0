"""Supabase JWT validation for browser-originated requests.

The dashboard authenticates users via Supabase (Google OAuth). When the
browser calls our FastAPI server, it sends the Supabase session's
access_token as a Bearer header. We validate it here.

Supabase has two token-signing modes:

    1. Legacy — HS256 with a shared secret (SUPABASE_JWT_SECRET).
    2. Modern — asymmetric ES256/RS256 with keys published at
       {SUPABASE_URL}/auth/v1/.well-known/jwks.json

We support both. We try JWKS first (works for both new-style asymmetric
projects and any project that publishes keys), and fall back to the
shared secret if JWKS isn't reachable or the token is HS256.

Required env vars:
    SUPABASE_URL             https://<project>.supabase.co
    SUPABASE_JWT_SECRET      only needed for legacy HS256 projects
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Optional

from fastapi import Request, HTTPException

logger = logging.getLogger(__name__)

# Module-level cache so we don't refetch JWKS on every request.
_jwks_client_cache = None


@dataclass
class SupabaseUser:
    id: str        # UUID from Supabase auth.users.id
    email: str
    role: str      # "authenticated" for real users


def _jwt_secret() -> Optional[str]:
    return os.environ.get("SUPABASE_JWT_SECRET")


def _jwks_url() -> Optional[str]:
    """Supabase's public JWKS endpoint, derived from SUPABASE_URL."""
    base = os.environ.get("SUPABASE_URL", "")
    if not base:
        # Try to derive from GLI_DATABASE_URL host: postgres.<ref>.pooler...
        # This is a heuristic — set SUPABASE_URL explicitly for reliability.
        db = os.environ.get("GLI_DATABASE_URL", "")
        if "postgres." in db and ".pooler." in db:
            try:
                ref = db.split("postgres.", 1)[1].split(":", 1)[0]
                return f"https://{ref}.supabase.co/auth/v1/.well-known/jwks.json"
            except Exception:
                return None
        return None
    return base.rstrip("/") + "/auth/v1/.well-known/jwks.json"


def _get_jwks_client():
    """Lazy-init a PyJWKClient pointed at Supabase's public keys."""
    global _jwks_client_cache
    if _jwks_client_cache is not None:
        return _jwks_client_cache
    url = _jwks_url()
    if not url:
        return None
    try:
        from jwt import PyJWKClient
        _jwks_client_cache = PyJWKClient(url, cache_keys=True, lifespan=3600)
        return _jwks_client_cache
    except Exception as e:
        logger.warning("Could not initialize JWKS client (%s); falling back to HS256", e)
        return None


def _decode(token: str) -> dict:
    """Decode + verify a Supabase JWT. Raises HTTPException on failure."""
    try:
        import jwt  # PyJWT
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="PyJWT not installed. Run: pip install pyjwt",
        )

    common_kwargs = dict(
        audience="authenticated",
        options={"require": ["exp", "sub"]},
    )

    # ---- Try JWKS (asymmetric ES256/RS256) ----
    jwks_client = _get_jwks_client()
    if jwks_client is not None:
        try:
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            return jwt.decode(
                token,
                signing_key.key,
                algorithms=["ES256", "RS256", "EdDSA"],
                **common_kwargs,
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Session expired. Sign in again.")
        except jwt.InvalidAudienceError:
            raise HTTPException(status_code=401, detail="Invalid token audience")
        except jwt.PyJWKClientError as e:
            logger.warning("JWKS lookup failed (%s); trying HS256 fallback", e)
        except jwt.InvalidTokenError as e:
            # Might be an HS256 token — fall through to shared-secret path.
            logger.debug("JWKS decode failed (%s); trying HS256 fallback", e)

    # ---- Fall back to HS256 shared secret ----
    secret = _jwt_secret()
    if secret:
        try:
            return jwt.decode(
                token,
                secret,
                algorithms=["HS256"],
                **common_kwargs,
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Session expired. Sign in again.")
        except jwt.InvalidAudienceError:
            raise HTTPException(status_code=401, detail="Invalid token audience")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    # Dev fallback (opt-in): decode without verifying signature.
    if os.environ.get("GLI_ALLOW_UNVERIFIED_JWT") == "1":
        logger.warning("Accepting UNVERIFIED JWT (dev mode).")
        return jwt.decode(token, options={"verify_signature": False, "verify_aud": False})

    raise HTTPException(
        status_code=500,
        detail=(
            "Cannot verify Supabase JWT. Set SUPABASE_URL (for asymmetric "
            "keys) and/or SUPABASE_JWT_SECRET (for legacy HS256)."
        ),
    )


def _extract_bearer(request: Request) -> Optional[str]:
    header = request.headers.get("Authorization", "")
    if not header.lower().startswith("bearer "):
        return None
    return header.split(" ", 1)[1].strip() or None


def require_supabase_user(request: Request) -> SupabaseUser:
    """FastAPI dependency: extract + verify the caller's Supabase session."""
    token = _extract_bearer(request)
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization: Bearer <supabase-access-token>",
        )
    payload = _decode(token)
    user_id = payload.get("sub")
    email = payload.get("email", "")
    role = payload.get("role", "")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token has no subject")
    return SupabaseUser(id=str(user_id), email=str(email), role=str(role))
