# Keycloak Setup (Local via Docker)

This guide covers setting up Keycloak locally using Docker for ThinkLife authentication.

## Quick Start

If you have the `docker-compose.yml` file in the root or backend directory, simply run:

```bash
docker-compose up -d keycloak
```

This will typically start Keycloak on `http://localhost:8080`.

## Configuration Steps

### 1. Verify Container Status

Check if Keycloak is running:

```bash
docker ps | grep keycloak
```

You should see a container listening on port `8080`.

### 2. Access Admin Console

1.  Open browser: `http://localhost:8080`
2.  Click **"Administration Console"**.
3.  Login with default credentials (check your `docker-compose.yml`):
    *   **Username:** `admin`
    *   **Password:** `admin`

### 3. Create Realm and Client

You need to configure a Realm and a Client for the frontend application.

1.  **Create Realm:**
    *   Hover over "Master" in the top-left dropdown.
    *   Click **"Create Realm"**.
    *   Name: `thinklife` (or your preferred name).
    *   Click **Create**.

2.  **Create Client:**
    *   Go to **Clients** in the left menu.
    *   Click **Create client**.
    *   **Client ID:** `thinklife-frontend`
    *   **Client type:** `OpenID Connect`
    *   Click **Next**.

3.  **Client Settings:**
    *   **Standard Flow:** Enabled (checked).
    *   **Direct Access Grants:** Enabled (checked).
    *   **Valid Redirect URIs:** `http://localhost:3000/*` (allows redirects to frontend).
    *   **Web Origins:** `http://localhost:3000` (allows CORS from frontend).
    *   **Valid Post Logout Redirect URIs:** `http://localhost:3000/*`
    *   Click **Save**.

### 4. Environment Variables

Update your `frontend/.env.local` file to match these settings:

```env
# Keycloak Configuration
NEXT_PUBLIC_KEYCLOAK_URL=http://localhost:8080
NEXT_PUBLIC_KEYCLOAK_REALM=thinklife
NEXT_PUBLIC_KEYCLOAK_CLIENT_ID=thinklife-frontend
```

## Common Commands

**Check logs:**
```bash
docker logs <container_name>
```

**Check env vars inside container:**
```bash
docker exec <container_name> env | grep KEYCLOAK
```

## Troubleshooting

*   **Connection Refused:** Ensure nothing else is using port 8080.
*   **CORS Errors:** Double-check **Web Origins** in the Client settings. It must match your frontend URL exactly (`http://localhost:3000` with no trailing slash).
*   **Infinite Redirect Loop:** Check **Valid Redirect URIs**. Ensure it includes `/*`.
