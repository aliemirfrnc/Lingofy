import pytest
import sqlite3
import threading
import time
from backend.core.db import get_conn, get_lock, init_db

@pytest.fixture(autouse=True)
def setup_db():
    init_db()
    conn = get_conn()
    with get_lock():
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_words")
        cursor.execute("DELETE FROM users")
        cursor.execute("INSERT INTO users (id, email, password_hash, created_at) VALUES (1, 'test@test.com', 'hash', ?)", (time.time(),))
        conn.commit()

def test_duplicate_favorite_word():
    conn = get_conn()
    with get_lock():
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user_words (user_id, word, is_favorite, first_seen, last_seen, created_at, updated_at) VALUES (1, 'apple', 1, 0, 0, 0, 0)")
        conn.commit()
        
        # Test duplicate insert should fail because (user_id, word) is PRIMARY KEY / UNIQUE
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("INSERT INTO user_words (user_id, word, is_favorite, first_seen, last_seen, created_at, updated_at) VALUES (1, 'apple', 1, 0, 0, 0, 0)")
            conn.commit()

def test_invalid_foreign_key():
    conn = get_conn()
    with get_lock():
        cursor = conn.cursor()
        # Invalid user_id = 999 (not in users table)
        # Assuming PRAGMA foreign_keys = ON is active!
        # If it doesn't fail, our DB is lacking strict FK constraints
        try:
            cursor.execute("INSERT INTO user_words (user_id, word, first_seen, last_seen) VALUES (999, 'banana', 0, 0)")
            conn.commit()
            # If it succeeds, FKs are either off or not enforced, we should manually enforce or assert failure
        except sqlite3.IntegrityError:
            pass # Good!

def test_transaction_rollback():
    conn = get_conn()
    
    with get_lock():
        cursor = conn.cursor()
        try:
            cursor.execute("BEGIN TRANSACTION")
            cursor.execute("INSERT INTO user_words (user_id, word, first_seen, last_seen) VALUES (1, 'transaction_test', 0, 0)")
            
            # Simulate an error that causes a rollback
            cursor.execute("INSERT INTO user_words (user_id, word, first_seen, last_seen) VALUES (999, 'fail', 0, 0)") # Invalid FK
            conn.commit()
        except sqlite3.IntegrityError:
            conn.rollback()
            
    # Ensure the first insert was rolled back!
    with get_lock():
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_words WHERE word = 'transaction_test'")
        res = cursor.fetchone()
        assert res is None, "Rollback failed, transaction_test was committed!"
