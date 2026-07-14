"use client";

import { useEffect, useState } from "react";
import Auth from "./Auth";
import Footer from "./Footer";
import Navbar from "./Navbar";
import { api } from "../lib/api";
import { Button } from "./ui/Button";

export default function LandingPage({ onAuthenticated }) {
  const [authMode, setAuthMode] = useState(null);
  const [activeFaq, setActiveFaq] = useState(null);

  useEffect(() => {
    const elements = document.querySelectorAll(".reveal");
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            entry.target.classList.remove("opacity-0", "translate-y-10");
          }
        });
      },
      { threshold: 0.12 },
    );
    elements.forEach((element) => observer.observe(element));
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!authMode) return;
    const closeOnEscape = (event) => {
      if (event.key === "Escape") setAuthMode(null);
    };
    document.addEventListener("keydown", closeOnEscape);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", closeOnEscape);
      document.body.style.overflow = "auto";
    };
  }, [authMode]);

  return (
    <main className="min-h-screen bg-[#050505] text-white selection:bg-green-500/30 overflow-x-hidden">
      <Navbar onAuth={setAuthMode} />

      {/* 1. HERO SECTION */}
      <section className="relative pt-40 pb-20 px-4 md:px-8 max-w-7xl mx-auto flex flex-col items-center text-center">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-green-500/20 blur-[120px] rounded-full pointer-events-none"></div>
        <div className="reveal opacity-0 translate-y-10 transition-all duration-1000 ease-out z-10">
          <div className="inline-block mb-6 px-4 py-1.5 rounded-full border border-white/10 bg-white/5 backdrop-blur-md text-sm font-medium text-zinc-300">
            <span className="text-green-400 mr-2">✦</span>
            Yapay Zeka Destekli Dil Koçu
          </div>
          <h1 className="text-5xl md:text-8xl font-black tracking-tighter mb-8 leading-tight">
            Müzik dinlerken <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-green-400 via-emerald-500 to-teal-500">
              İngilizce öğren.
            </span>
          </h1>
          <p className="text-lg md:text-2xl text-zinc-400 max-w-3xl mx-auto mb-10 leading-relaxed font-light">
            Sıkıcı ders kitaplarını unut. En sevdiğin şarkılarla kelime öğren, 
            yapay zeka koçunla telaffuzunu mükemmelleştir.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Button 
              size="lg"
              variant="primary"
              onClick={() => setAuthMode("register")}
              className="w-full sm:w-auto px-8 py-6 rounded-full font-bold text-lg hover:scale-105"
            >
              Ücretsiz Başla
            </Button>
            <Button 
              size="lg"
              variant="secondary"
              onClick={async () => {
                const url = await api.spotifyConnectUrl();
                window.location.href = url;
              }}
              className="w-full sm:w-auto px-8 py-6 rounded-full font-bold hover:scale-105 flex items-center justify-center gap-2"
            >
              <svg className="w-5 h-5 text-[#1DB954]" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.54.659.3 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15.001 10.62 18.66 12.84c.361.181.54.78.3 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.6.18-1.2.72-1.381 4.26-1.261 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.54-1.02.72-1.56.3z"/></svg>
              Spotify ile Bağlan
            </Button>
          </div>
        </div>
      </section>

      {/* 2. NASIL ÇALIŞIR */}
      <section className="py-24 px-4 relative">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16 reveal opacity-0 translate-y-10 transition-all duration-1000">
            <h2 className="text-3xl md:text-5xl font-black mb-4">Müzik, Öğretmenin Olsun.</h2>
            <p className="text-zinc-400 text-lg">Eğlenceli ve akılda kalıcı öğrenme metodu.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: "01", title: "Şarkını Seç", desc: "Spotify hesabını bağla ve öğrenmek istediğin favori şarkını aç." },
              { step: "02", title: "Anlamını Keşfet", desc: "Bilmediğin kelimelerin Türkçe çevirisine ve okunuşlarına anında bak." },
              { step: "03", title: "Telaffuz Pratiği", desc: "AI ses koçuyla mikrofonu aç, kendi sesini kaydet ve analiz raporu al." },
            ].map((item, i) => (
              <div key={i} className="reveal opacity-0 translate-y-10 transition-all duration-1000 bg-zinc-900/40 border border-zinc-800/50 p-8 rounded-3xl backdrop-blur-sm hover:bg-zinc-900/60 transition-colors" style={{ transitionDelay: `${i * 100}ms` }}>
                <div className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-br from-zinc-600 to-zinc-800 mb-6">{item.step}</div>
                <h3 className="text-xl font-bold mb-3">{item.title}</h3>
                <p className="text-zinc-400 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 3. ÖZELLİKLER & AI */}
      <section className="py-24 px-4 bg-zinc-950/50">
        <div className="max-w-7xl mx-auto space-y-32">
          {/* Shadowing Mode */}
          <div className="flex flex-col md:flex-row items-center gap-12 reveal opacity-0 translate-y-10 transition-all duration-1000">
            <div className="flex-1">
              <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-500/10 text-blue-400 rounded-full text-sm font-bold mb-4 border border-blue-500/20">
                <span className="relative flex h-2 w-2"><span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span><span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span></span>
                Live Feature
              </div>
              <h2 className="text-4xl font-black mb-6">Shadowing Mode</h2>
              <p className="text-lg text-zinc-400 leading-relaxed mb-6">
                Native speaker&apos;ı duyduğun anda taklit etmeye dayalı en etkili konuşma pratik metodu artık müzikle birleşti. Şarkı sözleri akarken mikrofonu aç ve eşlik et.
              </p>
              <ul className="space-y-4">
                <li className="flex items-center gap-3"><span className="text-blue-500">✓</span> Akıcı konuşma refleksini geliştirir</li>
                <li className="flex items-center gap-3"><span className="text-blue-500">✓</span> Gerçek zamanlı ritim eşleşmesi</li>
              </ul>
            </div>
            <div className="flex-1 w-full bg-gradient-to-br from-blue-900/20 to-black p-1 rounded-3xl border border-white/5">
              <div className="aspect-video bg-zinc-900 rounded-[22px] flex items-center justify-center relative overflow-hidden shadow-2xl">
                <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10"></div>
                <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center animate-pulse">
                  <svg className="w-8 h-8 text-black" fill="currentColor" viewBox="0 0 24 24"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
                </div>
              </div>
            </div>
          </div>

          {/* AI Coach */}
          <div className="flex flex-col md:flex-row-reverse items-center gap-12 reveal opacity-0 translate-y-10 transition-all duration-1000">
            <div className="flex-1">
              <div className="inline-flex items-center gap-2 px-3 py-1 bg-purple-500/10 text-purple-400 rounded-full text-sm font-bold mb-4 border border-purple-500/20">
                ✨ Yapay Zeka
              </div>
              <h2 className="text-4xl font-black mb-6">AI Telaffuz Koçu</h2>
              <p className="text-lg text-zinc-400 leading-relaxed mb-6">
                Her analizinde gelişimi takip eden özel bir öğretmenin var. Sesini kaydedip saniyeler içinde zayıf yönlerini, güçlü taraflarını ve çalışman gereken bir sonraki hedefi gör.
              </p>
              <ul className="space-y-4">
                <li className="flex items-center gap-3"><span className="text-purple-500">✓</span> Fonem (Ses) bazlı analiz</li>
                <li className="flex items-center gap-3"><span className="text-purple-500">✓</span> Geçmiş performans belleği</li>
                <li className="flex items-center gap-3"><span className="text-purple-500">✓</span> Ritim ve tonlama grafikleri</li>
              </ul>
            </div>
            <div className="flex-1 w-full bg-gradient-to-br from-purple-900/20 to-black p-1 rounded-3xl border border-white/5">
              <div className="aspect-square md:aspect-[4/3] bg-zinc-900 rounded-[22px] p-6 flex flex-col gap-4 relative overflow-hidden">
                <div className="bg-zinc-800/50 p-4 rounded-xl border border-white/5 backdrop-blur-sm">
                  <div className="text-xs text-purple-400 font-bold mb-1">AI Coach</div>
                  <div className="text-sm text-zinc-300">Geçen hafta R sesinde zorlanıyordun, bugün harika bir gelişim görüyorum!</div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-green-500/10 p-4 rounded-xl border border-green-500/20">
                    <div className="text-xs text-green-400 font-bold">Accuracy</div>
                    <div className="text-2xl font-black">92%</div>
                  </div>
                  <div className="bg-blue-500/10 p-4 rounded-xl border border-blue-500/20">
                    <div className="text-xs text-blue-400 font-bold">Fluency</div>
                    <div className="text-2xl font-black">88%</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4. PREMIUM PLANS */}
      <section className="py-32 px-4 relative bg-[#020202]">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-4xl h-[300px] bg-green-500/10 blur-[150px] rounded-full pointer-events-none"></div>
        <div className="max-w-7xl mx-auto relative z-10">
          <div className="text-center mb-16 reveal opacity-0 translate-y-10 transition-all duration-1000">
            <h2 className="text-4xl md:text-5xl font-black mb-4">Sınırları Kaldır.</h2>
            <p className="text-zinc-400 text-lg">Hedeflerine ulaşmak için sana en uygun planı seç.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 items-center max-w-6xl mx-auto">
            {/* FREE */}
            <div className="reveal opacity-0 translate-y-10 transition-all duration-1000 bg-zinc-900/40 backdrop-blur-xl border border-zinc-800 rounded-[2rem] p-8 hover:border-zinc-700 transition-colors">
              <h3 className="text-2xl font-bold mb-2">Free</h3>
              <div className="text-zinc-400 mb-6 text-sm">Temelleri atmak için harika bir başlangıç.</div>
              <div className="text-4xl font-black mb-8">$0<span className="text-lg font-normal text-zinc-500">/ay</span></div>
              <ul className="space-y-4 mb-8 text-zinc-300">
                <li className="flex items-center gap-3"><span className="text-zinc-600">✓</span> Günlük 5 Şarkı Seçimi</li>
                <li className="flex items-center gap-3"><span className="text-zinc-600">✓</span> 5 Telaffuz Analizi</li>
                <li className="flex items-center gap-3"><span className="text-zinc-600">✓</span> 10 AI Sorusu</li>
                <li className="flex items-center gap-3 text-zinc-600"><span className="opacity-50">✗</span> Shadowing Mode (Yok)</li>
              </ul>
              <button onClick={() => setAuthMode("register")} className="w-full py-4 rounded-full font-bold bg-zinc-800 hover:bg-zinc-700 text-white transition-colors">
                Ücretsiz Başla
              </button>
            </div>

            {/* PRO */}
            <div className="reveal opacity-0 translate-y-10 transition-all duration-1000 delay-100 bg-zinc-900/80 backdrop-blur-xl border-2 border-green-500 rounded-[2.5rem] p-10 transform md:scale-105 shadow-[0_0_50px_rgba(34,197,94,0.15)] relative">
              <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-green-500 text-black px-4 py-1 rounded-full text-xs font-black uppercase tracking-wider">
                En Popüler
              </div>
              <h3 className="text-2xl font-black mb-2 text-green-400">Lingofy Pro</h3>
              <div className="text-zinc-300 mb-6 text-sm">Ciddi öğreniciler için sınırsız deneyim.</div>
              <div className="text-5xl font-black mb-8">$9.99<span className="text-lg font-normal text-zinc-500">/ay</span></div>
              <ul className="space-y-4 mb-8 text-white font-medium">
                <li className="flex items-center gap-3"><span className="text-green-500">✓</span> Sınırsız Şarkı Analizi</li>
                <li className="flex items-center gap-3"><span className="text-green-500">✓</span> Sınırsız Telaffuz Koçu</li>
                <li className="flex items-center gap-3"><span className="text-green-500">✓</span> Sınırsız AI Chat</li>
                <li className="flex items-center gap-3"><span className="text-green-500">✓</span> Sınırsız Shadowing Mode</li>
                <li className="flex items-center gap-3"><span className="text-green-500">✓</span> Performans Geçmişi</li>
              </ul>
              <button onClick={() => setAuthMode("register")} className="w-full py-4 rounded-full font-black bg-green-500 hover:bg-green-400 text-black transition-colors shadow-lg shadow-green-500/25 hover:shadow-green-500/40 hover:scale-105 active:scale-95">
                Pro&apos;ya Geç
              </button>
            </div>

            {/* MASTER */}
            <div className="reveal opacity-0 translate-y-10 transition-all duration-1000 delay-200 bg-zinc-900/40 backdrop-blur-xl border border-zinc-800 rounded-[2rem] p-8 hover:border-zinc-700 transition-colors">
              <h3 className="text-2xl font-bold mb-2 text-purple-400">Master</h3>
              <div className="text-zinc-400 mb-6 text-sm">Native speaker olmak isteyenlere.</div>
              <div className="text-4xl font-black mb-8">$19.99<span className="text-lg font-normal text-zinc-500">/ay</span></div>
              <ul className="space-y-4 mb-8 text-zinc-300">
                <li className="flex items-center gap-3"><span className="text-purple-400">✓</span> Pro&apos;daki Her Şey</li>
                <li className="flex items-center gap-3"><span className="text-purple-400">✓</span> IELTS/TOEFL Simülasyonu</li>
                <li className="flex items-center gap-3"><span className="text-purple-400">✓</span> Native IPA Analizi</li>
                <li className="flex items-center gap-3"><span className="text-purple-400">✓</span> Birebir Mentörlük</li>
              </ul>
              <button onClick={() => setAuthMode("register")} className="w-full py-4 rounded-full font-bold bg-zinc-100 hover:bg-white text-black transition-colors">
                Master Ol
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* 5. YORUMLAR */}
      <section className="py-24 px-4 bg-zinc-950">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16 reveal opacity-0 translate-y-10 transition-all duration-1000">
            <h2 className="text-3xl md:text-4xl font-black mb-4">Öğrencilerin Yorumları</h2>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { name: "Ayşe Y.", text: "Kitaplarla yıllarca öğrenemediğim İngilizceyi sevdiğim şarkılarla öğrendim. AI Coach sanki gerçek bir hoca gibi hatalarımı düzeltiyor." },
              { name: "Emir C.", text: "Shadowing mode bağımlılık yaptı! Ritim tutarak konuştuğum için artık yabancılarla konuşurken çok daha akıcıyım." },
              { name: "Selin K.", text: "Kelimelerin şarkı içindeki bağlamsal çevirilerini görmek müthiş. Düz çeviri programlarının çok ötesinde." }
            ].map((review, idx) => (
              <div key={idx} className="reveal opacity-0 translate-y-10 transition-all duration-1000 bg-zinc-900/50 p-6 rounded-2xl border border-white/5" style={{ transitionDelay: `${idx * 100}ms` }}>
                <div className="flex text-green-400 mb-4">★★★★★</div>
                <p className="text-zinc-300 italic mb-4 leading-relaxed">&quot;{review.text}&quot;</p>
                <div className="font-bold text-zinc-400">— {review.name}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 6. SSS */}
      <section className="py-24 px-4">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-16 reveal opacity-0 translate-y-10 transition-all duration-1000">
            <h2 className="text-3xl font-black mb-4">Sıkça Sorulan Sorular</h2>
          </div>
          <div className="space-y-4">
            {[
              { q: "Spotify Premium gerekli mi?", a: "Hayır. Free hesaplarla 30 saniyelik önizlemeler üzerinden pratik yapabilirsin, ancak tam şarkı deneyimi için Spotify Premium önerilir." },
              { q: "AI Telaffuz koçu nasıl çalışıyor?", a: "Sesini kaydettiğinde yapay zeka modelimiz saniyeler içinde sesini metne döker, beklenen kelimelerle karşılaştırır ve sana ritim, doğruluk, akıcılık puanları verir." },
              { q: "Planımı istediğim zaman iptal edebilir miyim?", a: "Evet, Lingofy Premium abonelikleri taahhütsüzdür. Dilediğin an iptal edebilirsin." },
            ].map((faq, idx) => (
              <div key={idx} className="reveal opacity-0 translate-y-10 transition-all duration-1000 bg-zinc-900/40 border border-white/5 rounded-2xl overflow-hidden cursor-pointer hover:bg-zinc-900/60 transition-colors" onClick={() => setActiveFaq(activeFaq === idx ? null : idx)}>
                <div className="p-6 flex justify-between items-center font-bold">
                  {faq.q}
                  <span className="text-zinc-500">{activeFaq === idx ? "−" : "+"}</span>
                </div>
                {activeFaq === idx && <div className="px-6 pb-6 text-zinc-400">{faq.a}</div>}
              </div>
            ))}
          </div>
        </div>
      </section>

      <Footer />

      {/* AUTH MODAL */}
      {authMode && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <button className="absolute inset-0 bg-black/80 backdrop-blur-sm cursor-default" onClick={() => setAuthMode(null)} />
          <div className="relative bg-zinc-950 border border-white/10 p-8 rounded-3xl w-full max-w-md shadow-2xl animate-fade-in">
            <button className="absolute top-4 right-4 text-zinc-500 hover:text-white" onClick={() => setAuthMode(null)}>✕</button>
            <div className="text-center mb-8">
              <h2 className="text-2xl font-black mb-2">{authMode === "login" ? "Tekrar Hoş Geldin" : "Hemen Başla"}</h2>
              <p className="text-zinc-400 text-sm">Giriş yap ve öğrenmeye devam et.</p>
            </div>
            <Auth initialMode={authMode} onAuthenticated={onAuthenticated} />
          </div>
        </div>
      )}
    </main>
  );
}
