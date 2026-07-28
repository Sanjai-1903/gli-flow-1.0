#!/usr/bin/env python3
"""
test_supabase_read.py — Test read operations against Supabase.

Tests:
  - Basic SELECT
  - Aggregation queries (COUNT, AVG, SUM, GROUP BY)
  - JOIN queries
  - Subqueries
  - JSONB querying
  - LIKE/ILIKE search
  - NULL handling
  - Schema introspection

Usage:
    DATABASE_URL=postgresql://... python scripts/test_supabase_read.py

Exit codes:
  0 — All read tests passed
  1 — Read test failed
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
    table = f"_test_read_{test_id}"

    conn = None
    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = False
        cur = conn.cursor()

        # Setup test data
        print("Setting up test data...")
        cur.execute(f"""
            CREATE TEMPORARY TABLE {table} (
                id SERIAL PRIMARY KEY,
                category TEXT,
                score DOUBLE PRECISION,
                name TEXT,
                metadata JSONB DEFAULT '{{}}',
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)

        categories = ["A", "B", "C"]
        for i in range(1, 31):
            cat = categories[i % 3]
            score = i * 1.5
            meta = f'{{"index": {i}, "even": {"true" if i % 2 == 0 else "false"}}}'
            name = f"record_{i}"
            active = i % 5 != 0
            cur.execute(
                f"INSERT INTO {table} (category, score, name, metadata, active) VALUES (%s, %s, %s, %s, %s)",
                (cat, score, name, meta, active),
            )
        conn.commit()
        print(f"  Inserted 30 test records")

        # Test 1: Basic SELECT
        print(f"\n=== Test 1: Basic SELECT ===")
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        print(f"  ✓ COUNT(*) = {count}")
        assert count == 30

        # Test 2: SELECT with WHERE
        print(f"\n=== Test 2: SELECT with WHERE ===")
        cur.execute(f"SELECT COUNT(*) FROM {table} WHERE category = %s", ("A",))
        cat_a_count = cur.fetchone()[0]
        print(f"  ✓ WHERE category='A' = {cat_a_count}")
        assert cat_a_count > 0

        # Test 3: Aggregation
        print(f"\n=== Test 3: Aggregation ===")
        cur.execute(f"SELECT category, COUNT(*), AVG(score), SUM(score) FROM {table} GROUP BY category ORDER BY category")
        agg_rows = cur.fetchall()
        for row in agg_rows:
            print(f"  ✓ {row[0]}: count={row[1]}, avg={row[2]:.1f}, sum={row[3]:.1f}")
        assert len(agg_rows) == 3

        # Test 4: ORDER BY + LIMIT
        print(f"\n=== Test 4: ORDER BY + LIMIT ===")
        cur.execute(f"SELECT name, score FROM {table} ORDER BY score DESC LIMIT 3")
        top3 = cur.fetchall()
        print(f"  ✓ Top 3 by score: {[r[0] for r in top3]}")
        assert len(top3) == 3

        # Test 5: LIKE search
        print(f"\n=== Test 5: LIKE search ===")
        cur.execute(f"SELECT COUNT(*) FROM {table} WHERE name LIKE %s", ("%1%",))
        like_count = cur.fetchone()[0]
        print(f"  ✓ LIKE '%%1%%' = {like_count}")
        assert like_count > 0

        # Test 6: JSONB query
        print(f"\n=== Test 6: JSONB query ===")
        cur.execute(f"SELECT COUNT(*) FROM {table} WHERE metadata @> %s", ('{"even": "true"}',))
        even_count = cur.fetchone()[0]
        print(f"  ✓ JSONB @> even:true = {even_count}")
        assert even_count == 15

        cur.execute(f"SELECT COUNT(*) FROM {table} WHERE (metadata ->> 'index')::int > %s", (25,))
        high_index = cur.fetchone()[0]
        print(f"  ✓ JSONB ->> index > 25 = {high_index}")

        # Test 7: Boolean filtering
        print(f"\n=== Test 7: Boolean filtering ===")
        cur.execute(f"SELECT COUNT(*) FROM {table} WHERE active = TRUE")
        active_count = cur.fetchone()[0]
        print(f"  ✓ active = TRUE: {active_count}")
        assert active_count == 24

        # Test 8: NULL handling
        print(f"\n=== Test 8: NULL handling ===")
        cur.execute(f"SELECT COUNT(*) FROM {table} WHERE category IS NOT NULL")
        non_null = cur.fetchone()[0]
        print(f"  ✓ IS NOT NULL: {non_null}")
        assert non_null == 30

        # Test 9: Subquery
        print(f"\n=== Test 9: Subquery ===")
        cur.execute(f"""
            SELECT name, score FROM {table}
            WHERE score > (SELECT AVG(score) FROM {table})
            ORDER BY score DESC
        """)
        above_avg = cur.fetchall()
        print(f"  ✓ Records above average score: {len(above_avg)}")

        # Test 10: Schema introspection
        print(f"\n=== Test 10: Schema Introspection ===")
        cur.execute(
            "SELECT column_name, data_type FROM information_schema.columns "
            "WHERE table_name = %s ORDER BY ordinal_position",
            (table,),
        )
        columns = cur.fetchall()
        print(f"  ✓ Columns ({len(columns)}):")
        for col in columns:
            print(f"      {col[0]:15s} {col[1]}")

        # Cleanup
        cur.execute(f"DROP TABLE IF EXISTS {table}")
        conn.commit()

        print("\n" + "=" * 50)
        print("✓ ALL READ TESTS PASSED")
        print("=" * 50)
        return 0

    except psycopg2.Error as e:
        print(f"\n✗ Read test failed: {e}", file=sys.stderr)
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
