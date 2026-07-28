#!/usr/bin/env python3
"""
test_supabase_connection.py — PostgreSQL/Supabase connectivity validation.

Requirements:
  pip install psycopg2-binary  (or psycopg2)

Usage:
  DATABASE_URL="postgresql://user:pass@host:5432/db" python scripts/test_supabase_connection.py

Exit codes:
  0 — All checks passed
  1 — Connection failed
  2 — Query execution failed
"""

import os
import sys


def main() -> int:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable is not set.", file=sys.stderr)
        print("Usage: DATABASE_URL=\"postgresql://...\" python scripts/test_supabase_connection.py", file=sys.stderr)
        return 1

    try:
        import psycopg2
    except ImportError:
        print("ERROR: psycopg2 is not installed.", file=sys.stderr)
        print("Install it: pip install psycopg2-binary", file=sys.stderr)
        return 1

    conn = None
    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cur = conn.cursor()

        # Test 1: PostgreSQL version
        print("=== Test 1: SELECT version() ===")
        cur.execute("SELECT version();")
        row = cur.fetchone()
        print(f"  PostgreSQL version: {row[0]}")

        # Test 2: Current timestamp
        print("\n=== Test 2: SELECT NOW() ===")
        cur.execute("SELECT NOW();")
        row = cur.fetchone()
        print(f"  Server time: {row[0]}")

        # Test 3: Current database
        print("\n=== Test 3: SELECT current_database() ===")
        cur.execute("SELECT current_database();")
        row = cur.fetchone()
        print(f"  Current database: {row[0]}")

        # Test 4: Connection parameters
        print("\n=== Test 4: Connection Info ===")
        print(f"  Host: {conn.info.host}")
        print(f"  Port: {conn.info.port}")
        print(f"  User: {conn.info.user}")
        print(f"  Database: {conn.info.dbname}")
        print(f"  SSL in use: {conn.info.ssl_in_use}")

        # Test 5: Schema introspection capability
        print("\n=== Test 5: Schema Introspection ===")
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        if tables:
            print(f"  Existing tables ({len(tables)}):")
            for t in tables:
                print(f"    - {t[0]}")
        else:
            print("  No tables found in public schema (expected for fresh DB).")

        print("\n✓ All Supabase connectivity checks passed.")
        return 0

    except psycopg2.OperationalError as e:
        print(f"\n✗ Connection failed: {e}", file=sys.stderr)
        return 1
    except psycopg2.Error as e:
        print(f"\n✗ Query execution failed: {e}", file=sys.stderr)
        return 2
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    sys.exit(main())
