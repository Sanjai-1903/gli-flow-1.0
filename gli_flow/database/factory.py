import os
from typing import Optional

from gli_flow.database.database_provider import DatabaseProvider


def create_provider(database_url: Optional[str] = None, db_path: Optional[str] = None) -> DatabaseProvider:
    url = database_url or os.environ.get("DATABASE_URL")
    if url and url.startswith("postgresql"):
        from gli_flow.database.postgres_provider import PostgresProvider
        provider = PostgresProvider(database_url=url)
        provider.connect()
        return provider

    # Only use SupabaseApiProvider when no explicit db_path is given
    # (callers that pass db_path want a local SQLite DB, e.g. upload queue)
    if db_path is None:
        supabase_token = os.environ.get("SUPABASE_API_TOKEN")
        supabase_ref = os.environ.get("SUPABASE_PROJECT_REF")
        if supabase_token and supabase_ref:
            from gli_flow.database.supabase_api_provider import SupabaseApiProvider
            provider = SupabaseApiProvider(project_ref=supabase_ref, api_token=supabase_token)
            provider.connect()
            return provider

    from gli_flow.database.sqlite_provider import SQLiteProvider
    provider = SQLiteProvider(db_path=db_path)
    provider.connect()
    return provider
