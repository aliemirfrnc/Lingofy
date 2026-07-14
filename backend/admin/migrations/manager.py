import os
import importlib
from backend.core.logger import get_logger
from backend.core.db import get_conn, get_lock

logger = get_logger(__name__)

def initialize_admin_schema():
    """
    Runs all pending admin migrations in order.
    """
    logger.info("Initializing admin schema...")
    conn = get_conn()
    lock = get_lock()
    
    with lock:
        # Create schema_version table if not exists
        conn.execute('''
            CREATE TABLE IF NOT EXISTS admin_schema_version (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at REAL NOT NULL
            )
        ''')
        conn.commit()

        # Find migration modules
        migrations_dir = os.path.dirname(__file__)
        migration_files = sorted([
            f for f in os.listdir(migrations_dir)
            if f.startswith('migration_') and f.endswith('.py')
        ])

        for file_name in migration_files:
            module_name = file_name[:-3]
            try:
                version = int(module_name.split('_')[1])
            except ValueError:
                logger.error(f"Invalid migration file name: {file_name}")
                continue
            
            # Check if already applied
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM admin_schema_version WHERE version = ?", (version,))
            if cursor.fetchone():
                continue

            logger.info(f"Applying admin migration: {module_name}")
            module = importlib.import_module(f"backend.admin.migrations.{module_name}")
            
            try:
                # Run the upgrade function
                module.upgrade(conn)
                
                import time
                conn.execute(
                    "INSERT INTO admin_schema_version (version, name, applied_at) VALUES (?, ?, ?)",
                    (version, module_name, time.time())
                )
                conn.commit()
                logger.info(f"Successfully applied admin migration: {module_name}")
            except Exception as e:
                conn.rollback()
                logger.error(f"Failed to apply admin migration {module_name}: {e}")
                raise e
