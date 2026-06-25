"use client";

import React, { useEffect, useState, memo } from "react";
import { api } from "../lib/api";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { Target, TrendingUp, Mic, Star, Award, Zap, Award as AwardIcon, Loader2, ArrowLeft } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/Card";
import { Button } from "./ui/Button";

export default memo(function ProgressDashboard({ onClose }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadStats() {
      try {
        const data = await api.getProgressStats();
        setStats(data);
      } catch (err) {
        // Failed silently for UI handling
      } finally {
        setLoading(false);
      }
    }
    loadStats();
  }, []);

  if (loading) {
    return (
      <Card className="w-full h-full flex flex-col justify-center items-center gap-4 animate-slide-up">
        <Loader2 className="w-8 h-8 text-theme animate-spin" />
        <p className="text-white/50 text-sm">Veriler yükleniyor...</p>
      </Card>
    );
  }

  if (!stats) {
    return (
      <Card className="w-full h-full flex flex-col justify-center items-center gap-4 animate-slide-up">
        <p className="text-white/50 text-sm">Veriler yüklenemedi.</p>
        <Button variant="secondary" onClick={onClose} className="rounded-full px-6">
          Geri Dön
        </Button>
      </Card>
    );
  }

  const currentXP = stats.total_xp;
  let nextLevelXP = 200;
  if (currentXP >= 200) nextLevelXP = 500;
  if (currentXP >= 500) nextLevelXP = 1000;
  if (currentXP >= 1000) nextLevelXP = 2000;
  if (currentXP >= 2000) nextLevelXP = 4000;
  if (currentXP >= 4000) nextLevelXP = 7000;
  if (currentXP >= 7000) nextLevelXP = 12000;
  if (currentXP >= 12000) nextLevelXP = 20000;
  
  const xpPercentage = Math.min(100, (currentXP / nextLevelXP) * 100);

  return (
    <Card className="w-full h-full flex flex-col overflow-hidden animate-slide-up rounded-none md:rounded-2xl border-x-0 md:border-x">
      {/* Header */}
      <div className="sticky top-0 z-20 bg-black/60 backdrop-blur-xl px-6 md:px-8 py-5 flex justify-between items-center border-b border-white/5 shrink-0">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={onClose} className="rounded-full w-10 h-10 shrink-0 md:hidden">
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div className="p-3 bg-gradient-to-tr from-theme-500/20 to-purple-500/20 rounded-xl border border-white/10 shadow-glow hidden sm:flex">
            <Mic className="w-6 h-6 text-theme" />
          </div>
          <div>
            <h1 className="text-xl md:text-2xl font-black text-white tracking-tight leading-none mb-1">AI Pronunciation Coach</h1>
            <p className="text-xs md:text-sm font-medium text-white/50 m-0">Gerçek zamanlı telaffuz analizi ve gelişim yol haritası.</p>
          </div>
        </div>
        <Button variant="ghost" size="icon" onClick={onClose} className="rounded-full w-10 h-10 shrink-0 hidden md:flex">
          <span className="text-xl leading-none">×</span>
        </Button>
      </div>

      {/* Scrollable Body */}
      <CardContent className="flex-1 overflow-y-auto overflow-x-hidden p-6 md:p-8 custom-scrollbar">
        <div className="max-w-7xl mx-auto space-y-8">
          
          {/* Level Card */}
          <div className="relative overflow-hidden bg-gradient-to-br from-theme-900/40 to-black border border-theme-500/20 rounded-2xl p-6 shadow-xl group">
            <div className="absolute -right-10 -top-10 w-40 h-40 bg-theme-500/20 blur-3xl rounded-full group-hover:bg-theme-400/30 transition-colors"></div>
            
            <div className="flex justify-between items-start mb-6 relative z-10">
              <div>
                <p className="text-theme-300 text-[10px] font-bold uppercase tracking-widest mb-1">Mevcut Seviye</p>
                <h2 className="text-3xl font-black text-white m-0">{stats.current_level}</h2>
              </div>
              <div className="p-3 bg-theme-500/20 rounded-2xl shadow-glow">
                <Star className="w-6 h-6 text-theme-300 fill-theme-400/20" />
              </div>
            </div>
            
            <div className="relative z-10">
              <div className="flex justify-between items-end mb-2">
                <span className="text-white font-bold text-sm">{currentXP} <span className="text-white/40 font-normal">XP</span></span>
                <span className="text-theme-400 font-bold text-[10px] uppercase tracking-wider">{nextLevelXP} Hedef</span>
              </div>
              <div className="h-3 bg-black/40 rounded-full overflow-hidden border border-white/5">
                <div 
                  className="h-full bg-gradient-to-r from-theme-600 to-theme-300 rounded-full shadow-glow transition-all duration-1000 ease-out"
                  style={{ width: `${xpPercentage}%` }}
                ></div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
            
            {/* Left Column */}
            <div className="xl:col-span-2 space-y-8">
              {/* Line Chart Progress */}
              <div>
                <div className="flex items-center gap-2 mb-4 pl-1">
                  <TrendingUp className="w-5 h-5 text-theme-400" />
                  <h3 className="text-base font-bold text-white tracking-wide m-0">Son Kayıtların (30)</h3>
                </div>
                <div className="bg-white/5 border border-white/10 rounded-2xl p-6 h-[300px] w-full shadow-sm">
                  {stats.history && stats.history.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={stats.history} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <defs>
                          <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="var(--theme-color, #a855f7)" stopOpacity={0.3}/>
                            <stop offset="95%" stopColor="var(--theme-color, #a855f7)" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <XAxis 
                          dataKey="date" 
                          tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 10 }}
                          tickLine={false}
                          axisLine={false}
                          dy={10}
                        />
                        <YAxis 
                          tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 10 }}
                          tickLine={false}
                          axisLine={false}
                          domain={[0, 100]}
                        />
                        <Tooltip 
                          contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(10px)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '12px', fontSize: '12px', color: '#fff' }}
                          itemStyle={{ color: 'var(--theme-color, #a855f7)', fontWeight: 'bold' }}
                          labelStyle={{ color: 'rgba(255,255,255,0.5)', marginBottom: '4px' }}
                        />
                        <Area type="monotone" dataKey="score" stroke="var(--theme-color, #a855f7)" strokeWidth={3} fillOpacity={1} fill="url(#colorScore)" />
                      </AreaChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="w-full h-full flex flex-col items-center justify-center text-center opacity-50">
                      <TrendingUp className="w-12 h-12 text-white/20 mb-3" />
                      <p className="text-sm text-white/50 m-0">Grafik için kayıt bekleniyor...</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Mini Stats Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-white/5 border border-white/10 hover:border-white/20 transition-colors rounded-2xl p-5 flex flex-col justify-center relative overflow-hidden group">
                  <div className="absolute -right-6 -bottom-6 w-20 h-20 bg-theme-500/10 rounded-full blur-xl group-hover:bg-theme-500/20 transition-colors" />
                  <p className="text-xs font-bold uppercase tracking-widest text-white/40 mb-2 z-10 m-0">Günlük Skor</p>
                  <p className="text-3xl font-black text-white z-10 m-0">{stats.daily_score}</p>
                </div>
                <div className="bg-white/5 border border-white/10 hover:border-white/20 transition-colors rounded-2xl p-5 flex flex-col justify-center relative overflow-hidden group">
                  <div className="absolute -right-6 -bottom-6 w-20 h-20 bg-blue-500/10 rounded-full blur-xl group-hover:bg-blue-500/20 transition-colors" />
                  <p className="text-xs font-bold uppercase tracking-widest text-white/40 mb-2 z-10 m-0">Süre</p>
                  <p className="text-3xl font-black text-white z-10 m-0">{Math.floor(stats.total_time_minutes)}<span className="text-base font-bold text-white/30 ml-1.5">dk</span></p>
                </div>
                <div className="bg-white/5 border border-white/10 hover:border-white/20 transition-colors rounded-2xl p-5 flex flex-col justify-center relative overflow-hidden group">
                  <div className="absolute -right-6 -bottom-6 w-20 h-20 bg-green-500/10 rounded-full blur-xl group-hover:bg-green-500/20 transition-colors" />
                  <p className="text-xs font-bold uppercase tracking-widest text-white/40 mb-2 z-10 m-0">Şarkı</p>
                  <p className="text-3xl font-black text-white z-10 m-0">{stats.completed_songs}</p>
                </div>
                <div className="bg-white/5 border border-white/10 hover:border-white/20 transition-colors rounded-2xl p-5 flex flex-col justify-center relative overflow-hidden group">
                  <div className="absolute -right-6 -bottom-6 w-20 h-20 bg-yellow-500/10 rounded-full blur-xl group-hover:bg-yellow-500/20 transition-colors" />
                  <p className="text-xs font-bold uppercase tracking-widest text-white/40 mb-2 z-10 m-0">Rozetler</p>
                  <p className="text-3xl font-black text-white z-10 m-0">{stats.badges ? stats.badges.filter(b=>b.unlocked).length : 0}<span className="text-base font-bold text-white/30 ml-1.5">/ {stats.badges ? stats.badges.length : 6}</span></p>
                </div>
              </div>
            </div>

            {/* Right Column */}
            <div className="space-y-8">
              {/* Weakness Roadmap */}
              <div>
                <div className="flex items-center gap-2 mb-4 pl-1">
                  <Target className="w-5 h-5 text-red-400" />
                  <h3 className="text-base font-bold text-white tracking-wide m-0">Geliştirmen Gerekenler</h3>
                </div>
                <div className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-6 shadow-sm">
                  {stats.worst_words && stats.worst_words.length > 0 ? (
                    stats.worst_words.slice(0, 5).map((w, idx) => (
                      <div key={idx} className="relative group">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-[15px] font-bold text-white group-hover:text-theme-200 transition-colors">{w.word}</span>
                          <span className="text-[11px] font-bold text-red-400 bg-red-400/10 px-2 py-1 rounded-md border border-red-400/20 shadow-sm">% {w.error_rate} Hata</span>
                        </div>
                        <div className="h-2 bg-black/40 rounded-full overflow-hidden border border-white/5">
                          <div 
                            className="h-full bg-gradient-to-r from-red-500 to-orange-400 rounded-full shadow-glow"
                            style={{ width: `${w.error_rate}%` }}
                          ></div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="py-6 flex flex-col items-center justify-center opacity-70">
                      <Award className="w-12 h-12 text-yellow-400 mb-3" />
                      <p className="text-sm font-medium text-white m-0 text-center">Harika gidiyorsun!</p>
                      <p className="text-xs text-white/50 text-center mt-1">Şu an büyük bir hata tespit edilmedi.</p>
                    </div>
                  )}
                </div>
              </div>

              {/* AI Memory / Goal */}
              <div className="bg-gradient-to-br from-theme-900/30 to-purple-900/20 border border-theme-500/30 rounded-2xl p-6 md:p-8 relative overflow-hidden shadow-xl">
                <div className="absolute inset-0 bg-noise opacity-[0.03]"></div>
                
                <div className="flex items-start gap-4 relative z-10 mb-6">
                  <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-theme-500 to-purple-600 flex items-center justify-center text-xl shadow-glow shrink-0 border border-white/10">
                    🤖
                  </div>
                  <div>
                    <p className="text-theme-300 text-[10px] font-black uppercase tracking-widest mb-1.5 m-0">Yapay Zeka Koçu</p>
                    <p className="text-[15px] text-white leading-relaxed font-medium">"{stats.motivation}"</p>
                  </div>
                </div>
                
                <div className="pt-5 border-t border-theme-500/20 relative z-10 bg-black/20 -mx-6 -mb-6 md:-mx-8 md:-mb-8 px-6 md:px-8 pb-6 md:pb-8">
                  <div className="flex items-center gap-2 mb-3">
                    <Zap className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                    <p className="text-[10px] font-black uppercase tracking-widest text-white/50 m-0">Sıradaki Hedef</p>
                  </div>
                  <p className="text-sm text-theme-100 font-bold m-0 leading-relaxed">{stats.daily_goal}</p>
                </div>
              </div>
            </div>
          </div>

        </div>
      </CardContent>
    </Card>
  );
});
