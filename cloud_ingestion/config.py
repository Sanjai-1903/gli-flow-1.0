import os
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 8100
    workers: int = 2
    log_level: str = "INFO"
    max_request_size_mb: int = 10


@dataclass
class DatabaseConfig:
    url: str = "sqlite:///tmp/cloud_ingestion_dev.db"
    pool_size: int = 5
    max_overflow: int = 10

    @property
    def is_postgres(self) -> bool:
        return self.url.startswith("postgresql")


@dataclass
class AuthConfig:
    api_key: str = ""
    enabled: bool = True


@dataclass
class RateLimitConfig:
    max_requests_per_minute: int = 120


@dataclass
class CorsConfig:
    allowed_origins: list[str] = field(default_factory=lambda: ["*"])


@dataclass
class CloudIngestionConfig:
    server: ServerConfig = field(default_factory=ServerConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)
    rate_limiting: RateLimitConfig = field(default_factory=RateLimitConfig)
    cors: CorsConfig = field(default_factory=CorsConfig)

    @classmethod
    def load(cls, path: Optional[str] = None) -> "CloudIngestionConfig":
        if path is None:
            path = str(Path(__file__).parent.parent / "config" / "cloud_ingestion.yaml")

        cfg = cls()
        if os.path.exists(path):
            with open(path) as f:
                raw = yaml.safe_load(f) or {}

            if "server" in raw:
                cfg.server = ServerConfig(**raw["server"])
            if "database" in raw:
                cfg.database = DatabaseConfig(**raw["database"])
            if "auth" in raw:
                cfg.auth = AuthConfig(**raw["auth"])
            if "rate_limiting" in raw:
                cfg.rate_limiting = RateLimitConfig(**raw["rate_limiting"])
            if "cors" in raw:
                cfg.cors = CorsConfig(**raw["cors"])

        env_api_key = os.environ.get("GLI_API_KEY")
        if env_api_key:
            cfg.auth.api_key = env_api_key

        env_db_url = os.environ.get("GLI_DATABASE_URL")
        if env_db_url:
            cfg.database.url = env_db_url

        env_server_url = os.environ.get("GLI_SERVER_URL")
        if env_server_url:
            import urllib.parse
            parsed = urllib.parse.urlparse(env_server_url)
            cfg.server.host = parsed.hostname or cfg.server.host
            cfg.server.port = parsed.port or cfg.server.port

        return cfg
