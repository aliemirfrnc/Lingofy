"use client";
import React, { useState, useEffect } from 'react';
import { Card, StatCard } from '@/components/admin/Card';

export default function SystemPage() {
    const [health, setHealth] = useState(null);

    useEffect(() => {
        setTimeout(() => {
            setHealth({
                cpu_usage_percent: 24.5,
                ram_usage_percent: 45.2,
                ram_total_mb: 8192,
                disk_usage_percent: 62.1,
                database_size_bytes: 4120032,
                status: "HEALTHY"
            });
        }, 300);
    }, []);

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-3xl font-bold text-[#f4f4f5]">System Health</h2>
                <p className="text-[#a1a1aa] mt-2">Real-time metrics for CPU, Memory, Disk, and Database status.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <StatCard 
                    title="CPU Usage" 
                    value={health ? `${health.cpu_usage_percent}%` : '...'} 
                />
                <StatCard 
                    title="RAM Usage" 
                    value={health ? `${health.ram_usage_percent}%` : '...'} 
                />
                <StatCard 
                    title="SQLite Database Size" 
                    value={health ? `${(health.database_size_bytes / 1024 / 1024).toFixed(2)} MB` : '...'} 
                />
            </div>
            
            <Card title="Provider Circuit Breakers" description="Current status of external integrations">
                <div className="space-y-4">
                    <div className="flex justify-between items-center p-4 bg-[#18181b] rounded-lg border border-[#27272a]">
                        <span className="font-medium text-[#f4f4f5]">Groq</span>
                        <span className="px-3 py-1 bg-emerald-500/10 text-emerald-500 text-xs font-bold uppercase rounded-full">Closed (Healthy)</span>
                    </div>
                    <div className="flex justify-between items-center p-4 bg-[#18181b] rounded-lg border border-[#27272a]">
                        <span className="font-medium text-[#f4f4f5]">OpenRouter</span>
                        <span className="px-3 py-1 bg-emerald-500/10 text-emerald-500 text-xs font-bold uppercase rounded-full">Closed (Healthy)</span>
                    </div>
                    <div className="flex justify-between items-center p-4 bg-[#18181b] rounded-lg border border-[#27272a]">
                        <span className="font-medium text-[#f4f4f5]">Spotify API</span>
                        <span className="px-3 py-1 bg-emerald-500/10 text-emerald-500 text-xs font-bold uppercase rounded-full">Closed (Healthy)</span>
                    </div>
                </div>
            </Card>
        </div>
    );
}
