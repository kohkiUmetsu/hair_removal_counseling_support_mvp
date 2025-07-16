'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: 'counselor' | 'manager' | 'admin';
  fallbackUrl?: string;
}

export function ProtectedRoute({ 
  children, 
  requiredRole,
  fallbackUrl = '/login' 
}: ProtectedRouteProps) {
  const { user, loading, isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      if (!isAuthenticated) {
        router.push(fallbackUrl);
        return;
      }

      if (requiredRole && user?.role) {
        const roleHierarchy = { admin: 3, manager: 2, counselor: 1 };
        const userLevel = roleHierarchy[user.role];
        const requiredLevel = roleHierarchy[requiredRole];

        if (userLevel < requiredLevel) {
          router.push('/dashboard'); // Redirect to dashboard if insufficient permissions
          return;
        }
      }
    }
  }, [loading, isAuthenticated, user, requiredRole, router, fallbackUrl]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  if (requiredRole && user?.role) {
    const roleHierarchy = { admin: 3, manager: 2, counselor: 1 };
    const userLevel = roleHierarchy[user.role];
    const requiredLevel = roleHierarchy[requiredRole];

    if (userLevel < requiredLevel) {
      return null;
    }
  }

  return <>{children}</>;
}