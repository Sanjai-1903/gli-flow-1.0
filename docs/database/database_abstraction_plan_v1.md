# Database Abstraction Layer Plan v1

**Generated:** 2026-06-23
**Goal:** Remove SQLite assumptions from business logic; enable PostgreSQL (Supabase) without deleting SQLite support.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│                 Business Logic                   │
│  (orchestrator, CLI, backend, telemetry, etc.)   │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│            DatabaseProvider Interface            │
│  (abstract base class / protocol)               │
└──────────────────────┬──────────────────────────┘
                       │
           ┌───────────┴───────────┐
           ▼                       ▼
┌──────────────────┐   ┌──────────────────────┐
│  SQLiteProvider   │   │  PostgresProvider     │
│  (existing code)  │   │  (new implementation) │
└──────────────────┘   └──────────────────────┘
```

---

## 1. DatabaseProvider Interface

### 1.1 Design Principles

1. **Minimal surface area** — only abstract what multiple providers need
2. **Connection management** — each provider manages its own connection lifecycle
3. **Row factory** — both providers return `dict`-like rows
4. **Transaction support** — commit/rollback context manager
5. **Migration** — each provider implements its own migration strategy
6. **No ORM** — raw SQL remains, just parameterized correctly per dialect

### 1.2 Interface Definition

```python
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Protocol


class Row(Dict[str, Any]):
    """A dictionary representing a database row."""
    pass


class DatabaseProvider(ABC):
    """Abstract interface for database access."""

    @abstractmethod
    def connect(self) -> None:
        """Establish database connection."""
        ...

    @abstractmethod
    def disconnect(self) -> None:
        """Close database connection."""
        ...

    @abstractmethod
    def execute(self, sql: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a single SQL statement (no results)."""
        ...

    @abstractmethod
    def fetchone(self, sql: str, params: Optional[Dict[str, Any]] = None) -> Optional[Row]:
        """Execute SQL and return first row as dict."""
        ...

    @abstractmethod
    def fetchall(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Row]:
        """Execute SQL and return all rows as list of dicts."""
        ...

    @abstractmethod
    def fetchval(self, sql: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute SQL and return first column of first row."""
        ...

    @abstractmethod
    def commit(self) -> None:
        """Commit current transaction."""
        ...

    @abstractmethod
    def rollback(self) -> None:
        """Rollback current transaction."""
        ...

    @abstractmethod
    @contextmanager
    def transaction(self):
        """Context manager for transaction."""
        ...

    @abstractmethod
    def migrate(self) -> None:
        """Apply pending schema migrations."""
        ...

    @abstractmethod
    def validate_schema(self) -> bool:
        """Validate that all expected tables/columns exist."""
        ...

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connection is alive."""
        ...
```

---

## 2. Repository Migration Strategy

Each repository should accept a `DatabaseProvider` instead of a raw connection or path.

### 2.1 Current Pattern (example: FailureAtlasRepository)

```python
class FailureAtlasRepository:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or _get_db_path()
        migrate_if_needed(self.db_path)
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA journal_mode=WAL")
```

### 2.2 Target Pattern

```python
class FailureAtlasRepository:
    def __init__(self, provider: DatabaseProvider):
        self.db = provider
        self.db.migrate()

    def _fetchone(self, sql: str, params=None) -> Optional[Row]:
        return self.db.fetchone(sql, params)

    def _fetchall(self, sql: str, params=None) -> List[Row]:
        return self.db.fetchall(sql, params)

    def _execute(self, sql: str, params=None):
        self.db.execute(sql, params)
```

### 2.3 Repositories to Migrate

| Repository | Current Constructor Change | Current Connection Source |
|-----------|---------------------------|-------------------------|
| `DatabaseManager` (sqlite.py) | `db_path` → `provider` | `_get_db_path()` |
| `FailureAtlasRepository` | `db_path` → `provider` | `_get_db_path()` |
| `ResolutionRepository` | `conn` → `provider` | Injected connection |
| `IngestionDatabase` | `config` → `provider` | `config.database.url` |
| `UploadQueue` | `db_path` → `provider` | `~/.gli-flow/upload_queue.db` |
| `TelemetryWarehouse` | (auto) → `provider` | `_get_db_path()` |
| `TelemetryAuditLog` | `db_path` → `provider` | `_get_db_path()` |
| `EscalationTelemetry` | (auto) → `provider` | `_get_db_path()` |
| `UnknownFailureDataset` | (auto) → `provider` | `_get_db_path()` |
| `CommunityEscalation` | (auto) → `provider` | `_get_db_path()` |
| `DesignFeatureExtractor` | `db_path` → `provider` | `_get_db_path()` |
| `DesignProfileEngine` | `db_path` → `provider` | `_get_db_path()` |
| `DatasetQualityAudit` | `db_path` → `provider` | `_get_db_path()` |

---

## 3. SQLiteProvider Implementation

### 3.1 Design

```python
class SQLiteProvider(DatabaseProvider):
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or _get_db_path()

    def connect(self) -> None:
        import sqlite3
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")

    def disconnect(self) -> None:
        if self._conn:
            self._conn.close()

    def execute(self, sql: str, params=None) -> None:
        if params is None:
            params = ()
        elif isinstance(params, dict):
            # sqlite3 supports both positional and named params
            pass
        self._conn.execute(sql, params)
        self._conn.commit()

    def fetchone(self, sql: str, params=None) -> Optional[Row]:
        if params is None:
            params = ()
        cursor = self._conn.execute(sql, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    def fetchall(self, sql: str, params=None) -> List[Row]:
        if params is None:
            params = ()
        cursor = self._conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]

    def fetchval(self, sql: str, params=None) -> Any:
        if params is None:
            params = ()
        cursor = self._conn.execute(sql, params)
        row = cursor.fetchone()
        return row[0] if row else None

    def migrate(self) -> None:
        from gli_flow.database.migrations import migrate_if_needed
        migrate_if_needed(self.db_path)

    def validate_schema(self) -> bool:
        from gli_flow.database.migrations import MigrationEngine
        engine = MigrationEngine(self.db_path)
        try:
            ok, _ = engine.validate_runtime_schema()
            return ok
        finally:
            engine.close()
```

### 3.2 Key SQLite Behaviors to Preserve

- `INSERT OR REPLACE` → remains as-is
- `INSERT OR IGNORE` → remains as-is
- `PRAGMA journal_mode=WAL` → applied on connect (SQLite-only)
- `rowid` → no change needed (SQLite-only feature)
- `lastrowid` → available via `cursor.lastrowid`

---

## 4. PostgresProvider Implementation

### 4.1 Design

```python
import psycopg2
import psycopg2.extras


class PostgresProvider(DatabaseProvider):
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.environ.get("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL must be set for PostgresProvider")

    def connect(self) -> None:
        self._conn = psycopg2.connect(self.database_url)
        self._conn.autocommit = False

    def disconnect(self) -> None:
        if self._conn and not self._conn.closed:
            self._conn.close()

    def execute(self, sql: str, params=None) -> None:
        if params is None:
            params = ()
        with self._conn.cursor() as cur:
            cur.execute(sql, params)
        self._conn.commit()

    def fetchone(self, sql: str, params=None) -> Optional[Row]:
        with self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params or ())
            row = cur.fetchone()
            return dict(row) if row else None

    def fetchall(self, sql: str, params=None) -> List[Row]:
        with self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params or ())
            return [dict(row) for row in cur.fetchall()]

    def fetchval(self, sql: str, params=None) -> Any:
        with self._conn.cursor() as cur:
            cur.execute(sql, params or ())
            row = cur.fetchone()
            return row[0] if row else None

    def migrate(self) -> None:
        """Apply PostgreSQL schema using the schema from postgresql_schema_v1.md."""
        from gli_flow.database.pg_migrations import PGMigrationEngine
        engine = PGMigrationEngine(self._conn)
        engine.migrate()

    def validate_schema(self) -> bool:
        """Validate schema against information_schema."""
        with self._conn.cursor() as cur:
            for table in self.EXPECTED_TABLES:
                cur.execute(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema = 'public' AND table_name = %s",
                    (table,),
                )
                actual = {row[0] for row in cur.fetchall()}
                if not actual:
                    return False
        return True
```

### 4.2 SQL Rewrites Needed for PostgresProvider

| SQLite Pattern | PostgreSQL Replacement |
|----------------|----------------------|
| `INSERT OR REPLACE INTO t ...` | `INSERT INTO t ... ON CONFLICT (pk) DO UPDATE SET ...` |
| `INSERT OR IGNORE INTO t ...` | `INSERT INTO t ... ON CONFLICT DO NOTHING` |
| `PRAGMA journal_mode=WAL` | Remove (no-op) |
| `SELECT ... FROM sqlite_master` | `SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'` |
| `PRAGMA table_info(t)` | `SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s` |
| `WHERE rowid IN (SELECT MIN(rowid) ...)` | Rewrite using primary key or CTID |
| `cursor.lastrowid` | `INSERT ... RETURNING id` |
| `LIKE` with `%` wildcards | Same (compatible) |
| `json_extract(col, '$.path')` | `col #>> '{path}'` or `jsonb_extract_path(col, 'path')` |
| `DATE(col)` | `col::date` |
| `datetime('now')` | `NOW()` |
| `COALESCE(?, datetime('now'))` | `COALESCE(%s, NOW())` |
| `?` placeholders (positional) | `%s` placeholders (psycopg2 positional) |
| `?` placeholders (named) | `%(name)s` placeholders |

---

## 5. Provider Selection Strategy

### 5.1 Runtime Selection

```python
def create_provider() -> DatabaseProvider:
    database_url = os.environ.get("DATABASE_URL")
    if database_url and database_url.startswith("postgresql"):
        return PostgresProvider(database_url)
    return SQLiteProvider()
```

### 5.2 Environment Variable Priority

```
GLI_FLOW_DB         → forces SQLite path (overrides default)
GLI_FLOW_DB_PATH    → forces SQLite path (secondary)
DATABASE_URL        → forces PostgreSQL when present and starts with postgresql://
```

If `DATABASE_URL` is set to a PostgreSQL URL, use `PostgresProvider`.
Otherwise, fall back to `SQLiteProvider` with existing path resolution.

---

## 6. Migration Plan by Component

### Phase A: Infrastructure (no behavior change)

1. Define `DatabaseProvider` interface in `gli_flow/database/provider.py`
2. Implement `SQLiteProvider` wrapping existing `sqlite3` logic
3. Implement `PostgresProvider` wrapping `psycopg2`
4. Implement `create_provider()` factory

### Phase B: Repository Migration (replace constructor arg)

For each repository class:
1. Change constructor to accept `DatabaseProvider` instead of `db_path`/`conn`
2. Make PRAGMA calls conditional (only for SQLite)
3. Replace SQLite-specific SQL patterns with provider-agnostic versions
4. Add tests with both providers

### Phase C: Business Logic Migration

For each consumer of repositories:
1. Pass `provider` instead of `db_path`
2. Verify queries work with both backends
3. Enable PostgreSQL in staging
4. Run parallel validation

---

## 7. File Structure

```
gli_flow/database/
├── __init__.py
├── provider.py          # DatabaseProvider interface
├── sqlite_provider.py   # SQLiteProvider implementation
├── pg_provider.py       # PostgresProvider implementation
├── factory.py           # create_provider() factory
├── pg_migrations.py     # PostgreSQL migration engine
├── migrations.py        # Existing SQLite migrations (unchanged)
├── sqlite.py            # Existing DatabaseManager (deprecated → wrapper)
└── manager.py           # Existing legacy manager (unchanged)
```

---

## 8. Testing Strategy

```python
def test_repository_with_both_providers():
    # SQLite
    sqlite_provider = SQLiteProvider(":memory:")
    sqlite_provider.connect()
    repo = FailureAtlasRepository(sqlite_provider)
    # ... run tests ...

    # PostgreSQL (requires TEST_DATABASE_URL)
    pg_provider = PostgresProvider(os.environ["TEST_DATABASE_URL"])
    pg_provider.connect()
    repo = FailureAtlasRepository(pg_provider)
    # ... run same tests ...
```

---

## 9. Non-Goals

- No ORM introduction
- No SQL query builder
- No async migration (can add later)
- No removal of SQLite support
- No automatic migration of existing data (handled in Phase 5)
- No changes to cloud_ingestion database (will be migrated separately)
