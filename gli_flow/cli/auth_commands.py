"""CLI command implementations for `gli-flow login/logout/whoami/sync`.

Kept in a separate module to avoid bloating cli/main.py. main.py registers
subparsers and dispatches to the functions here.
"""

from __future__ import annotations

import sys

from gli_flow.cli.utils import success, warn, info, error, error_and_exit
from gli_flow.cloud import auth as cloud_auth


def login_command(args):
    """`gli-flow login [--token TOKEN] [--web-url URL] [--ingest-url URL]`"""
    web_url = getattr(args, "web_url", None) or cloud_auth.DEFAULT_WEB_URL
    ingest_url = getattr(args, "ingest_url", None) or cloud_auth.DEFAULT_INGEST_URL

    if cloud_auth.is_logged_in():
        state = cloud_auth.load_auth()
        warn(f"Already logged in as {state.email or state.user_id} (token: {state.token_prefix}...)")
        info("To switch accounts: gli-flow logout, then gli-flow login")
        return

    token_arg = getattr(args, "token", None)
    if token_arg:
        # Paste fallback path
        info(f"Verifying token against {ingest_url}...")
        try:
            state = cloud_auth.login_with_token(
                token=token_arg,
                ingest_url=ingest_url,
                web_url=web_url,
            )
        except ValueError as e:
            error_and_exit(str(e), fix="Generate a new token from the dashboard: " + web_url + "/dashboard/tokens")
        except Exception as e:
            error_and_exit(f"Token verification failed: {e}", fix="Check your network and the --ingest-url.")
        success(f"Logged in. Token: {state.token_prefix}... user_id: {state.user_id}")
        return

    # Device flow (default)
    info(f"Starting device-flow login via {web_url}")
    try:
        state = cloud_auth.login_with_device_flow(
            web_url=web_url,
            ingest_url=ingest_url,
            printer=print,
        )
    except cloud_auth.DeviceFlowError as e:
        error_and_exit(
            f"Login failed: {e}",
            fix="Try again, or use --token to paste a token manually.",
        )
    except Exception as e:
        error_and_exit(
            f"Unexpected error during login: {e}",
            fix="If the web app is offline, use `gli-flow login --token gfp_...` with a token you generated earlier.",
        )
    success(f"Logged in as {state.email or state.user_id}")
    info(f"Token stored at ~/.gli-flow/auth.json (prefix: {state.token_prefix}...)")


def logout_command(args):
    """`gli-flow logout`"""
    if cloud_auth.clear_auth():
        success("Logged out. Local token deleted.")
        info("Note: this only removes the token from your machine. "
             "To fully invalidate it, revoke it from the dashboard.")
    else:
        warn("Not logged in.")


def whoami_command(args):
    """`gli-flow whoami` — verify token against server and print current identity."""
    try:
        state = cloud_auth.load_auth()
    except cloud_auth.NotLoggedInError as e:
        error_and_exit(str(e), fix="Run: gli-flow login")

    info(f"Local auth file:")
    info(f"  email:      {state.email or '(unknown)'}")
    info(f"  user_id:    {state.user_id}")
    info(f"  token:      {state.token_prefix}...")
    info(f"  web_url:    {state.web_url}")
    info(f"  ingest_url: {state.ingest_url}")
    info(f"  logged in:  {state.logged_in_at}")

    info("\nVerifying with server...")
    try:
        result = cloud_auth.verify_token(state.ingest_url, state.token)
        success(f"Server confirms user_id={result.get('user_id')}")
    except ValueError as e:
        error_and_exit(str(e), fix="Your token was revoked. Run: gli-flow logout && gli-flow login")
    except Exception as e:
        error_and_exit(f"Could not reach {state.ingest_url}: {e}",
                       fix="Check your network. Local runs still work while offline.")


def sync_command(args):
    """`gli-flow sync` — drain the local upload queue to the cloud."""
    from gli_flow.cloud.sync import SyncEngine

    if not cloud_auth.is_logged_in():
        error_and_exit("Not logged in.", fix="Run: gli-flow login")

    dry_run = getattr(args, "dry_run", False)
    purge = getattr(args, "purge_synced", False)
    daemon = getattr(args, "daemon", False)

    engine = SyncEngine()
    if daemon:
        info("Starting sync daemon (Ctrl+C to stop)...")
        engine.run_daemon()
        return

    stats = engine.sync_once(dry_run=dry_run)
    if stats["attempted"] == 0:
        info("Nothing to sync. Local queue is empty.")
    else:
        success(f"Sync: {stats['synced']} uploaded, {stats['failed']} failed, {stats['skipped']} skipped.")

    if purge:
        purged = engine.purge_old_synced()
        info(f"Retention: purged {purged} synced runs older than 7 days.")


def sync_status_command(args):
    """`gli-flow sync-status` — show local queue + retention info."""
    from gli_flow.cloud.sync import SyncEngine
    engine = SyncEngine()
    stats = engine.queue_stats()
    info(f"Local upload queue:")
    info(f"  total items:       {stats['total']}")
    info(f"  pending:           {stats['by_status'].get('pending', 0)}")
    info(f"  failed (retrying): {stats['by_status'].get('failed', 0)}")
    info(f"  in progress:       {stats['by_status'].get('in_progress', 0)}")
    info(f"  completed:         {stats['by_status'].get('completed', 0)}")
    ret = engine.retention_stats()
    info(f"\nRetention:")
    info(f"  synced runs on disk:  {ret['synced_runs_on_disk']}")
    info(f"  eligible for purge:   {ret['eligible_for_purge']} (>{ret['retention_days']}d since sync)")
