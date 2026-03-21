import os
from typing import Optional


class Settings:
    """
    Configurazione centrale PROMETEO.
    Legge variabili ambiente e fornisce fallback sicuri per sviluppo locale.
    """

    def __init__(self):

        # ---- ENV -----------------------------------------------------
        self.env: str = os.getenv("ENV", "local")

        # ---- SERVICE INFO -------------------------------------------
        self.service_name: str = "prometeo-core"
        self.version: str = "0.3.1"

        # ---- SERVER --------------------------------------------------
        self.port: int = int(os.getenv("PORT", "8000"))

        # ---- DATABASE -----------------------------------------------
        self.database_url: Optional[str] = os.getenv("DATABASE_URL")

        # flag: DB configurato
        self.database_configured: bool = self.database_url is not None

        # ---- UI ------------------------------------------------------
        self.ui_available: bool = True


settings = Settings()
