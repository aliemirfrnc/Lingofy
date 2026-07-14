import ConsoleSidebar from '@/components/console/layout/ConsoleSidebar';
import SmartPalette from '@/components/console/layout/SmartPalette';

export default function ConsoleLayout({ children }) {
  return (
    <div className="flex h-screen bg-neutral-950 text-neutral-100 overflow-hidden font-sans">
      <ConsoleSidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <header className="h-16 border-b border-neutral-800 flex items-center px-6 justify-between bg-neutral-950/80 backdrop-blur-md">
           <div className="flex items-center gap-4">
              <h2 className="text-sm font-medium text-neutral-400">Operations Console v4</h2>
           </div>
           <div className="flex items-center gap-4">
              <button className="text-xs px-3 py-1.5 bg-neutral-900 rounded-md border border-neutral-800 hover:bg-neutral-800 transition flex items-center gap-2 text-neutral-400">
                 <span className="font-mono text-[10px] bg-neutral-800 px-1 rounded">Ctrl K</span>
                 <span>Search</span>
              </button>
              <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-sm font-bold shadow-lg shadow-indigo-900/20">
                 A
              </div>
           </div>
        </header>
        <main className="flex-1 overflow-y-auto p-6 bg-neutral-900/30">
          {children}
        </main>
      </div>
      <SmartPalette />
    </div>
  );
}
