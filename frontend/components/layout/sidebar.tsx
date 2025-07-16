'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useAuth } from '@/lib/auth';
import {
  LayoutDashboard,
  Mic,
  FileText,
  BarChart3,
  Users,
  Settings,
} from 'lucide-react';

const navigation = [
  {
    name: 'ダッシュボード',
    href: '/dashboard',
    icon: LayoutDashboard,
    roles: ['counselor', 'manager', 'admin'],
  },
  {
    name: 'カウンセリング録音',
    href: '/recording',
    icon: Mic,
    roles: ['counselor', 'manager', 'admin'],
  },
  {
    name: 'セッション一覧',
    href: '/sessions',
    icon: FileText,
    roles: ['counselor', 'manager', 'admin'],
  },
  {
    name: '分析結果',
    href: '/analysis',
    icon: BarChart3,
    roles: ['counselor', 'manager', 'admin'],
  },
  {
    name: 'ユーザー管理',
    href: '/users',
    icon: Users,
    roles: ['manager', 'admin'],
  },
  {
    name: '設定',
    href: '/settings',
    icon: Settings,
    roles: ['admin'],
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user } = useAuth();

  const filteredNavigation = navigation.filter(item => 
    user?.role && item.roles.includes(user.role)
  );

  return (
    <div className="flex h-full w-64 flex-col bg-gray-50 border-r">
      <nav className="flex-1 space-y-1 px-2 py-4">
        {filteredNavigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors',
                isActive
                  ? 'bg-blue-100 text-blue-900'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              )}
            >
              <item.icon
                className={cn(
                  'mr-3 h-5 w-5 flex-shrink-0',
                  isActive ? 'text-blue-500' : 'text-gray-400'
                )}
              />
              {item.name}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}