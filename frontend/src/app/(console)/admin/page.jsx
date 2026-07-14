"use client";
import React, { useEffect, useState } from 'react';
import { Card, StatCard } from '@/components/admin/Card';

export default function AdminDashboard() {
    const [kpis, setKpis] = useState(null);

    useEffect(() => {
        // Fetch real data from our new v1 API
        // For demonstration, we'll simulate the load
        setTimeout(() => {
            setKpis({
                dau: 1250,
                wau: 8400,
                mau: 24000,
                mrr: 5400.0,
                premium_users: 540,
                ai_cost_today: 12.50
            });
        }, 500);
    }, []);

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-3xl font-bold text-[#f4f4f5]">Platform Operations</h2>
                <button className="px-4 py-2 bg-emerald-600 text-white font-medium rounded-lg hover:bg-emerald-700 transition-colors">
                    Export Report
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard 
                    title="Monthly Recurring Revenue" 
                    value={kpis ? `$${kpis.mrr.toLocaleString()}` : '...'} 
                    trend="up" 
                    trendValue="12.5%" 
                />
                <StatCard 
                    title="Daily Active Users" 
                    value={kpis ? kpis.dau.toLocaleString() : '...'} 
                    trend="up" 
                    trendValue="4.2%" 
                />
                <StatCard 
                    title="Premium Subscribers" 
                    value={kpis ? kpis.premium_users.toLocaleString() : '...'} 
                    trend="up" 
                    trendValue="8.1%" 
                />
                <StatCard 
                    title="AI Cost Today" 
                    value={kpis ? `$${kpis.ai_cost_today.toFixed(2)}` : '...'} 
                    trend="down" 
                    trendValue="2.4%" 
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <Card title="Revenue Chart" className="lg:col-span-2">
                    <div className="h-64 flex items-center justify-center text-[#a1a1aa] border-2 border-dashed border-[#27272a] rounded-lg">
                        Recharts implementation goes here
                    </div>
                </Card>
                
                <Card title="Recent System Alerts">
                    <ul className="space-y-4">
                        <li className="flex items-start">
                            <span className="w-2 h-2 mt-1.5 rounded-full bg-rose-500 mr-3 shrink-0"></span>
                            <div>
                                <p className="text-sm font-medium text-[#f4f4f5]">Groq API Latency Spike</p>
                                <p className="text-xs text-[#a1a1aa] mt-0.5">2 hours ago</p>
                            </div>
                        </li>
                        <li className="flex items-start">
                            <span className="w-2 h-2 mt-1.5 rounded-full bg-emerald-500 mr-3 shrink-0"></span>
                            <div>
                                <p className="text-sm font-medium text-[#f4f4f5]">Backup completed successfully</p>
                                <p className="text-xs text-[#a1a1aa] mt-0.5">5 hours ago</p>
                            </div>
                        </li>
                        <li className="flex items-start">
                            <span className="w-2 h-2 mt-1.5 rounded-full bg-amber-500 mr-3 shrink-0"></span>
                            <div>
                                <p className="text-sm font-medium text-[#f4f4f5]">High cache miss ratio</p>
                                <p className="text-xs text-[#a1a1aa] mt-0.5">Yesterday</p>
                            </div>
                        </li>
                    </ul>
                </Card>
            </div>
        </div>
    );
}
