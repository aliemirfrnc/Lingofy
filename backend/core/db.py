import sqlite3
import threading
from pathlib import Path

_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "lingofy.db"
_LOCK = threading.Lock()


def _connect() -> sqlite3.Connection:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


_conn = _connect()

def auto_migrate_table(conn: sqlite3.Connection, table_name: str, desired_columns: dict):
    """
    Checks the existing table's schema. If columns from desired_columns are missing,
    it runs ALTER TABLE ADD COLUMN.
    desired_columns format: {"column_name": "TYPE DEFAULT X"}
    """
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_cols = {row[1]: row[2] for row in cursor.fetchall()}
    
    for col_name, col_def in desired_columns.items():
        if col_name not in existing_cols:
            print(f"Migration: Adding column {col_name} to {table_name}...")
            try:
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_def}")
            except Exception as e:
                print(f"Error migrating {col_name} on {table_name}: {e}")

def init_db() -> None:
    with _LOCK:
        _conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS refresh_tokens (
                token_hash TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at REAL NOT NULL,
                expires_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS spotify_accounts (
                user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                access_token TEXT NOT NULL,
                refresh_token TEXT NOT NULL,
                expires_at REAL NOT NULL,
                updated_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS oauth_states (
                state TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS spotify_connect_tokens (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS pronunciation_profiles (
                user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                avg_score REAL DEFAULT 0,
                updated_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS pronunciation_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS pronunciation_coach_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                message TEXT NOT NULL,
                created_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS pronunciation_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                goal_text TEXT NOT NULL,
                xp_reward INTEGER DEFAULT 50,
                completed BOOLEAN DEFAULT 0,
                created_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS pronunciation_badges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                badge_name TEXT NOT NULL,
                unlocked_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS pronunciation_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                word TEXT NOT NULL,
                correct_count INTEGER DEFAULT 0,
                wrong_count INTEGER DEFAULT 0,
                UNIQUE(user_id, word)
            );

            -- MEMBERSHIP SYSTEM --
            
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                price REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                songs_limit INTEGER DEFAULT 5,
                words_limit INTEGER DEFAULT 20,
                ai_messages_limit INTEGER DEFAULT 10,
                shadowing_limit INTEGER DEFAULT 5,
                pronunciation_limit INTEGER DEFAULT 5,
                has_pdf_report BOOLEAN DEFAULT 0,
                has_ai_mentor BOOLEAN DEFAULT 0,
                has_speaking_sim BOOLEAN DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                plan_id INTEGER NOT NULL REFERENCES plans(id),
                status TEXT DEFAULT 'ACTIVE',
                provider TEXT,
                provider_subscription_id TEXT,
                provider_customer_id TEXT,
                started_at REAL NOT NULL,
                expires_at REAL NOT NULL,
                cancel_at_period_end BOOLEAN DEFAULT 0,
                trial_ends_at REAL,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS usage_limits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                date_str TEXT NOT NULL,
                songs_used INTEGER DEFAULT 0,
                word_analysis_used INTEGER DEFAULT 0,
                pronunciation_used INTEGER DEFAULT 0,
                shadowing_minutes INTEGER DEFAULT 0,
                ai_messages INTEGER DEFAULT 0,
                created_at REAL NOT NULL,
                UNIQUE(user_id, date_str)
            );

            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                provider TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                status TEXT NOT NULL,
                invoice_id TEXT,
                transaction_id TEXT,
                created_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS login_attempts (
                ip_address TEXT,
                email TEXT,
                attempts INTEGER DEFAULT 1,
                last_attempt REAL NOT NULL,
                locked_until REAL,
                UNIQUE(ip_address, email)
            );

            CREATE TABLE IF NOT EXISTS rate_limits (
                ip_address TEXT PRIMARY KEY,
                request_count INTEGER DEFAULT 1,
                reset_at REAL NOT NULL
            );

            -- Default Plans Insertion --
            INSERT OR IGNORE INTO plans (name, price, songs_limit, words_limit, ai_messages_limit, shadowing_limit, pronunciation_limit) 
            VALUES ('FREE', 0, 5, 20, 10, 5, 5);
            
            INSERT OR IGNORE INTO plans (name, price, songs_limit, words_limit, ai_messages_limit, shadowing_limit, pronunciation_limit, has_pdf_report) 
            VALUES ('PRO', 9.99, 999999, 999999, 999999, 999999, 999999, 0);

            INSERT OR IGNORE INTO plans (name, price, songs_limit, words_limit, ai_messages_limit, shadowing_limit, pronunciation_limit, has_pdf_report, has_ai_mentor, has_speaking_sim) 
            VALUES ('MASTER', 19.99, 999999, 999999, 999999, 999999, 999999, 1, 1, 1);
            """
        )
        
        # Idempotent Migrations to ensure columns exist without dropping tables.
        auto_migrate_table(_conn, "users", {
            "role": "TEXT DEFAULT 'USER'"
        })

        auto_migrate_table(_conn, "pronunciation_profiles", {
            "avg_accuracy": "REAL DEFAULT 0",
            "avg_fluency": "REAL DEFAULT 0",
            "avg_rhythm": "REAL DEFAULT 0",
            "avg_stress": "REAL DEFAULT 0",
            "avg_intonation": "REAL DEFAULT 0",
            "avg_confidence": "REAL DEFAULT 0",
            "cefr_level": "TEXT DEFAULT 'A1'",
            "current_level": "TEXT DEFAULT '🔰 Beginner'",
            "total_time_minutes": "REAL DEFAULT 0",
            "total_recordings": "INTEGER DEFAULT 0",
            "total_shadowing_sessions": "INTEGER DEFAULT 0",
            "total_completed_songs": "INTEGER DEFAULT 0",
            "total_xp": "INTEGER DEFAULT 0",
            "daily_streak": "INTEGER DEFAULT 0",
            "longest_streak": "INTEGER DEFAULT 0",
            "best_score": "REAL DEFAULT 0",
            "favorite_artist": "TEXT DEFAULT ''",
            "favorite_song": "TEXT DEFAULT ''",
            "phoneme_statistics": "TEXT DEFAULT '{}'",
            "learning_history": "TEXT DEFAULT '[]'"
        })

        auto_migrate_table(_conn, "pronunciation_sessions", {
            "track_id": "TEXT",
            "lyrics_line": "TEXT",
            "audio_path": "TEXT",
            "transcript": "TEXT",
            "phoneme_result": "TEXT",
            "accuracy": "REAL",
            "fluency": "REAL",
            "rhythm": "REAL",
            "stress": "REAL",
            "intonation": "REAL",
            "confidence": "REAL",
            "overall_score": "REAL"
        })

        _conn.commit()


def get_conn() -> sqlite3.Connection:
    return _conn


def get_lock() -> threading.Lock:
    return _LOCK
