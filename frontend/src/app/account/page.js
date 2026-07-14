"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "../../../lib/api";

export default function AccountPage() {
  const router = useRouter();
  const [profile, setProfile] = useState(null);
  const [planStatus, setPlanStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [meData, planData] = await Promise.all([
          api.me(),
          api.getMyPlan()
        ]);
        setProfile(meData);
        setPlanStatus(planData);
      } catch (err) {
        // Not logged in or error
        router.push("/");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [router]);

  const handleLogoutAll = async () => {
    if (confirm("Tüm cihazlardan çıkış yapmak istediğinize emin misiniz?")) {
      await api.logoutAll();
      router.push("/");
    }
  };

  if (loading) {
    return <div className="min-h-screen bg-black text-white flex items-center justify-center">Yükleniyor...</div>;
  }

  return (
    <div className="min-h-screen bg-[#000000] text-white p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        
        <h1 className="text-4xl font-extrabold mb-8">Hesabım</h1>

        {/* PROFILE CARD */}
        <div className="bg-zinc-900/50 backdrop-blur-xl border border-zinc-800 rounded-2xl p-6">
          <h2 className="text-xl font-bold mb-4 text-zinc-400">Profil</h2>
          <div className="text-lg">
            <strong>E-Posta:</strong> {profile?.email}
          </div>
        </div>

        {/* SUBSCRIPTION CARD */}
        <div className="bg-zinc-900/50 backdrop-blur-xl border border-zinc-800 rounded-2xl p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-zinc-400">Mevcut Plan</h2>
            <div className={`px-3 py-1 rounded-full text-sm font-bold ${
              planStatus?.plan?.name === 'PRO' ? 'bg-green-500/20 text-green-500' :
              planStatus?.plan?.name === 'MASTER' ? 'bg-purple-500/20 text-purple-400' :
              'bg-zinc-800 text-zinc-300'
            }`}>
              {planStatus?.plan?.name || "FREE"}
            </div>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-black/50 p-4 rounded-xl">
              <div className="text-zinc-500 text-sm mb-1">Şarkı Analizi</div>
              <div className="text-xl font-bold">
                {planStatus?.usage?.songs || 0} / {planStatus?.plan?.songs_limit >= 999999 ? '∞' : planStatus?.plan?.songs_limit}
              </div>
            </div>
            <div className="bg-black/50 p-4 rounded-xl">
              <div className="text-zinc-500 text-sm mb-1">Kelime Araması</div>
              <div className="text-xl font-bold">
                {planStatus?.usage?.words || 0} / {planStatus?.plan?.words_limit >= 999999 ? '∞' : planStatus?.plan?.words_limit}
              </div>
            </div>
            <div className="bg-black/50 p-4 rounded-xl">
              <div className="text-zinc-500 text-sm mb-1">Telaffuz</div>
              <div className="text-xl font-bold">
                {planStatus?.usage?.pronunciation || 0} / {planStatus?.plan?.pronunciation_limit >= 999999 ? '∞' : planStatus?.plan?.pronunciation_limit}
              </div>
            </div>
            <div className="bg-black/50 p-4 rounded-xl">
              <div className="text-zinc-500 text-sm mb-1">AI Mesajları</div>
              <div className="text-xl font-bold">
                {planStatus?.usage?.ai_messages || 0} / {planStatus?.plan?.ai_messages_limit >= 999999 ? '∞' : planStatus?.plan?.ai_messages_limit}
              </div>
            </div>
          </div>

          <button 
            onClick={() => router.push("/pricing")}
            className="text-sm font-bold bg-white text-black px-4 py-2 rounded-full hover:bg-zinc-200 transition-colors"
          >
            Planı Yükselt
          </button>
        </div>

        {/* SECURITY CARD */}
        <div className="bg-zinc-900/50 backdrop-blur-xl border border-zinc-800 rounded-2xl p-6">
          <h2 className="text-xl font-bold mb-4 text-zinc-400">Güvenlik & Cihazlar</h2>
          <p className="text-zinc-400 mb-4 text-sm">
            Eğer hesabınıza başka bir yerden giriş yapıldığını düşünüyorsanız tüm cihazlardan çıkış yapabilirsiniz.
          </p>
          <button 
            onClick={handleLogoutAll}
            className="text-sm font-bold border border-red-500/50 text-red-500 hover:bg-red-500/10 px-4 py-2 rounded-full transition-colors"
          >
            Tüm Cihazlardan Çıkış Yap
          </button>
        </div>

      </div>
    </div>
  );
}
