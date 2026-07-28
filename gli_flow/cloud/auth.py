"""CLI authentication: device flow + paste fallback + local token storage.

Storage: ~/.gli-flow/auth.json
    {
      "token": "gfp_...",
      "token_prefix": "gfp_1a2b3c",
      "user_id": "uuid",
      "email": "user@example.com",
      "web_url": "https://app.example.com",
      "ingest_url": "https://ingest.example.com",
      "logged_in_at": "2026-07-27T18:00:00Z"
    }

Device flow:
    1. POST {web}/api/cli/device/authorize
       -> { device_code, user_code, verification_uri, expires_in, interval }
    2. Show user_code + open verification_uri in browser
    3. Poll POST {web}/api/cli/device/poll with { device_code }
       every `interval` seconds until:
         - 200 with { access_token, user_id, email }  -> save + done
         - 400 with { error: "authorization_pending" } -> keep polling
         - 400 with { error: "expired_token" }         -> give up
         - 400 with { error: "access_denied" }         -> give up

Paste fallback:
    User visits web dashboard, generates a token, pastes it into
    `gli-flow login --token gfp_xxx`. We verify it by hitting
    {ingest}/api/v1/whoami with the token.
"""

from __future__ import annotations

import json
import os
import time
import webbrowser
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx


AUTH_DIR = Path.home() / ".gli-flow"
AUTH_FILE = AUTH_DIR / "auth.json"

# Sensible defaults — override with env vars or `gli-flow config`.
DEFAULT_WEB_URL = os.environ.get(
    "GLI_WEB_URL",
    "https://gli-flow.vercel.app",
)
DEFAULT_INGEST_URL = os.environ.get(
    "GLI_INGEST_URL",
    os.environ.get("GLI_SERVER_URL", "http://localhost:8100"),
)


@dataclass
class AuthState:
    token: str
    token_prefix: str
    user_id: str
    email: str
    web_url: str
    ingest_url: str
    logged_in_at: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "AuthState":
        return cls(**{k: d.get(k, "") for k in cls.__dataclass_fields__})


class NotLoggedInError(Exception):
    pass


def load_auth() -> AuthState:
    if not AUTH_FILE.exists():
        raise NotLoggedInError("Not logged in. Run: gli-flow login")
    try:
        with open(AUTH_FILE, "r") as f:
            return AuthState.from_dict(json.load(f))
    except Exception as e:
        raise NotLoggedInError(f"Auth file unreadable ({e}). Run: gli-flow login")


def save_auth(state: AuthState) -> None:
    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    with open(AUTH_FILE, "w") as f:
        json.dump(state.to_dict(), f, indent=2)
    try:
        os.chmod(AUTH_FILE, 0o600)  # user-only
    except OSError:
        pass


def clear_auth() -> bool:
    if AUTH_FILE.exists():
        AUTH_FILE.unlink()
        return True
    return False


def is_logged_in() -> bool:
    return AUTH_FILE.exists()


def _prefix(token: str) -> str:
    """First 12 chars of the token, for display only."""
    return token[:12] if len(token) > 12 else token


# ---------- Verification (used by paste fallback and post-device-flow) ----------

def verify_token(ingest_url: str, token: str, timeout: float = 15.0) -> dict:
    """Verify a token against the ingest server's /whoami endpoint.

    Returns { user_id, authenticated: True } on success.
    Raises on HTTP error / invalid token.
    """
    url = ingest_url.rstrip("/") + "/api/v1/whoami"
    with httpx.Client(timeout=timeout) as client:
        resp = client.get(url, headers={"Authorization": f"Bearer {token}"})
    if resp.status_code == 401:
        raise ValueError("Server rejected the token (401). Check the token or the ingest URL.")
    resp.raise_for_status()
    return resp.json()


# ---------- Device flow (default) ----------

class DeviceFlowError(Exception):
    pass


def start_device_flow(ingest_url: str, timeout: float = 15.0) -> dict:
    """POST /api/v1/cli/device/authorize -> { device_code, user_code, verification_uri, expires_in, interval }.

    Note: hits the INGEST server (FastAPI). The returned verification_uri
    points at the WEB dashboard (Vercel) where the user approves.
    """
    url = ingest_url.rstrip("/") + "/api/v1/cli/device/authorize"
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(url, json={})
    if resp.status_code >= 400:
        raise DeviceFlowError(
            f"Device authorize failed ({resp.status_code}): {resp.text[:200]}"
        )
    return resp.json()


def poll_device_flow(
    ingest_url: str,
    device_code: str,
    interval: int,
    expires_in: int,
    on_wait: Optional[callable] = None,
) -> dict:
    """Poll until approved, denied, or expired.

    Returns { access_token, user_id, email } on success.
    Raises DeviceFlowError otherwise.
    """
    url = ingest_url.rstrip("/") + "/api/v1/cli/device/poll"
    deadline = time.time() + expires_in
    interval = max(2, interval)  # never spam
    with httpx.Client(timeout=15.0) as client:
        while time.time() < deadline:
            time.sleep(interval)
            if on_wait:
                on_wait(int(deadline - time.time()))
            try:
                resp = client.post(url, json={"device_code": device_code})
            except httpx.RequestError as e:
                # Transient network hiccup — keep polling
                continue
            if resp.status_code == 200:
                return resp.json()
            body = {}
            try:
                body = resp.json()
            except Exception:
                pass
            # FastAPI HTTPException wraps our payload under "detail".
            err_container = body.get("detail", body) if isinstance(body, dict) else {}
            if isinstance(err_container, str):
                err = err_container
            else:
                err = (err_container or {}).get("error", "")
            if err == "authorization_pending":
                continue
            if err == "slow_down":
                interval += 2
                continue
            if err == "access_denied":
                raise DeviceFlowError("Access denied. You clicked 'Cancel' on the approval page.")
            if err == "expired_token":
                raise DeviceFlowError("The login attempt expired. Run `gli-flow login` again.")
            # Unknown error
            raise DeviceFlowError(
                f"Unexpected response from server ({resp.status_code}): {resp.text[:200]}"
            )
    raise DeviceFlowError("Login timed out. Run `gli-flow login` again.")


# ---------- Public entry points ----------

def login_with_token(
    token: str,
    ingest_url: str = DEFAULT_INGEST_URL,
    web_url: str = DEFAULT_WEB_URL,
    email: str = "",
) -> AuthState:
    """Paste-fallback login: verify token, save it."""
    if not token.strip():
        raise ValueError("Empty token.")
    info = verify_token(ingest_url, token.strip())
    state = AuthState(
        token=token.strip(),
        token_prefix=_prefix(token.strip()),
        user_id=str(info.get("user_id", "")),
        email=email or "",
        web_url=web_url,
        ingest_url=ingest_url,
        logged_in_at=datetime.now(timezone.utc).isoformat(),
    )
    save_auth(state)
    return state


def login_with_device_flow(
    web_url: str = DEFAULT_WEB_URL,
    ingest_url: str = DEFAULT_INGEST_URL,
    open_browser: bool = True,
    printer: callable = print,
) -> AuthState:
    """Device flow login: open browser, poll for approval, save token."""
    session = start_device_flow(ingest_url)
    device_code = session["device_code"]
    user_code = session["user_code"]
    # Server returns a verification URI derived from GLI_WEB_URL. If the
    # user overrode --web-url, prefer that.
    verification_uri = (
        web_url.rstrip("/") + "/cli/device"
        if web_url and web_url != DEFAULT_WEB_URL
        else session.get("verification_uri", web_url.rstrip("/") + "/cli/device")
    )
    interval = int(session.get("interval", 5))
    expires_in = int(session.get("expires_in", 900))

    printer("")
    printer(f"  To finish signing in, open this URL in a browser:")
    printer(f"    {verification_uri}?user_code={user_code}")
    printer("")
    printer(f"  And enter this code:")
    printer(f"    {user_code}")
    printer("")

    if open_browser:
        try:
            webbrowser.open(f"{verification_uri}?user_code={user_code}")
        except Exception:
            pass

    printer("  Waiting for approval...")

    result = poll_device_flow(
        ingest_url=ingest_url,
        device_code=device_code,
        interval=interval,
        expires_in=expires_in,
    )
    token = result["access_token"]
    user_id = str(result.get("user_id", ""))
    email = str(result.get("email", ""))

    state = AuthState(
        token=token,
        token_prefix=_prefix(token),
        user_id=user_id,
        email=email,
        web_url=web_url,
        ingest_url=ingest_url,
        logged_in_at=datetime.now(timezone.utc).isoformat(),
    )
    save_auth(state)
    return state


def get_auth_headers() -> dict:
    """Return the Authorization header for an authenticated CLI request."""
    state = load_auth()
    return {"Authorization": f"Bearer {state.token}"}


def get_ingest_url() -> str:
    try:
        return load_auth().ingest_url
    except NotLoggedInError:
        return DEFAULT_INGEST_URL
