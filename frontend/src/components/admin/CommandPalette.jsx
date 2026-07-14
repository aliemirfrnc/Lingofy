"use client";
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/navigation';

export default function CommandPalette({ isOpen, onClose }) {
    const [query, setQuery] = useState('');
    const router = useRouter();

    const actions = [
        { id: 1, label: 'Go to Dashboard', action: () => router.push('/admin') },
        { id: 2, label: 'Search Users', action: () => router.push('/admin/users') },
        { id: 3, label: 'View Audit Logs', action: () => router.push('/admin/audit') },
        { id: 4, label: 'System Health', action: () => router.push('/admin/system') }
    ];

    const filteredActions = query === '' 
        ? actions 
        : actions.filter(action => action.label.toLowerCase().includes(query.toLowerCase()));

    // Escape to close
    useEffect(() => {
        const handleKeyDown = (e) => {
            if (e.key === 'Escape') {
                onClose();
            }
        };
        if (isOpen) {
            window.addEventListener('keydown', handleKeyDown);
        }
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [isOpen, onClose]);

    if (!isOpen) return null;

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh] bg-black/50 backdrop-blur-sm" onClick={onClose}>
                <motion.div 
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    transition={{ duration: 0.15 }}
                    className="w-full max-w-xl bg-[#09090b] border border-[#27272a] rounded-xl shadow-2xl overflow-hidden"
                    onClick={(e) => e.stopPropagation()}
                >
                    <div className="flex items-center px-4 py-3 border-b border-[#27272a]">
                        <svg className="w-5 h-5 text-[#a1a1aa] mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                        </svg>
                        <input
                            type="text"
                            autoFocus
                            className="w-full bg-transparent border-none outline-none text-[#f4f4f5] placeholder-[#a1a1aa] text-lg"
                            placeholder="Type a command or search..."
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                        />
                        <button onClick={onClose} className="px-2 py-1 text-xs text-[#a1a1aa] bg-[#27272a] rounded">ESC</button>
                    </div>
                    
                    <div className="max-h-[60vh] overflow-y-auto py-2">
                        {filteredActions.length > 0 ? (
                            <ul className="px-2">
                                {filteredActions.map((action, index) => (
                                    <li key={action.id}>
                                        <button 
                                            onClick={() => {
                                                action.action();
                                                onClose();
                                            }}
                                            className="w-full text-left px-3 py-3 text-sm text-[#f4f4f5] rounded-md hover:bg-[#27272a] hover:text-white transition-colors flex items-center justify-between"
                                        >
                                            <span>{action.label}</span>
                                            <span className="text-xs text-[#a1a1aa]">Jump to</span>
                                        </button>
                                    </li>
                                ))}
                            </ul>
                        ) : (
                            <div className="px-4 py-8 text-center text-[#a1a1aa] text-sm">
                                No results found for &quot;{query}&quot;
                            </div>
                        )}
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
}
