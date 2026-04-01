'use client';

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import type Keycloak from 'keycloak-js';
import { keycloak, initKeycloak, login, logout, register, getToken, getUserInfo, isAuthenticated, hasRole, hasAnyRole } from '../lib/keycloak';

interface KeycloakContextType {
  keycloak: Keycloak | null;
  authenticated: boolean;
  loading: boolean;
  user: ReturnType<typeof getUserInfo>;
  login: (redirectUri?: string) => void;
  logout: (redirectUri?: string) => void;
  register: (redirectUri?: string) => void;
  getToken: () => Promise<string | undefined>;
  hasRole: (role: string) => boolean;
  hasAnyRole: (roles: string[]) => boolean;
}

const KeycloakContext = createContext<KeycloakContextType | undefined>(undefined);

export const useKeycloak = () => {
  const context = useContext(KeycloakContext);
  if (!context) {
    throw new Error('useKeycloak must be used within a KeycloakProvider');
  }
  return context;
};

interface KeycloakProviderProps {
  children: ReactNode;
}

export const KeycloakProvider: React.FC<KeycloakProviderProps> = ({ children }) => {
  const [authenticated, setAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<ReturnType<typeof getUserInfo>>(null);

  useEffect(() => {
    if (typeof window === 'undefined') {
      setLoading(false);
      return;
    }

    const initializeAuth = async () => {
      try {
        // Initialize Keycloak silently - don't block if it fails
        const isAuth = await initKeycloak();
        setAuthenticated(isAuth);
        
        if (isAuth) {
          setUser(getUserInfo());
        }

        // Listen for token updates only if keycloak is available
        const keycloakInstance = keycloak as Keycloak | null;
        if (keycloakInstance) {
          keycloakInstance.onTokenExpired = () => {
            keycloakInstance.updateToken(30).catch((error) => {
              console.warn('Failed to refresh token:', error);
              setAuthenticated(false);
              setUser(null);
            });
          };

          keycloakInstance.onAuthSuccess = () => {
            setAuthenticated(true);
            setUser(getUserInfo());
          };

          keycloakInstance.onAuthError = () => {
            setAuthenticated(false);
            setUser(null);
          };

          keycloakInstance.onAuthLogout = () => {
            setAuthenticated(false);
            setUser(null);
          };
        }
      } catch (error) {
        // Don't block page load - just log warning
        console.warn('Keycloak initialization error (non-blocking):', error);
        setAuthenticated(false);
        setUser(null);
      } finally {
        // Always set loading to false so page can render
        setLoading(false);
      }
    };

    // Initialize auth but don't block page rendering
    initializeAuth();
  }, []);

  const handleLogin = async (redirectUri?: string) => {
    await login(redirectUri || window.location.href);
  };

  const handleLogout = (redirectUri?: string) => {
    logout(redirectUri || window.location.origin);
  };

  const handleRegister = (redirectUri?: string) => {
    register(redirectUri || window.location.href);
  };

  const handleGetToken = async (): Promise<string | undefined> => {
    return await getToken();
  };

  const value: KeycloakContextType = {
    keycloak,
    authenticated,
    loading,
    user,
    login: handleLogin,
    logout: handleLogout,
    register: handleRegister,
    getToken: handleGetToken,
    hasRole,
    hasAnyRole,
  };

  return (
    <KeycloakContext.Provider value={value}>
      {children}
    </KeycloakContext.Provider>
  );
};

