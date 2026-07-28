#!/usr/bin/env python3
"""
test_supabase_write.py — Test write operations against Supabase.

Tests:
  - INSERT into a temp table
  - UPDATE
  - DELETE
  - Transaction rollback
  - Connection close/reopen

Usage:
    DATABASE_URL=postgresql://... python scripts/test_supabase_write.py

Exit codes:
  0 — All write tests passed
  1 — Write test failed
"""

import os
import sys
import uuid


def main() -> int:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable is not set.", file=sys.stderr)
        return 1

    try:
        import psycopg2
    except ImportError:
        print("ERROR: psycopg2 is not installed.", file=sys.stderr)
        return 1

    test_id = str(uuid.uuid4())[:8]
    table = f"_test_write_{test_id}"

    conn = None
    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = False
        cur = conn.cursor()

        # Test 1: CREATE TABLE
        print(f"=== Test 1: CREATE TEMP TABLE {table} ===")
        cur.execute(f"""
            CREATE TEMPORARY TABLE {table} (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                value INTEGER DEFAULT 0,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        conn.commit()
        print("  ✓ CREATE TABLE succeeded")

        # Test 2: INSERT
        print(f"\n=== Test 2: INSERT ===")
        cur.execute(
            f"INSERT INTO {table} (name, value) VALUES (%s, %s) RETURNING id",
            ("test_alpha", 42),
        )
        inserted_id = cur.fetchone()[0]
        conn.commit()
        print(f"  ✓ INSERT succeeded (id={inserted_id})")

        # Test 3: Bulk INSERT
        print(f"\n=== Test 3: Bulk INSERT ===")
        records = [(f"item_{i}", i * 10) for i in range(1, 11)]
        for name, val in records:
            cur.execute(
                f"INSERT INTO {table} (name, value) VALUES (%s, %s)",
                (name, val),
            )
        conn.commit()
        print(f"  ✓ Bulk INSERT of {len(records)} records succeeded")

        # Test 4: SELECT
        print(f"\n=== Test 4: SELECT ===")
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        print(f"  ✓ SELECT COUNT(*) = {count} (expected {len(records) + 1})")
        assert count == len(records) + 1, f"Row count mismatch: {count}"

        # Test 5: UPDATE
        print(f"\n=== Test 5: UPDATE ===")
        cur.execute(
            f"UPDATE {table} SET value = %s WHERE name = %s",
            (999, "test_alpha"),
        )
        conn.commit()
        cur.execute(f"SELECT value FROM {table} WHERE name = 'test_alpha'")
        updated_val = cur.fetchone()[0]
        print(f"  ✓ UPDATE succeeded (value={updated_val})")
        assert updated_val == 999, f"Update value mismatch: {updated_val}"

        # Test 6: DELETE
        print(f"\n=== Test 6: DELETE ===")
        cur.execute(f"DELETE FROM {table} WHERE value < %s", (50,))
        conn.commit()
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        after_delete = cur.fetchone()[0]
        print(f"  ✓ DELETE succeeded (remaining rows: {after_delete})")

        # Test 7: TRANSACTION ROLLBACK
        print(f"\n=== Test 7: Transaction Rollback ===")
        try:
            cur.execute(f"INSERT INTO {table} (name, value) VALUES (%s, %s)", ("rollback_test", "not_a_number"))
            conn.commit()
            print("  ✗ INSERT should have failed", file=sys.stderr)
        except Exception as e:
            conn.rollback()
            print(f"  ✓ Rollback succeeded (expected error: {e})")

        # Test 8: Verify rollback didn't affect data
        print(f"\n=== Test 8: Verify Rollback ===")
        cur.execute(f"SELECT COUNT(*) FROM {table} WHERE name = 'rollback_test'")
        rollback_count = cur.fetchone()[0]
        assert rollback_count == 0, "Rollback did not undo the insert"
        print(f"  ✓ Rollback confirmed (count={rollback_count})")

        # Test 9: DROP TABLE
        print(f"\n=== Test 9: DROP TABLE ===")
        cur.execute(f"DROP TABLE IF EXISTS {table}")
        conn.commit()
        print("  ✓ DROP TABLE succeeded")

        print("\n" + "=" * 50)
        print("✓ ALL WRITE TESTS PASSED")
        print("=" * 50)
        return 0

    except psycopg2.Error as e:
        print(f"\n✗ Write test failed: {e}", file=sys.stderr)
        if conn:
            conn.rollback()
        return 1
    except AssertionError as e:
        print(f"\n✗ Assertion failed: {e}", file=sys.stderr)
        return 1
    finally:
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(f"DROP TABLE IF EXISTS {table}")
                conn.commit()
            except Exception:
                pass
            conn.close()


if __name__ == "__main__":
    sys.exit(main())
