"use client";
import { useState, useEffect } from "react";
import { X, Loader2, Volume2, Heart, Brain, Clock, Repeat, ArrowRight, Sparkles } from "lucide-react";
import ErrorBanner from "./ErrorBanner";
import { Card, CardContent, CardHeader } from "./ui/Card";
import { Badge } from "./ui/Badge";
import { Button } from "./ui/Button";
import { authFetch } from "../lib/api";

import { memo } from "react";

export default memo(function WordPanel({
  selectedWord,
  wordInfo,
  wordLoading,
  wordError,
  onRetry,
  onClose,
}) {
  const [isFavorite, setIsFavorite] = useState(false);
  const [isMemorized, setIsMemorized] = useState(false);
  const [isActionLoading, setIsActionLoading] = useState(false);

  useEffect(() => {
    if (wordInfo) {
      setIsFavorite(wordInfo.is_favorite || false);
      setIsMemorized(wordInfo.is_memorized || false);
    }
  }, [wordInfo]);

  if (!selectedWord) return null;

  const handleAudio = () => {
    if (wordInfo?.word) {
      const utterance = new SpeechSynthesisUtterance(wordInfo.word);
      utterance.lang = "en-US";
      window.speechSynthesis.speak(utterance);
    }
  };

  const handleFavorite = async () => {
    if (!wordInfo?.word || isActionLoading) return;
    setIsActionLoading(true);
    try {
      const res = await authFetch("/api/words/favorite", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ word: wordInfo.word }),
      });
      setIsFavorite(res.is_favorite);
    } catch (err) {
      // Failed silently
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleMemorize = async () => {
    if (!wordInfo?.word || isActionLoading) return;
    setIsActionLoading(true);
    try {
      const res = await authFetch("/api/words/memorize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ word: wordInfo.word }),
      });
      setIsMemorized(res.is_memorized);
    } catch (err) {
      // Failed silently
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleReview = async () => {
    if (!wordInfo?.word || isActionLoading) return;
    setIsActionLoading(true);
    try {
      const res = await authFetch("/api/words/review", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ word: wordInfo.word }),
      });
      // Optionally handle review_count update here
    } catch (err) {
      // Failed silently
    } finally {
      setIsActionLoading(false);
    }
  };

  const calculateColor = (perc) => {
    if (perc < 30) return "bg-red-500";
    if (perc < 70) return "bg-yellow-500";
    if (perc < 100) return "bg-blue-500";
    return "bg-green-500";
  };

  return (
    <Card className="flex flex-col h-full animate-slide-up">
      <CardHeader className="flex flex-row items-center justify-between pb-4 px-6 pt-6 border-b border-white/5">
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-3">
            <h2 className="text-3xl font-black tracking-tight text-white m-0">
              {selectedWord}
            </h2>
            <button 
              onClick={handleAudio}
              className="p-2 rounded-full bg-white/5 hover:bg-theme-500/20 hover:text-theme-400 text-white/70 transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-theme"
              aria-label="Telaffuzu Dinle"
              title="Telaffuzu Dinle"
            >
              <Volume2 size={20} />
            </button>
          </div>
          <div className="flex items-center gap-2">
            {wordInfo?.pronunciation && (
              <span className="text-sm font-mono text-white/40">/{wordInfo.pronunciation}/</span>
            )}
            {wordInfo?.part_of_speech && (
              <Badge variant="outline" className="text-[10px] uppercase tracking-widest border-white/10 text-white/60">
                {wordInfo.part_of_speech}
              </Badge>
            )}
            {wordInfo?.syllables && (
              <span className="text-xs text-white/30 tracking-widest uppercase ml-2">• {wordInfo.syllables}</span>
            )}
          </div>
        </div>
        <Button variant="ghost" size="icon" onClick={onClose} className="h-10 w-10 rounded-full bg-white/5 hover:bg-red-500/20 hover:text-red-400 text-white/50 transition-all">
          <X size={20} />
          <span className="sr-only">Kapat</span>
        </Button>
      </CardHeader>

      <CardContent className="flex-1 overflow-y-auto px-6 py-6 custom-scrollbar space-y-8">
        {wordLoading && (
          <div className="flex justify-center items-center py-20 flex-col gap-4">
            <Loader2 className="w-10 h-10 animate-spin text-theme-400" />
            <p className="text-sm font-medium text-white/40 animate-pulse">Sözlük aranıyor...</p>
          </div>
        )}

        {wordError && !wordLoading && (
          <ErrorBanner message={wordError} onRetry={onRetry} />
        )}

        {wordInfo && !wordLoading && !wordError && (
          <div className="space-y-8 animate-fade-in pb-10">
            
            {/* 1. Progress Section */}
            <div className="bg-white/5 border border-white/10 rounded-2xl p-5 shadow-inner">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xs font-bold uppercase tracking-widest text-white/40 m-0">Öğrenme İlerlemesi</h3>
                <Badge variant="default" className="text-[10px] bg-theme-500/20 text-theme-300 uppercase">
                  {wordInfo.mastery_level || "New"}
                </Badge>
              </div>
              
              <div className="w-full bg-black/40 rounded-full h-2.5 mb-5 overflow-hidden border border-white/5">
                <div 
                  className={`h-2.5 rounded-full ${calculateColor(wordInfo.learning_percentage || 0)} transition-all duration-1000 ease-out`}
                  style={{ width: `${Math.max(5, wordInfo.learning_percentage || 0)}%` }}
                ></div>
              </div>

              <div className="grid grid-cols-3 gap-2">
                <div className="flex flex-col items-center justify-center bg-black/20 rounded-xl py-3 border border-white/5">
                  <span className="text-2xl font-black text-white">{wordInfo.times_seen || 1}</span>
                  <span className="text-[10px] font-bold text-white/30 uppercase tracking-wider mt-1">Kez Görüldü</span>
                </div>
                
                <button 
                  onClick={handleFavorite}
                  disabled={isActionLoading}
                  className={`flex flex-col items-center justify-center rounded-xl py-3 border transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-theme ${isFavorite ? "bg-red-500/10 border-red-500/30 text-red-400" : "bg-black/20 border-white/5 text-white/30 hover:bg-white/5"}`}
                  aria-pressed={isFavorite}
                  aria-label={isFavorite ? "Favorilerden Çıkar" : "Favorilere Ekle"}
                >
                  <Heart className={`w-6 h-6 mb-1 ${isFavorite ? "fill-red-500 stroke-red-500 animate-pulse-soft" : "stroke-white/40"}`} />
                  <span className="text-[10px] font-bold uppercase tracking-wider">Favori</span>
                </button>

                <button 
                  onClick={handleMemorize}
                  disabled={isActionLoading}
                  className={`flex flex-col items-center justify-center rounded-xl py-3 border transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-theme ${isMemorized ? "bg-green-500/10 border-green-500/30 text-green-400" : "bg-black/20 border-white/5 text-white/30 hover:bg-white/5"}`}
                  aria-pressed={isMemorized}
                  aria-label={isMemorized ? "Öğrenildi İşaretini Kaldır" : "Öğrenildi Olarak İşaretle"}
                >
                  <Brain className={`w-6 h-6 mb-1 ${isMemorized ? "stroke-green-400 animate-pulse-soft" : "stroke-white/40"}`} />
                  <span className="text-[10px] font-bold uppercase tracking-wider">Öğrenildi</span>
                </button>
              </div>
            </div>

            {/* 2. Meanings Section */}
            <div className="space-y-4">
              <h3 className="text-xs font-bold uppercase tracking-widest text-white/40 m-0">Anlamlar</h3>
              
              {/* Contextual Meaning (AI) */}
              {wordInfo.contextual_meaning && (
                <div className="bg-theme-500/10 border border-theme-500/30 rounded-xl p-4 relative overflow-hidden group">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-theme-500/20 blur-3xl -mr-10 -mt-10 transition-transform group-hover:scale-150"></div>
                  <div className="relative z-10">
                    <p className="text-[10px] font-black uppercase tracking-widest text-theme-400 mb-2 flex items-center gap-1.5">
                      <Sparkles size={12} /> Bu Şarkıdaki Bağlam
                    </p>
                    <p className="text-lg font-bold text-white/90 leading-snug">{wordInfo.contextual_meaning}</p>
                  </div>
                </div>
              )}

              {/* Dictionary Translations */}
              {Array.isArray(wordInfo.turkish_meanings) && wordInfo.turkish_meanings.length > 0 && (
                <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                  <p className="text-[10px] font-black uppercase tracking-widest text-white/30 mb-2">Genel Anlamlar (Çeviri)</p>
                  <div className="flex flex-col gap-2">
                    {wordInfo.turkish_meanings.map((tm, idx) => (
                      <p key={idx} className="text-base font-semibold text-white/80 flex items-start gap-2 m-0">
                        <ArrowRight size={16} className="text-white/20 mt-0.5 shrink-0" /> {tm}
                      </p>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* 3. Dictionary Details */}
            {wordInfo.definition && (
              <div className="space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-widest text-white/40 m-0 flex items-center gap-2">
                  İngilizce Açıklama
                </h3>
                <p className="text-[14px] leading-relaxed text-white/70 bg-black/40 p-4 rounded-xl border border-white/5">{wordInfo.definition}</p>
              </div>
            )}

            {/* Examples */}
            {Array.isArray(wordInfo.examples) && wordInfo.examples.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-widest text-white/40 m-0">Örnekler</h3>
                <div className="flex flex-col gap-2">
                  {wordInfo.examples.map((ex, idx) => (
                    <div key={idx} className="bg-white/[0.03] border-l-2 border-theme-500/50 p-3 rounded-r-xl">
                      <p className="text-[13px] italic text-white/80 m-0">"{ex}"</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Grid for Synonyms & Antonyms */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Array.isArray(wordInfo.synonyms) && wordInfo.synonyms.length > 0 && (
                <div className="bg-white/5 p-4 rounded-xl border border-white/5">
                  <p className="text-[10px] uppercase tracking-widest text-white/30 font-bold mb-3">Eş Anlamlılar</p>
                  <div className="flex flex-wrap gap-2">
                    {wordInfo.synonyms.slice(0, 8).map(syn => (
                       <Badge key={syn} variant="outline" className="text-xs bg-black/40 border-white/10 text-white/60">{syn}</Badge>
                    ))}
                  </div>
                </div>
              )}

              {Array.isArray(wordInfo.antonyms) && wordInfo.antonyms.length > 0 && (
                <div className="bg-white/5 p-4 rounded-xl border border-white/5">
                  <p className="text-[10px] uppercase tracking-widest text-white/30 font-bold mb-3">Zıt Anlamlılar</p>
                  <div className="flex flex-wrap gap-2">
                    {wordInfo.antonyms.slice(0, 8).map(ant => (
                       <Badge key={ant} variant="outline" className="text-xs bg-black/40 border-white/10 text-white/60">{ant}</Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Advanced Arrays (Word Family, Collocations, Phrasal Verbs) */}
            <div className="space-y-4">
              {Array.isArray(wordInfo.collocations) && wordInfo.collocations.length > 0 && (
                <div className="bg-black/40 p-4 rounded-xl border border-white/5">
                  <p className="text-[10px] font-black uppercase tracking-widest text-blue-400 mb-3">Sık Kullanılan Kalıplar (Collocations)</p>
                  <div className="flex flex-wrap gap-2">
                    {wordInfo.collocations.map((c, i) => <Badge key={i} variant="secondary" className="bg-blue-500/10 text-blue-200 border border-blue-500/20">{c}</Badge>)}
                  </div>
                </div>
              )}
              {Array.isArray(wordInfo.phrasal_verbs) && wordInfo.phrasal_verbs.length > 0 && (
                <div className="bg-black/40 p-4 rounded-xl border border-white/5">
                  <p className="text-[10px] font-black uppercase tracking-widest text-pink-400 mb-3">Phrasal Verbs</p>
                  <div className="flex flex-wrap gap-2">
                    {wordInfo.phrasal_verbs.map((pv, i) => <Badge key={i} variant="secondary" className="bg-pink-500/10 text-pink-200 border border-pink-500/20">{pv}</Badge>)}
                  </div>
                </div>
              )}
              {Array.isArray(wordInfo.word_family) && wordInfo.word_family.length > 0 && (
                <div className="bg-black/40 p-4 rounded-xl border border-white/5">
                  <p className="text-[10px] font-black uppercase tracking-widest text-yellow-400 mb-3">Kelime Ailesi</p>
                  <div className="flex flex-wrap gap-2">
                    {wordInfo.word_family.map((wf, i) => <Badge key={i} variant="secondary" className="bg-yellow-500/10 text-yellow-200 border border-yellow-500/20">{wf}</Badge>)}
                  </div>
                </div>
              )}
            </div>

            {/* 4. AI Learning Tip */}
            {wordInfo.ai_learning_tip && (
              <div className="bg-gradient-to-br from-purple-900/40 to-theme-900/20 border border-purple-500/30 rounded-2xl p-5 shadow-inner">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-6 h-6 rounded-full bg-purple-500/20 flex items-center justify-center shrink-0">
                    <Brain size={12} className="text-purple-300" />
                  </div>
                  <h3 className="text-[11px] font-black uppercase tracking-widest text-purple-300 m-0">AI Öğrenme Tüyosu</h3>
                </div>
                <p className="text-[13px] font-medium text-purple-100/90 leading-relaxed m-0 ml-8">
                  {wordInfo.ai_learning_tip}
                </p>
              </div>
            )}

            {/* Timing Footer */}
            <div className="flex items-center justify-center gap-4 text-[10px] text-white/30 uppercase tracking-widest font-bold pt-4 border-t border-white/5">
              <span className="flex items-center gap-1.5"><Clock size={12} /> İlk Görüldü: {new Date(wordInfo.first_seen * 1000).toLocaleDateString("tr-TR")}</span>
              <span>•</span>
              <span className="flex items-center gap-1.5"><Repeat size={12} /> Son Tekrar: {new Date(wordInfo.last_seen * 1000).toLocaleDateString("tr-TR")}</span>
            </div>

          </div>
        )}
      </CardContent>
    </Card>
  );
});
