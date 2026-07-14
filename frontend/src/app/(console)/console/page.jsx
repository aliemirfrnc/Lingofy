export const metadata = {
  title: 'Dashboard - Lingofy Operations Console',
};

export default function ConsoleDashboard() {
  const kpis = [
    { title: "Active Users (24h)", value: "0" },
    { title: "AI Requests (24h)", value: "0" },
    { title: "System Health", value: "100%", textClass: "text-green-400" },
    { title: "Cost (30d)", value: "$0.00" }
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
         <div>
            <h1 className="text-2xl font-bold text-neutral-100 tracking-tight">Command Center</h1>
            <p className="text-sm text-neutral-400 mt-1">Welcome to Enterprise Operations Console v4.</p>
         </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
         {kpis.map((kpi, i) => (
            <div key={i} className="p-5 rounded-xl border border-neutral-800/60 bg-neutral-900/40 backdrop-blur-sm flex flex-col gap-1">
               <div className="text-sm font-medium text-neutral-400">{kpi.title}</div>
               <div className={`text-2xl font-bold ${kpi.textClass || "text-neutral-100"}`}>{kpi.value}</div>
            </div>
         ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="h-64 rounded-xl border border-neutral-800/60 bg-neutral-900/40 p-5 flex flex-col">
           <h3 className="text-sm font-medium text-neutral-400 mb-4">Operations Timeline</h3>
           <div className="flex-1 flex items-center justify-center text-sm text-neutral-600">
             No recent operations
           </div>
        </div>
        <div className="h-64 rounded-xl border border-neutral-800/60 bg-neutral-900/40 p-5 flex flex-col">
           <h3 className="text-sm font-medium text-neutral-400 mb-4">Live Activity</h3>
           <div className="flex-1 flex items-center justify-center text-sm text-neutral-600">
             Waiting for events...
           </div>
        </div>
      </div>
    </div>
  );
}
