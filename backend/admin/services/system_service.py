import os
import psutil
import sqlite3
from typing import Dict, Any
from backend.core.db import get_conn

class SystemService:
    def get_health_metrics(self) -> Dict[str, Any]:
        """
        Returns OS level health metrics and database status.
        """
        cpu_percent = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        db_size = 0
        try:
            conn = get_conn()
            # SQLite specific DB size check
            cursor = conn.cursor()
            cursor.execute("PRAGMA page_count;")
            page_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_size;")
            page_size = cursor.fetchone()[0]
            db_size = page_count * page_size
        except Exception:
            pass

        return {
            "cpu_usage_percent": cpu_percent,
            "ram_usage_percent": ram.percent,
            "ram_total_mb": ram.total // (1024 * 1024),
            "disk_usage_percent": disk.percent,
            "database_size_bytes": db_size,
            "status": "HEALTHY" if cpu_percent < 90 and ram.percent < 90 else "DEGRADED"
        }

    def get_database_tables(self) -> list:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = cursor.fetchall()
        
        stats = []
        for (table_name,) in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            stats.append({"name": table_name, "row_count": row_count})
        return stats
