import sqlite3
import time
from typing import List, Dict, Any, Optional
from .interfaces import IConfigurationRepository

class ConfigurationRepository(IConfigurationRepository):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get_runtime_configuration(self) -> Dict[str, str]:
        self.conn.row_factory = sqlite3.Row
        rows = self.conn.execute("SELECT key, value_json FROM runtime_configuration").fetchall()
        return {row["key"]: row["value_json"] for row in rows}

    def get_config_value(self, key: str) -> Optional[str]:
        self.conn.row_factory = sqlite3.Row
        row = self.conn.execute("SELECT value_json FROM runtime_configuration WHERE key = ?", (key,)).fetchone()
        return row["value_json"] if row else None

    def set_config_value(self, key: str, value_json: str, admin_id: Optional[int] = None) -> None:
        self.conn.execute(
            """
            INSERT INTO runtime_configuration (key, value_json, updated_at, updated_by)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json, updated_at=excluded.updated_at, updated_by=excluded.updated_by
            """,
            (key, value_json, time.time(), admin_id)
        )
