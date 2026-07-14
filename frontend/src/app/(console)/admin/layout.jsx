"use client";
import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import CommandPalette from '@/components/admin/CommandPalette';

export default function AdminLayout({ children }) {
    const pathname = usePathname();
    const [isCommandPaletteOpen, setCommandPaletteOpen] = useState(false);

    useEffect(() => {
        const handleKeyDown = (e) => {
            if (e.ctrlKey && e.key === 'k') {
                e.preventDefault();
                setCommandPaletteOpen(prev => !prev);
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, []);

    const navItems = [
        { label: 'Dashboard', path: '/admin' },
        { label: 'Users', path: '/admin/users' },
        { label: 'Payments', path: '/admin/payments' },
        { label: 'System Health', path: '/admin/system' },
        { label: 'Audit Logs', path: '/admin/audit' },
    ];

    return (
        <div className="flex h-screen bg-[#09090b] text-[#f4f4f5]">
            <CommandPalette isOpen={isCommandPaletteOpen} onClose={() => setCommandPaletteOpen(false)} />
            
            <aside className="w-64 border-r border-[#27272a] bg-[#09090b] flex flex-col">
                <div className="p-4 border-b border-[#27272a]">
                    <h1 className="text-xl font-bold tracking-tighter">Lingofy Enterprise</h1>
                    <p className="text-xs text-[#a1a1aa] mt-1">Platform Operations</p>
                </div>
                
                <nav className="flex-1 overflow-y-auto py-4">
                    <ul className="space-y-1 px-2">
                        {navItems.map((item) => (
                            <li key={item.path}>
                                <Link href={item.path} 
                                    className={`block px-3 py-2 rounded-md text-sm transition-colors ${
                                        pathname === item.path 
                                            ? 'bg-[#27272a] text-white font-medium' 
                                            : 'text-[#a1a1aa] hover:bg-[#18181b] hover:text-white'
                                    }`}>
                                    {item.label}
                                </Link>
                            </li>
                        ))}
                    </ul>
                </nav>
                
                <div className="p-4 border-t border-[#27272a]">
                    <button 
                        onClick={() => setCommandPaletteOpen(true)}
                        className="w-full flex items-center justify-between px-3 py-2 bg-[#18181b] border border-[#27272a] rounded-md text-sm text-[#a1a1aa] hover:bg-[#27272a] transition-colors"
                    >
                        <span>Search</span>
                        <kbd className="hidden sm:inline-block px-1.5 py-0.5 text-xs font-sans bg-[#27272a] rounded text-[#a1a1aa]">Ctrl+K</kbd>
                    </button>
                </div>
            </aside>
            
            <main className="flex-1 overflow-y-auto">
                <div className="p-8">
                    {children}
                </div>
            </main>
        </div>
    );
}
