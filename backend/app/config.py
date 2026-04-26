from __future__ import annotations

import os
from pathlib import Path


class Settings:
    def __init__(self) -> None:
        self.service_name: str = "prometeo-core"
        self.version: str = "0.4.0"

        base_dir = Path(__file__).resolve().parent.parent
        default_sqlite_dir = Path(
            os.getenv("PROMETEO_DATA_DIR", str(base_dir / "app" / "data"))
        )
        self.sqlite_dir: Path = default_sqlite_dir
        self.sqlite_path: Path = self.sqlite_dir / "prometeo.sqlite3"

        self.database_url: str = os.getenv("DATABASE_URL", "").strip()
        self.prometeo_api_key: str = os.getenv("PROMETEO_API_KEY", "").strip()

        raw_backend = os.getenv("PROMETEO_DB_BACKEND", "").strip().lower()

        if raw_backend in {"sqlite", "postgres"}:
            self.db_backend = raw_backend
        elif self.database_url:
            self.db_backend = "postgres"
        else:
            self.db_backend = "sqlite"

    @property
    def ui_available(self) -> bool:
        return True

    @property
    def database_configured(self) -> bool:
        if self.db_backend == "postgres":
            return bool(self.database_url)
        return True

    @property
    def postgres_configured(self) -> bool:
        return bool(self.database_url)


settings = Settings()
