import React from 'react';

export function Card({ title, description, children, className = "" }) {
    return (
        <div className={`bg-[#09090b] border border-[#27272a] rounded-xl overflow-hidden ${className}`}>
            {(title || description) && (
                <div className="px-6 py-5 border-b border-[#27272a]">
                    {title && <h3 className="text-lg font-medium text-[#f4f4f5]">{title}</h3>}
                    {description && <p className="mt-1 text-sm text-[#a1a1aa]">{description}</p>}
                </div>
            )}
            <div className="p-6">
                {children}
            </div>
        </div>
    );
}

export function StatCard({ title, value, trend, trendValue, icon }) {
    return (
        <div className="bg-[#09090b] border border-[#27272a] rounded-xl p-6 flex items-start justify-between">
            <div>
                <p className="text-sm font-medium text-[#a1a1aa]">{title}</p>
                <h4 className="text-3xl font-bold text-[#f4f4f5] mt-2">{value}</h4>
                {trend && (
                    <div className="flex items-center mt-2">
                        <span className={`text-xs font-medium ${trend === 'up' ? 'text-emerald-500' : 'text-rose-500'}`}>
                            {trend === 'up' ? '↑' : '↓'} {trendValue}
                        </span>
                        <span className="text-xs text-[#a1a1aa] ml-2">vs last month</span>
                    </div>
                )}
            </div>
            {icon && (
                <div className="p-3 bg-[#18181b] rounded-lg text-[#a1a1aa]">
                    {icon}
                </div>
            )}
        </div>
    );
}
