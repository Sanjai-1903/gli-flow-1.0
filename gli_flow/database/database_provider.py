from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Generator


class Row(Dict[str, Any]):
    pass


class DatabaseProvider(ABC):
    @abstractmethod
    def connect(self) -> None:
        ...

    @abstractmethod
    def disconnect(self) -> None:
        ...

    @abstractmethod
    def execute(self, sql: str, params: Optional[Dict[str, Any]] = None) -> None:
        ...

    @abstractmethod
    def fetchone(self, sql: str, params: Optional[Dict[str, Any]] = None) -> Optional[Row]:
        ...

    @abstractmethod
    def fetchall(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Row]:
        ...

    @abstractmethod
    def fetchval(self, sql: str, params: Optional[Dict[str, Any]] = None) -> Any:
        ...

    @abstractmethod
    def commit(self) -> None:
        ...

    @abstractmethod
    def rollback(self) -> None:
        ...

    @contextmanager
    def transaction(self) -> Generator[None, None, None]:
        try:
            yield
            self.commit()
        except Exception:
            self.rollback()
            raise

    @abstractmethod
    def migrate(self) -> None:
        ...

    @abstractmethod
    def validate_schema(self) -> bool:
        ...

    @abstractmethod
    def close(self) -> None:
        ...

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        ...

    @property
    def rowcount(self) -> int:
        """Number of rows affected by last execute. -1 if unknown."""
        return -1
