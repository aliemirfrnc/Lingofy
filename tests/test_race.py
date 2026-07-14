import asyncio
from backend.core.services.subscription_service import SubscriptionService
from backend.core.db import get_conn
from datetime import datetime

async def main():
    service = SubscriptionService()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Insert mock user, plan and subscription
    with get_conn() as conn:
        conn.execute("INSERT OR IGNORE INTO users (id, email, password_hash, created_at) VALUES (1, 'race@test.com', 'hash', 0)")
        conn.execute("INSERT OR IGNORE INTO subscriptions (user_id, plan_id, started_at, expires_at, created_at, updated_at) VALUES (1, 1, 0, 0, 0, 0)")
        # Make sure usage_limits exists
        conn.execute("INSERT OR IGNORE INTO usage_limits (user_id, date_str, created_at) VALUES (1, ?, 0)", (today,))
        # Reset limit for word_analysis_used
        conn.execute("UPDATE usage_limits SET word_analysis_used = 0 WHERE user_id = 1 AND date_str = ?", (today,))
        conn.commit()
    
    print("Starting 100 concurrent requests...")
    
    async def make_request():
        # Using feature 'words' since the limit key is words_limit in DB
        # The repo uses specific columns for features.
        # Let's use ai_messages because it maps to ai_messages_limit
        # Wait, the repo.increment_usage implementation might be specific.
        # I'll just call consume_feature_atomic(1, "words", 1).
        # In free plan, words_limit is 20.
        try:
            # Let's just use "words" as feature
            res, msg = service.consume_feature_atomic(user_id=1, feature="words")
            return res
        except Exception as e:
            return str(e)
            
    tasks = [make_request() for _ in range(100)]
    results = await asyncio.gather(*tasks)
    
    success = [r for r in results if r is True]
    failed = [r for r in results if isinstance(r, str) or r is False]
    
    with get_conn() as conn:
        usage = conn.execute("SELECT SUM(words_limit) FROM plans WHERE id=1").fetchone()[0] # The limit
        # Let's check what repo increment actually uses, I can't guess easily, let's just query usage_limits
        row = conn.execute("SELECT * FROM usage_limits WHERE user_id = 1 AND date_str = ?", (today,)).fetchone()
        
    print(f"Successful consumptions: {len(success)}")
    print(f"Failed/Rejected consumptions: {len(failed)}")
    if row:
        print(f"Current usage row: {row}")

if __name__ == "__main__":
    asyncio.run(main())
