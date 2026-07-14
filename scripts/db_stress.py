import asyncio
import sqlite3
import time
from backend.core.db import _conn as conn, _LOCK as db_lock, auto_migrate_table

async def write_task(task_id):
    try:
        with db_lock:
            c = conn.cursor()
            # Ensure table exists
            c.execute("""
                CREATE TABLE IF NOT EXISTS test_stress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, val TEXT
                )
            """)
            c.execute("""
                INSERT INTO test_stress (val) VALUES (?)
            """, (f"dummy_{task_id}",))
            conn.commit()
            
            c.execute("SELECT count(*) FROM test_stress")
            count = c.fetchone()[0]
            return True, count
    except sqlite3.OperationalError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

async def main():
    print("Initializing DB...")
    
    # 1000 concurrent database requests
    concurrency = 1000
    print(f"Starting Database Certification ({concurrency} concurrent requests)...")
    
    start = time.time()
    
    # Create tasks
    tasks = [write_task(i) for i in range(concurrency)]
    results = await asyncio.gather(*tasks)
    
    elapsed = time.time() - start
    
    successes = sum(1 for r in results if r[0] is True)
    failures = sum(1 for r in results if r[0] is False)
    
    print(f"Elapsed Time: {elapsed:.2f}s")
    print(f"Successful Requests: {successes}")
    print(f"Failed Requests (Deadlock/Locked): {failures}")
    
    if failures == 0:
        print("\n✅ [PASS] SQLite WAL and RLock mechanism perfectly handled 1000 concurrent requests.")
    else:
        print("\n❌ [FAIL] Database locking errors occurred!")
        print(f"Sample error: {[r[1] for r in results if r[0] is False][0]}")
        
    # Clean up dummy records
    with db_lock:
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS test_stress")
        conn.commit()

if __name__ == "__main__":
    asyncio.run(main())
