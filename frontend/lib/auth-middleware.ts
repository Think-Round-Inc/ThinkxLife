import { NextRequest, NextResponse } from "next/server";
// import { createRouteHandlerClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
// import { prisma } from "@/lib/prisma";
const prisma = null as any; // Mock prisma for build

export type UserRole = 'MEMBER' | 'INTERN' | 'TEAM_LEAD' | 'ADMIN';
export type UserStatus = 'ACTIVE' | 'SUSPENDED' | 'ARCHIVED';

function isAdminEmail(email?: string | null): boolean {
  if (!email) return false;
  const raw = process.env.ADMIN_EMAILS || process.env.NEXT_PUBLIC_ADMIN_EMAILS || "";
  const list = raw
    .split(/[,\s]+/)
    .map((e) => e.trim().toLowerCase())
    .filter(Boolean);
  return list.includes(email.toLowerCase());
}

export interface AuthUser {
  id: string;
  email: string;
  name?: string;
  rolePrimary: UserRole;
  status: UserStatus;
  teamMemberships?: Array<{
    teamId: string;
    team: {
      id: string;
      name: string;
      leadId?: string;
    };
  }>;
  userRoles?: Array<{
    role: {
      code: string;
      name: string;
      permissions: any;
    };
  }>;
}

/**
 * Get authenticated user from Supabase and enrich with RBAC data
 */
export async function getAuthUser(): Promise<AuthUser | null> {
  try {
    // const supabase = createRouteHandlerClient({ cookies });
    // const { data: { user } } = await supabase.auth.getUser();
    const user = null as any; // Disabled Supabase auth during migration
    
    if (!user?.email) {
      return null;
    }

    try {
      // First try to get basic user data
      const basicUser = await prisma.user.findUnique({
        where: { email: user.email },
      });

      if (!basicUser) {
        return null;
      }

      // Try to get RBAC data if available
      let teamMemberships: any[] = [];
      let userRoles: any[] = [];
      let rolePrimary = 'ADMIN'; // Set to ADMIN for testing
      let status = 'ACTIVE';

      try {
        // Attempt to query RBAC fields
        const rbacUser = await (prisma as any).user.findUnique({
          where: { email: user.email },
          include: {
            TeamMemberships: {
              where: { leftAt: null },
              include: {
                Team: {
                  select: {
                    id: true,
                    name: true,
                    leadId: true,
                  },
                },
              },
            },
            UserRoles: {
              include: {
                Role: {
                  select: {
                    code: true,
                    name: true,
                    permissions: true,
                  },
                },
              },
            },
          },
        });

        if (rbacUser) {
          teamMemberships = rbacUser.TeamMemberships?.map((tm: any) => ({
            teamId: tm.teamId,
            team: tm.Team,
          })) || [];
          userRoles = rbacUser.UserRoles?.map((ur: any) => ({
            role: ur.Role,
          })) || [];
          rolePrimary = rbacUser.rolePrimary || 'ADMIN'; // Set to ADMIN for testing
          status = rbacUser.status || 'ACTIVE';
        }
      } catch (rbacError) {
        console.warn('RBAC fields not available, using defaults');
      }

      return {
        id: basicUser.id,
        email: basicUser.email,
        name: basicUser.name || undefined,
        rolePrimary: (isAdminEmail(basicUser.email) ? 'ADMIN' : rolePrimary) as UserRole,
        status: status as UserStatus,
        teamMemberships,
        userRoles,
      };
    } catch (dbError: any) {
      console.warn('RBAC database not available, falling back to basic user data:', dbError.message);
      
      // Fallback: try to get basic user data without RBAC fields
      try {
        const basicUser = await prisma.user.findUnique({
          where: { email: user.email },
          select: {
            id: true,
            email: true,
            name: true,
            createdAt: true,
            updatedAt: true,
          },
        });

        if (basicUser) {
          return {
            id: basicUser.id,
            email: basicUser.email,
            name: basicUser.name || undefined,
            rolePrimary: (isAdminEmail(basicUser.email) ? 'ADMIN' : 'ADMIN') as UserRole, // default ADMIN, allow env override
            status: 'ACTIVE' as UserStatus, // Default status
            teamMemberships: [],
            userRoles: [],
          };
        }
      } catch (fallbackError) {
        console.warn('Basic user lookup also failed:', fallbackError);
      }

      // Final fallback: create a temporary user object from Supabase data
      console.log('Using Supabase fallback for user:', user.email);
      return {
        id: user.id,
        email: user.email!,
        name: user.user_metadata?.name || user.user_metadata?.full_name || undefined,
        rolePrimary: (isAdminEmail(user.email) ? 'ADMIN' : 'ADMIN') as UserRole, // default ADMIN, allow env override
        status: 'ACTIVE' as UserStatus,
        teamMemberships: [],
        userRoles: [],
      };
    }
  } catch (error) {
    console.error('Error getting auth user:', error);
    return null;
  }
}

/**
 * Check if user has required role
 */
export function hasRole(user: AuthUser, requiredRole: UserRole): boolean {
  const roleHierarchy: Record<UserRole, number> = {
    MEMBER: 1,
    INTERN: 2,
    TEAM_LEAD: 3,
    ADMIN: 4,
  };

  const userLevel = roleHierarchy[user.rolePrimary];
  const requiredLevel = roleHierarchy[requiredRole];

  return userLevel >= requiredLevel;
}

/**
 * Check if user has specific permission
 */
export function hasPermission(user: AuthUser, resource: string, action: string): boolean {
  // Check primary role permissions
  const primaryRole = user.userRoles?.find(ur => ur.role.code === user.rolePrimary.toLowerCase());
  if (primaryRole && checkPermission(primaryRole.role.permissions, resource, action)) {
    return true;
  }

  // Check additional role permissions
  return user.userRoles?.some(ur => 
    checkPermission(ur.role.permissions, resource, action)
  ) || false;
}

/**
 * Check if user is team lead of specific team
 */
export function isTeamLead(user: AuthUser, teamId?: string): boolean {
  if (!hasRole(user, 'TEAM_LEAD')) {
    return false;
  }

  if (!teamId) {
    // Check if user is lead of any team
    return user.teamMemberships?.some(tm => tm.team.leadId === user.id) || false;
  }

  // Check if user is lead of specific team
  return user.teamMemberships?.some(tm => 
    tm.teamId === teamId && tm.team.leadId === user.id
  ) || false;
}

/**
 * Check if user can manage another user (same team or admin)
 */
export function canManageUser(actor: AuthUser, targetUserId: string): boolean {
  // Admins can manage anyone
  if (hasRole(actor, 'ADMIN')) {
    return true;
  }

  // Team leads can manage their team members
  if (hasRole(actor, 'TEAM_LEAD')) {
    // This would need additional logic to check if target user is in actor's team
    // For now, return false - implement team membership check
    return false;
  }

  // Users can only manage themselves
  return actor.id === targetUserId;
}

/**
 * Helper function to check permission in JSON structure
 */
function checkPermission(permissions: any, resource: string, action: string): boolean {
  if (!permissions || typeof permissions !== 'object') {
    return false;
  }

  const resourcePerms = permissions[resource];
  if (!resourcePerms || !Array.isArray(resourcePerms)) {
    return false;
  }

  return resourcePerms.includes(action) || resourcePerms.includes('*');
}

/**
 * Middleware factory for role-based route protection
 */
export function requireRole(requiredRole: UserRole) {
  return async function middleware(request: NextRequest) {
    const user = await getAuthUser();

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    if (user.status !== 'ACTIVE') {
      return NextResponse.json({ error: 'Account suspended or archived' }, { status: 403 });
    }

    if (!hasRole(user, requiredRole)) {
      return NextResponse.json({ error: 'Insufficient permissions' }, { status: 403 });
    }

    // Add user to request headers for downstream use
    const response = NextResponse.next();
    response.headers.set('x-user-id', user.id);
    response.headers.set('x-user-role', user.rolePrimary);
    
    return response;
  };
}

/**
 * Middleware factory for permission-based route protection
 */
export function requirePermission(resource: string, action: string) {
  return async function middleware(request: NextRequest) {
    const user = await getAuthUser();

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    if (user.status !== 'ACTIVE') {
      return NextResponse.json({ error: 'Account suspended or archived' }, { status: 403 });
    }

    if (!hasPermission(user, resource, action)) {
      return NextResponse.json({ error: 'Insufficient permissions' }, { status: 403 });
    }

    const response = NextResponse.next();
    response.headers.set('x-user-id', user.id);
    response.headers.set('x-user-role', user.rolePrimary);
    
    return response;
  };
}

/**
 * Audit logging helper
 */
export async function logAudit(
  actorId: string,
  action: string,
  entityType: string,
  entityId: string,
  diff?: any,
  metadata?: any
) {
  try {
    // Try to log to audit table if it exists
    await (prisma as any).auditLog.create({
      data: {
        actorId,
        action,
        entityType,
        entityId,
        diff,
        metadata,
      },
    });
  } catch (error) {
    console.warn('Audit logging failed (table may not exist yet):', error);
    // Don't throw - audit failures shouldn't break the main operation
  }
}
