'use client';

import { useKeycloak } from '@/contexts/KeycloakContext';

/**
 * Custom hook for authentication
 * Provides easy access to Keycloak authentication state and methods
 */
export const useAuth = () => {
  const {
    authenticated,
    loading,
    user,
    login,
    logout,
    register,
    getToken,
    hasRole,
    hasAnyRole,
  } = useKeycloak();

  return {
    isAuthenticated: authenticated,
    isLoading: loading,
    user,
    login,
    logout,
    register,
    getToken,
    hasRole,
    hasAnyRole,
  };
};

