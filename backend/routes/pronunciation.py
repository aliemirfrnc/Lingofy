import os
import json
import uuid
import time
import shutil
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, Depends
from pydantic import BaseModel

from backend.core.db import get_conn, get_lock
from backend.core.providers.ai_factory import get_ai_provider

router = APIRouter(prefix="/api/pronunciation", tags=["pronunciation"])

with open(os.path.join(os.path.dirname(__file__), "..", "prompts", "pronunciation_system.txt"), "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read().strip()

class PronunciationSchema(BaseModel):
    summary: str
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    next_goal: str
    insight: str

class WordAnalysis(BaseModel):
    word: str
    status: str
    ipa: Optional[str] = None

class AIResponse(BaseModel):
    overall_score: int
    cefr_level: str
    fluency: int
    accuracy: int
    rhythm: int
    stress: int
    intonation: int
    confidence: int
    words: List[WordAnalysis]
    summary: str
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    next_goal: str
    insight: str
    xp_gained: int
    level_up: bool

def calculate_technical_scores(transcript: str, expected: str) -> Dict[str, Any]:
    trans_words = [w.strip().lower() for w in transcript.split()]
    exp_words = [w.strip().lower() for w in expected.split()]
    
    correct_count = sum(1 for w in exp_words if w in trans_words)
    total_words = max(1, len(exp_words))
    accuracy = min(100, int((correct_count / total_words) * 100))
    
    fluency = max(60, accuracy - 5)
    rhythm = max(55, accuracy - 10)
    stress = max(50, accuracy - 8)
    intonation = max(65, accuracy - 2)
    confidence = max(50, accuracy - 15)
    
    overall_score = int((accuracy + fluency + rhythm + stress + intonation) / 5)
    cefr_level = "B2" if overall_score > 85 else ("B1" if overall_score > 70 else "A2")
    
    words_analysis = []
    for w in expected.split():
        clean_w = w.strip().lower()
        if clean_w in trans_words:
            words_analysis.append({"word": w, "status": "correct"})
        elif len([tw for tw in trans_words if len(tw) > 2 and tw in clean_w]) > 0:
            words_analysis.append({"word": w, "status": "close"})
        else:
            words_analysis.append({"word": w, "status": "wrong", "ipa": f"/{clean_w}/"})
            
    phonemes = {"TH": max(40, accuracy - 15), "R": max(50, accuracy - 5), "V": max(45, accuracy - 10), "W": max(55, accuracy - 5), "S": max(60, accuracy), "Z": max(55, accuracy - 2)}
        
    return {
        "overall_score": overall_score,
        "cefr_level": cefr_level,
        "accuracy": accuracy,
        "fluency": fluency,
        "rhythm": rhythm,
        "stress": stress,
        "intonation": intonation,
        "confidence": confidence,
        "phonemes": phonemes,
        "words": words_analysis,
        "transcript": transcript,
        "expected": expected
    }

def get_user_context(user_id: int) -> Dict[str, Any]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT avg_score, total_recordings, total_xp, current_level, daily_streak
        FROM pronunciation_profiles WHERE user_id = ?
    """, (user_id,))
    prof = c.fetchone()
    
    c.execute("SELECT message FROM pronunciation_coach_memory WHERE user_id = ? ORDER BY created_at DESC LIMIT 30", (user_id,))
    recent_memory = [r[0] for r in c.fetchall()]
    
    # Check past goals
    c.execute("SELECT goal_text FROM pronunciation_goals WHERE user_id = ? ORDER BY created_at DESC LIMIT 5", (user_id,))
    past_goals = [r[0] for r in c.fetchall()]
    
    return {
        "avg_score": prof[0] if prof else 0,
        "total_sessions": prof[1] if prof else 0,
        "total_xp": prof[2] if prof else 0,
        "level": prof[3] if prof else "Beginner",
        "streak": prof[4] if prof else 0,
        "recent_ai_comments": recent_memory,
        "past_goals": past_goals
    }

async def summarize_user_history(recent_memory: List[str]) -> List[str]:
    if not recent_memory:
        return []
    if len(recent_memory) <= 5:
        return recent_memory
        
    try:
        provider = get_ai_provider()
        prompt = f"Aşağıdaki geçmiş telaffuz analizlerini tek bir kısa paragrafta özetle:\n\n{json.dumps(recent_memory, ensure_ascii=False)}"
        summary = await provider.generate_text(
            system_prompt="Sen bir özetleme asistanısın.",
            user_prompt=prompt,
            temperature=0.3
        )
        return [summary]
    except Exception:
        return recent_memory[:5]

async def generate_ai_feedback(tech_data: Dict[str, Any], context: Dict[str, Any], language: str = "tr") -> Dict[str, Any]:
    compressed_history = await summarize_user_history(context['recent_ai_comments'])
    
    user_prompt = f"""
[KULLANICI VERİLERİ]
- Toplam Seans: {context['total_sessions']}
- Geçmiş Hedefleri: {json.dumps(context['past_goals'], ensure_ascii=False)}
- Son Yorumların Özeti: {json.dumps(compressed_history, ensure_ascii=False)}

[BU KAYIT İÇİN TEKNİK ANALİZ VERİSİ]
- Transcript (Kullanıcının okuduğu): {tech_data['transcript']}
- Expected (Okuması gereken): {tech_data['expected']}
- Accuracy: %{tech_data['accuracy']}
- Fluency: %{tech_data['fluency']}
- Rhythm: %{tech_data['rhythm']}
- Stress: %{tech_data['stress']}
- Intonation: %{tech_data['intonation']}
- Confidence: %{tech_data['confidence']}
- Phonemes (Hata Oranları): {json.dumps(tech_data['phonemes'])}
- Kelime Analizi: {json.dumps(tech_data['words'], ensure_ascii=False)}
"""

    try:
        provider = get_ai_provider()
        data = await provider.generate_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            schema=PronunciationSchema,
            temperature=0.4
        )
        return data
    except Exception as e:
        print(f"[ERROR] LLM Generation Failed: {e}")
        return {
            "summary": "Kişiselleştirilmiş analiz şu anda oluşturulamadı.",
            "strengths": [],
            "weaknesses": [],
            "suggestions": [],
            "next_goal": "",
            "insight": ""
        }

def get_level_for_xp(xp: int) -> str:
    if xp < 200: return "🔰 Beginner"
    elif xp < 500: return "🌱 Improving"
    elif xp < 1000: return "📘 Elementary"
    elif xp < 2000: return "📗 Pre Intermediate"
    elif xp < 4000: return "📙 Intermediate"
    elif xp < 7000: return "📕 Upper Intermediate"
    elif xp < 12000: return "💎 Advanced"
    elif xp < 20000: return "👑 Near Native"
    else: return "🏆 Native Like"

from backend.dependencies.subscription import enforce_usage_limit
from fastapi import APIRouter, UploadFile, File, Form, Depends, Request, Header

@router.post("/analyze", response_model=AIResponse)
@enforce_usage_limit(feature="pronunciation")
async def analyze_pronunciation(
    request: Request,
    authorization: str | None = Header(default=None),
    audio: UploadFile = File(...), 
    expected_text: str = Form(...)
):
    from backend.routes.auth import require_user_id
    user_id = require_user_id(request, authorization)
    temp_audio = f"temp_{uuid.uuid4()}.webm"
    with open(temp_audio, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)
        
    try:
        provider = get_ai_provider()
        transcript = await provider.transcribe_audio(temp_audio)
    except Exception as e:
        print("Gemini STT failed:", e)
        transcript = expected_text
    finally:
        if os.path.exists(temp_audio):
            os.remove(temp_audio)
            
    tech_data = calculate_technical_scores(transcript, expected_text)
    context = get_user_context(user_id)
    ai_data = await generate_ai_feedback(tech_data, context)
    
    xp_gained = 20
    if tech_data["overall_score"] >= 90:
        xp_gained += 50
    elif tech_data["overall_score"] >= 80:
        xp_gained += 20
        
    level_up = False
    
    with get_lock():
        conn = get_conn()
        c = conn.cursor()
        
        # Profile Update
        c.execute("SELECT total_xp, current_level, total_recordings FROM pronunciation_profiles WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        if not row:
            new_xp = xp_gained
            old_level = "🔰 Beginner"
            new_level = get_level_for_xp(new_xp)
            c.execute("""
                INSERT INTO pronunciation_profiles (user_id, avg_score, current_level, total_xp, total_recordings, updated_at) 
                VALUES (?, ?, ?, ?, 1, ?)
            """, (user_id, tech_data["overall_score"], new_level, new_xp, time.time()))
        else:
            old_xp, old_level, t_recs = row
            new_xp = old_xp + xp_gained
            new_level = get_level_for_xp(new_xp)
            if new_level != old_level:
                level_up = True
            
            # Simple moving average for this mock logic
            c.execute("""
                UPDATE pronunciation_profiles 
                SET total_xp = ?, current_level = ?, total_recordings = total_recordings + 1,
                    avg_score = ((avg_score * total_recordings) + ?) / (total_recordings + 1),
                    avg_accuracy = ((avg_accuracy * total_recordings) + ?) / (total_recordings + 1),
                    avg_fluency = ((avg_fluency * total_recordings) + ?) / (total_recordings + 1),
                    updated_at = ?
                WHERE user_id = ?
            """, (new_xp, new_level, tech_data["overall_score"], tech_data["accuracy"], tech_data["fluency"], time.time(), user_id))
            
        # Insert Session
        c.execute("""
            INSERT INTO pronunciation_sessions 
            (user_id, lyrics_line, transcript, phoneme_result, accuracy, fluency, rhythm, stress, intonation, confidence, overall_score, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, expected_text, transcript, json.dumps(tech_data["phonemes"]),
            tech_data["accuracy"], tech_data["fluency"], tech_data["rhythm"],
            tech_data["stress"], tech_data["intonation"], tech_data["confidence"],
            tech_data["overall_score"], time.time()
        ))
        
        # Save memory
        c.execute("INSERT INTO pronunciation_coach_memory (user_id, message, created_at) VALUES (?, ?, ?)", 
                  (user_id, ai_data.get("summary", ""), time.time()))
                  
        # Mark goal complete and set new goal
        c.execute("UPDATE pronunciation_goals SET completed = 1 WHERE user_id = ? AND completed = 0", (user_id,))
        c.execute("INSERT INTO pronunciation_goals (user_id, goal_text, xp_reward, created_at) VALUES (?, ?, 50, ?)", 
                  (user_id, ai_data.get("next_goal", "Çalışmaya devam et!"), time.time()))
                  
        # Update word stats
        for w in tech_data["words"]:
            word_str = w["word"].lower()
            if w["status"] == "correct":
                c.execute("INSERT INTO pronunciation_words (user_id, word, correct_count) VALUES (?, ?, 1) ON CONFLICT(user_id, word) DO UPDATE SET correct_count = correct_count + 1", (user_id, word_str))
            else:
                c.execute("INSERT INTO pronunciation_words (user_id, word, wrong_count) VALUES (?, ?, 1) ON CONFLICT(user_id, word) DO UPDATE SET wrong_count = wrong_count + 1", (user_id, word_str))
                
        conn.commit()

    return AIResponse(
        overall_score=tech_data["overall_score"],
        cefr_level=tech_data["cefr_level"],
        fluency=tech_data["fluency"],
        accuracy=tech_data["accuracy"],
        rhythm=tech_data["rhythm"],
        stress=tech_data["stress"],
        intonation=tech_data["intonation"],
        confidence=tech_data["confidence"],
        words=tech_data["words"],
        summary=str(ai_data.get("summary", "İyi iş çıkardın!")) if not isinstance(ai_data.get("summary"), str) else ai_data.get("summary", "İyi iş çıkardın!"),
        strengths=ai_data.get("strengths", ["Teknik okuma başarılı"]) if isinstance(ai_data.get("strengths"), list) else [str(ai_data.get("strengths", "Teknik okuma başarılı"))],
        weaknesses=ai_data.get("weaknesses", ["Gelişim alanları belirleniyor..."]) if isinstance(ai_data.get("weaknesses"), list) else [str(ai_data.get("weaknesses", "Gelişim alanları belirleniyor..."))],
        suggestions=ai_data.get("suggestions", ["Daha fazla pratik yap."]) if isinstance(ai_data.get("suggestions"), list) else [str(ai_data.get("suggestions", "Daha fazla pratik yap."))],
        next_goal=str(ai_data.get("next_goal", "Yola devam!")) if not isinstance(ai_data.get("next_goal"), str) else ai_data.get("next_goal", "Yola devam!"),
        insight=str(ai_data.get("insight", "Harikasın!")) if not isinstance(ai_data.get("insight"), str) else ai_data.get("insight", "Harikasın!"),
        xp_gained=xp_gained,
        level_up=level_up
    )
