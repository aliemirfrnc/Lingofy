"use client";
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function ConsoleSidebar() {
  const pathname = usePathname();
  const menus = [
    { name: 'Command Center', path: '/console' },
    { name: 'Users & Growth', path: '/console/users' },
    { name: 'AI Intelligence', path: '/console/ai' },
    { name: 'Product Analytics', path: '/console/analytics' },
    { name: 'Workflows', path: '/console/workflows' },
    { name: 'DevOps & Security', path: '/console/devops' },
  ];

  return (
    <aside className="w-64 border-r border-neutral-800 bg-neutral-950 flex flex-col hidden md:flex">
      <div className="h-16 flex items-center px-6 border-b border-neutral-800">
         <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
           Lingofy Ops
         </span>
      </div>
      <nav className="flex-1 p-4 space-y-1">
         {menus.map((m, i) => {
            const isActive = pathname === m.path;
            return (
              <Link 
                key={i} 
                href={m.path} 
                className={`block px-3 py-2 text-sm rounded-md transition ${isActive ? 'bg-neutral-800 text-white' : 'text-neutral-400 hover:text-white hover:bg-neutral-900'}`}
              >
                 {m.name}
              </Link>
            )
         })}
      </nav>
      <div className="p-4 border-t border-neutral-800 text-xs text-neutral-500">
         Operations Console v4.0
      </div>
    </aside>
  );
}
