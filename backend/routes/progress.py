from fastapi import APIRouter, Depends
from backend.core.db import get_conn
import json
from datetime import datetime, timedelta
from backend.routes.auth import require_user_id

router = APIRouter(prefix="/api/progress", tags=["progress"])

@router.get("/stats")
async def get_progress_stats(user_id: int = Depends(require_user_id)):
    try:
        conn = get_conn()
        from backend.core.db import get_lock
        with get_lock():
            c = conn.cursor()
            
            # 1. Profile Data
            c.execute("""
                SELECT avg_score, current_level, total_xp, total_time_minutes, 
                       total_completed_songs, daily_streak, cefr_level
                FROM pronunciation_profiles WHERE user_id = ?
            """, (user_id,))
            prof = c.fetchone()
            if not prof:
                prof = (0, "🔰 Beginner", 0, 0, 0, 0, "A1")
                
            avg_score, level, total_xp, total_time, completed_songs, streak, cefr = prof
            
            # 2. History (last 30 sessions)
            c.execute("""
                SELECT overall_score, created_at FROM pronunciation_sessions 
                WHERE user_id = ? ORDER BY created_at ASC LIMIT 30
            """, (user_id,))
            history_rows = c.fetchall()
            history = [{"date": datetime.fromtimestamp(r[1]).strftime("%d %b"), "score": r[0]} for r in history_rows]
            
            # 3. Badges
            c.execute("SELECT badge_name FROM pronunciation_badges WHERE user_id = ?", (user_id,))
            unlocked_badges = [r[0] for r in c.fetchall()]
            all_badges = [
                {"id": 1, "icon": "🥉", "name": "İlk Kayıt", "unlocked": "İlk Kayıt" in unlocked_badges},
                {"id": 2, "icon": "🔥", "name": "7 Gün Serisi", "unlocked": streak >= 7},
                {"id": 3, "icon": "🥈", "name": "90+ Skor", "unlocked": "90+ Skor" in unlocked_badges},
                {"id": 4, "icon": "🥇", "name": "100 Kayıt", "unlocked": "100 Kayıt" in unlocked_badges},
                {"id": 5, "icon": "🎤", "name": "10 Şarkı", "unlocked": completed_songs >= 10},
                {"id": 6, "icon": "⭐", "name": "Native Level", "unlocked": level == "🏆 Native Like"}
            ]
            
            # 4. Word Stats (Worst 20)
            c.execute("""
                SELECT word, correct_count, wrong_count, 
                       CAST(wrong_count AS FLOAT) / (correct_count + wrong_count) as error_rate
                FROM pronunciation_words 
                WHERE user_id = ? AND (correct_count + wrong_count) > 0
                ORDER BY error_rate DESC, wrong_count DESC LIMIT 20
            """, (user_id,))
            worst_words = [{"word": r[0], "correct": r[1], "wrong": r[2], "error_rate": int(r[3]*100)} for r in c.fetchall()]
            
            # 5. AI Memory / Goal
            c.execute("SELECT goal_text FROM pronunciation_goals WHERE user_id = ? AND completed = 0 ORDER BY created_at DESC LIMIT 1", (user_id,))
            goal_row = c.fetchone()
            daily_goal = goal_row[0] if goal_row else "Pratik yapmaya başla!"
            
            # 6. Phoneme Stats (Start vs Current)
            c.execute("SELECT phoneme_result FROM pronunciation_sessions WHERE user_id = ? ORDER BY created_at ASC LIMIT 5", (user_id,))
            first_5 = c.fetchall()
            c.execute("SELECT phoneme_result FROM pronunciation_sessions WHERE user_id = ? ORDER BY created_at DESC LIMIT 5", (user_id,))
            last_5 = c.fetchall()
            
        def avg_phonemes(rows):
            totals = {}
            counts = {}
            for r in rows:
                if not r[0]: continue
                ph = json.loads(r[0])
                for k, v in ph.items():
                    totals[k] = totals.get(k, 0) + v
                    counts[k] = counts.get(k, 0) + 1
            return {k: totals[k]//counts[k] for k in totals}
            
        start_ph = avg_phonemes(first_5) if first_5 else {"TH": 50, "R": 60, "V": 55, "W": 55, "S": 60, "Z": 50}
        current_ph = avg_phonemes(last_5) if last_5 else start_ph
        
        phoneme_progress = []
        for k in start_ph.keys():
            phoneme_progress.append({
                "sound": k,
                "start": start_ph.get(k, 0),
                "current": current_ph.get(k, start_ph.get(k, 0)),
                "improvement": current_ph.get(k, 0) - start_ph.get(k, 0)
            })
            
        motivation = "Veritabanı oluşturuldu. Kayıt almaya başla ve gelişimi izle!"
        if len(history_rows) > 0:
            motivation = f"Toplam {total_xp} XP kazandın. Harika gidiyorsun!"
            
        return {
            "daily_score": int(avg_score),
            "total_time_minutes": total_time,
            "completed_songs": completed_songs,
            "current_level": level,
            "cefr_level": cefr,
            "total_xp": total_xp,
            "history": history,
            "badges": all_badges,
            "worst_words": worst_words,
            "daily_goal": daily_goal,
            "phoneme_progress": phoneme_progress,
            "motivation": motivation
        }
    except Exception as e:
        import logging
        logging.error(f"PROGRESS API ERROR: {repr(e)}")
        return {
            "daily_score": 0,
            "total_time_minutes": 0,
            "completed_songs": 0,
            "current_level": "🔰 Beginner",
            "cefr_level": "A1",
            "total_xp": 0,
            "history": [],
            "badges": [],
            "worst_words": [],
            "daily_goal": "Pratik yapmaya başla!",
            "phoneme_progress": [],
            "motivation": "İstatistikler şu anda yüklenemiyor, daha sonra tekrar dene."
        }
