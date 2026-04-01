import Keycloak from 'keycloak-js';

// Keycloak configuration
const keycloakConfig = {
  url: process.env.NEXT_PUBLIC_KEYCLOAK_URL || 'http://localhost:8080',
  realm: process.env.NEXT_PUBLIC_KEYCLOAK_REALM || 'thinklife',
  clientId: process.env.NEXT_PUBLIC_KEYCLOAK_CLIENT_ID || 'thinklife-frontend',
};

// Initialize Keycloak instance
let keycloakInstance: Keycloak | null = null;

const createKeycloakInstance = (): Keycloak | null => {
  if (typeof window === 'undefined') {
    return null;
  }
  
  if (keycloakInstance) {
    return keycloakInstance;
  }
  
  try {
    keycloakInstance = new Keycloak(keycloakConfig);
    return keycloakInstance;
  } catch (error) {
    console.error('Failed to create Keycloak instance:', error);
    return null;
  }
};

// Create initial instance
createKeycloakInstance();

// Export the instance (will be null on server side)
export const keycloak: Keycloak | null = keycloakInstance;

// Keycloak initialization options
export const keycloakInitOptions = {
  onLoad: 'check-sso' as const, // Check SSO on load, don't redirect if not authenticated
  checkLoginIframe: false, // Disable iframe check for better performance
  pkceMethod: 'S256' as const, // Use PKCE for better security
  enableLogging: process.env.NODE_ENV === 'development',
};

// Track initialization state
let initPromise: Promise<boolean> | null = null;
let isInitializing = false;
let isInitialized = false; // Track if init() was successfully called

// Initialize Keycloak
export const initKeycloak = async (): Promise<boolean> => {
  // Use instance variable for internal operations
  const instance = keycloakInstance || keycloak;
  
  if (!instance) {
    // Try to create instance if it doesn't exist
    const newInstance = createKeycloakInstance();
    if (!newInstance) {
      console.warn('Keycloak is not available on server side');
      return false;
    }
  }

  const currentInstance = keycloakInstance || keycloak;
  if (!currentInstance) {
    return false;
  }

  // If already initialized, return the result
  if (isInitialized && currentInstance.authenticated !== undefined) {
    return currentInstance.authenticated;
  }

  // If currently initializing, wait for that promise
  if (initPromise) {
    return initPromise;
  }

  // Check if Keycloak URL is configured
  const keycloakUrl = process.env.NEXT_PUBLIC_KEYCLOAK_URL;
  if (!keycloakUrl) {
    // If not configured at all, don't try to initialize
    console.log('Keycloak not configured. Please set NEXT_PUBLIC_KEYCLOAK_URL in your .env.local file.');
    return false;
  }
  
  // Note: localhost:8080 is a valid Keycloak URL for local development
  // We should still try to initialize it

  // Start initialization
  isInitializing = true;
  initPromise = (async () => {
    try {
      const authenticated = await currentInstance.init(keycloakInitOptions);
      isInitializing = false;
      isInitialized = true; // Mark as successfully initialized
      return authenticated;
    } catch (error) {
      // Don't block page load if Keycloak fails - just log the error
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.warn('Keycloak initialization failed (non-blocking):', errorMessage);
      console.warn('Keycloak URL:', keycloakUrl);
      console.warn('This might be normal if Keycloak server is not running. Login will still work when user clicks login.');
      isInitializing = false;
      isInitialized = false;
      initPromise = null; // Reset so we can try again
      return false;
    }
  })();

  return initPromise;
};

// Ensure Keycloak is initialized (for login)
export const ensureKeycloakInitialized = async (): Promise<boolean> => {
  // Re-create keycloak instance if it's null (might have been cleared)
  if (!keycloakInstance && typeof window !== 'undefined') {
    createKeycloakInstance();
  }

  if (!keycloakInstance) {
    return false;
  }

  // If already initialized successfully, return immediately
  if (isInitialized && keycloakInstance.authenticated !== undefined) {
    return true;
  }

  // Wait for initialization to complete
  const result = await initKeycloak();
  
  // Return true only if initialization succeeded AND instance is valid
  return result && isInitialized && keycloakInstance !== null;
};

// Helper function to safely check if keycloak is valid and has login method
const isKeycloakValid = (): boolean => {
  // Always check the instance, not the exported const
  const instance = keycloakInstance || keycloak;
  // Must be initialized and have the login function
  return isInitialized && instance !== null && instance !== undefined && typeof instance.login === 'function';
};

// Login function
export const login = async (redirectUri?: string) => {
  // Ensure instance exists
  const instance = keycloakInstance || keycloak;
  if (!instance) {
    // Try to create instance
    const newInstance = createKeycloakInstance();
    if (!newInstance) {
      console.warn('Keycloak is not available. Please configure NEXT_PUBLIC_KEYCLOAK_URL in your .env.local file.');
      return;
    }
  }
  
  // Get current instance
  const currentInstance = keycloakInstance || keycloak;
  if (!currentInstance) {
    console.warn('Keycloak instance could not be created.');
    return;
  }
  
  // Store the final destination in localStorage for the callback page
  const finalDestination = redirectUri || window.location.origin;
  if (typeof window !== 'undefined') {
    localStorage.setItem('keycloak_redirect_uri', finalDestination);
  }
  
  // Always use the callback page as the Keycloak redirect URI
  const keycloakRedirectUri = `${window.location.origin}/auth/callback`;
  
  const options: Keycloak.KeycloakLoginOptions = {
    redirectUri: keycloakRedirectUri,
  };
  
  try {
    // Ensure Keycloak is fully initialized before attempting login
    const initResult = await ensureKeycloakInitialized();
    
    // Re-validate keycloak instance after async operations
    if (!isKeycloakValid()) {
      const keycloakUrl = process.env.NEXT_PUBLIC_KEYCLOAK_URL;
      if (!keycloakUrl) {
        console.error('Keycloak is not configured. Please set NEXT_PUBLIC_KEYCLOAK_URL in your .env.local file.');
        return;
      }
      console.error('Keycloak instance is invalid. Please check if Keycloak server is running at:', keycloakUrl);
      return;
    }
    
    if (!initResult) {
      // If initialization failed, check if Keycloak URL is configured
      const keycloakUrl = process.env.NEXT_PUBLIC_KEYCLOAK_URL;
      if (!keycloakUrl) {
        console.error('Keycloak is not configured. Please set NEXT_PUBLIC_KEYCLOAK_URL in your .env.local file.');
        return;
      }
      
      // If URL is configured but init failed, it might be a connection issue
      console.error('Failed to initialize Keycloak. Please check if Keycloak server is running at:', keycloakUrl);
      console.error('Login cannot proceed without successful initialization. Please ensure Keycloak server is accessible.');
      // DO NOT try to login if not initialized - this will cause errors
      return;
    }
    
    // Get the current instance
    const validInstance = keycloakInstance || keycloak;
    
    // Final comprehensive validation before calling login
    if (!validInstance) {
      console.error('Keycloak instance is null');
      return;
    }
    
    if (!isInitialized) {
      console.error('Keycloak was not successfully initialized (flag check)');
      return;
    }
    
    if (typeof validInstance.login !== 'function') {
      console.error('Keycloak instance is missing login method');
      return;
    }
    
    // Check if already authenticated
    if (validInstance.authenticated) {
      // Already authenticated, redirect to final destination
      if (typeof window !== 'undefined') {
        window.location.href = finalDestination;
      }
      return;
    }
    
    // Now that Keycloak is initialized and validated, trigger login
    console.log('Calling Keycloak login with options:', options);
    validInstance.login(options);
  } catch (error) {
    console.error('Login failed:', error);
    console.error('Keycloak initialization status:', isInitialized);
    console.error('Keycloak instance exists:', keycloakInstance !== null);
    
    // DO NOT retry login if it failed - this will just cause more errors
    // User should refresh the page if this happens
    console.error('Please refresh the page and try again. If the problem persists, Keycloak server may not be accessible.');
  }
};

// Logout function
export const logout = (redirectUri?: string) => {
  const instance = keycloakInstance || keycloak;
  if (!isKeycloakValid() || !instance) return;
  
  const options: Keycloak.KeycloakLogoutOptions = {};
  if (redirectUri) {
    options.redirectUri = redirectUri;
  }
  
  instance.logout(options);
};

// Register function
export const register = (redirectUri?: string) => {
  const instance = keycloakInstance || keycloak;
  if (!isKeycloakValid() || !instance) return;
  
  const options: Keycloak.KeycloakLoginOptions = {
    action: 'REGISTER',
  };
  if (redirectUri) {
    options.redirectUri = redirectUri;
  }
  
  instance.login(options);
};

// Get user token
export const getToken = async (): Promise<string | undefined> => {
  const instance = keycloakInstance || keycloak;
  if (!instance) return undefined;
  
  try {
    // Refresh token if needed
    await instance.updateToken(30); // Refresh if token expires in less than 30 seconds
    return instance.token;
  } catch (error) {
    console.error('Failed to get token:', error);
    return undefined;
  }
};

// Get user info
export const getUserInfo = () => {
  const instance = keycloakInstance || keycloak;
  if (!instance || !instance.authenticated) return null;
  
  return {
    id: instance.tokenParsed?.sub,
    email: instance.tokenParsed?.email,
    name: instance.tokenParsed?.name,
    firstName: instance.tokenParsed?.given_name,
    lastName: instance.tokenParsed?.family_name,
    username: instance.tokenParsed?.preferred_username,
    roles: instance.realmAccess?.roles || [],
    emailVerified: instance.tokenParsed?.email_verified,
  };
};

// Check if user is authenticated
export const isAuthenticated = (): boolean => {
  const instance = keycloakInstance || keycloak;
  return instance?.authenticated ?? false;
};

// Check if user has role
export const hasRole = (role: string): boolean => {
  const instance = keycloakInstance || keycloak;
  if (!instance || !instance.authenticated) return false;
  return instance.hasRealmRole(role);
};

// Check if user has any of the specified roles
export const hasAnyRole = (roles: string[]): boolean => {
  const instance = keycloakInstance || keycloak;
  if (!instance || !instance.authenticated) return false;
  return roles.some(role => instance.hasRealmRole(role));
};

