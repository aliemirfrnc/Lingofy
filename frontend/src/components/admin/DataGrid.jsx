"use client";
import React from 'react';
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
} from '@tanstack/react-table';

export function DataGrid({ data, columns, onNextPage, hasMore, isLoading }) {
    const table = useReactTable({
        data,
        columns,
        getCoreRowModel: getCoreRowModel(),
    });

    return (
        <div className="w-full">
            <div className="border border-[#27272a] rounded-xl overflow-hidden bg-[#09090b]">
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left">
                        <thead className="text-xs text-[#a1a1aa] uppercase bg-[#18181b] border-b border-[#27272a]">
                            {table.getHeaderGroups().map(headerGroup => (
                                <tr key={headerGroup.id}>
                                    {headerGroup.headers.map(header => (
                                        <th key={header.id} className="px-6 py-4 font-medium tracking-wider">
                                            {header.isPlaceholder
                                                ? null
                                                : flexRender(
                                                    header.column.columnDef.header,
                                                    header.getContext()
                                                )}
                                        </th>
                                    ))}
                                </tr>
                            ))}
                        </thead>
                        <tbody>
                            {table.getRowModel().rows.map(row => (
                                <tr key={row.id} className="border-b border-[#27272a] hover:bg-[#18181b]/50 transition-colors">
                                    {row.getVisibleCells().map(cell => (
                                        <td key={cell.id} className="px-6 py-4 whitespace-nowrap text-[#f4f4f5]">
                                            {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div className="mt-4 flex items-center justify-between">
                <div className="text-sm text-[#a1a1aa]">
                    Showing <span className="font-medium text-white">{data.length}</span> rows
                </div>
                {hasMore && (
                    <button
                        onClick={onNextPage}
                        disabled={isLoading}
                        className="px-4 py-2 text-sm font-medium text-white bg-[#27272a] rounded-lg hover:bg-[#3f3f46] disabled:opacity-50 transition-colors"
                    >
                        {isLoading ? 'Loading...' : 'Load More'}
                    </button>
                )}
            </div>
        </div>
    );
}
