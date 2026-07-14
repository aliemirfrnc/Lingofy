"use client";
import React, { useState, useEffect } from 'react';
import { DataGrid } from '@/components/admin/DataGrid';

export default function UsersPage() {
    const [data, setData] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    // Mock data generation for TanStack Table demonstration
    useEffect(() => {
        setIsLoading(true);
        setTimeout(() => {
            const mockUsers = Array.from({ length: 15 }).map((_, i) => ({
                id: 1000 - i,
                email: `user${1000 - i}@example.com`,
                role: i === 0 ? 'ADMIN' : 'USER',
                created_at: new Date(Date.now() - i * 86400000).toLocaleDateString()
            }));
            setData(mockUsers);
            setIsLoading(false);
        }, 500);
    }, []);

    const columns = [
        { header: 'ID', accessorKey: 'id' },
        { header: 'Email', accessorKey: 'email' },
        { 
            header: 'Role', 
            accessorKey: 'role',
            cell: info => (
                <span className={`px-2 py-1 text-xs rounded-full font-medium ${
                    info.getValue() === 'ADMIN' ? 'bg-indigo-500/10 text-indigo-400' : 'bg-[#27272a] text-[#a1a1aa]'
                }`}>
                    {info.getValue()}
                </span>
            )
        },
        { header: 'Joined', accessorKey: 'created_at' },
        {
            id: 'actions',
            header: '',
            cell: () => (
                <button className="text-[#a1a1aa] hover:text-white transition-colors">
                    Manage
                </button>
            )
        }
    ];

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-3xl font-bold text-[#f4f4f5]">User Management</h2>
                <p className="text-[#a1a1aa] mt-2">Manage all registered accounts, subscriptions, and profile states.</p>
            </div>

            <DataGrid 
                data={data} 
                columns={columns} 
                isLoading={isLoading} 
                hasMore={true}
                onNextPage={() => {}}
            />
        </div>
    );
}
