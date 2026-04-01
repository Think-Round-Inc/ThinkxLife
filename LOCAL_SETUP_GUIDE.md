# ThinkLife Local Development Setup Guide

This guide will help you set up and run ThinkxLife locally on your machine. The stack consists of a Python backend (FastAPI), a Next.js frontend, and Keycloak for authentication.

## Prerequisites Installation

### 1. Install Node.js (Required for Frontend)

#### Windows:
1. Visit [nodejs.org](https://nodejs.org/)
2. Download the LTS version (recommended)
3. Run the installer and follow the setup wizard
4. Restart your terminal/command prompt

#### macOS:
```bash
# Option 1: Direct download
# Visit https://nodejs.org/ and download the LTS version

# Option 2: Using Homebrew (if you have it)
brew install node
```

#### Linux (Ubuntu/Debian):
```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 2. Install Python (Required for Backend)

#### Windows:
1. Visit [python.org](https://www.python.org/downloads/)
2. Download Python 3.9 or higher
3. **IMPORTANT**: Check "Add Python to PATH" during installation
4. Run the installer

#### macOS:
```bash
# Using Homebrew
brew install python
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### 3. Install Docker (Required for Keycloak)

Keycloak runs in a Docker container for local development.

#### Windows/macOS:
1. Download and install **Docker Desktop** from [docker.com](https://www.docker.com/products/docker-desktop/).
2. Start Docker Desktop.

#### Linux:
Follow the official instructions to install Docker Engine and Docker Compose for your distribution.

### 4. Install Git (if not already installed)

#### Windows:
Download from [git-scm.com](https://git-scm.com/download/win)

#### macOS:
```bash
brew install git
```

#### Linux:
```bash
sudo apt install git
```

## Project Setup

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd ThinkLife
```

### Step 2: Backend Setup (Python)

#### Navigate to Backend Directory
```bash
cd backend
```

#### Create Python Virtual Environment
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Activate virtual environment (macOS/Linux)
source .venv/bin/activate
```

#### Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Create Backend Environment File
Create a file named `.env` in the `backend/` directory with the following content:

```env
# OpenAI Configuration (REQUIRED)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7

# Vector Database Configuration (OPTIONAL)
# CHROMA_DB_DIR=chroma_db

# Server Configuration
PORT=8000
DEBUG=True

# CORS Settings
CORS_ORIGINS=http://localhost:3000
```

### Step 3: Keycloak Setup (Docker)

We use Docker Compose to run Keycloak and its database locally.

#### Start Keycloak
From the **root** of the project (where `docker-compose.yml` is located):

```bash
docker-compose up -d
```

This will start Keycloak on `http://localhost:8080` and a PostgreSQL database.

*   **Admin Console**: http://localhost:8080
*   **Admin User**: `admin`
*   **Admin Password**: `admin`

Wait a minute for Keycloak to fully start up.

### Step 4: Frontend Setup (Node.js)

#### Navigate to Frontend Directory
```bash
cd frontend
```

#### Install Node.js Dependencies
```bash
npm install
```

#### Create Frontend Environment File
Create a file named `.env.local` in the `frontend/` directory with the following content:

```env
# Next.js Configuration
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Keycloak Configuration
NEXT_PUBLIC_KEYCLOAK_URL=http://localhost:8080
NEXT_PUBLIC_KEYCLOAK_REALM=thinklife
NEXT_PUBLIC_KEYCLOAK_CLIENT_ID=thinklife-frontend
```

*Note: You may need to configure the Realm and Client in Keycloak manually if not pre-configured.*

## Running the Application

You need to run three things: Keycloak (via Docker), the Backend, and the Frontend.

### 1. Start Keycloak (if not running)
```bash
# From project root
docker-compose up -d
```

### 2. Start Backend
Open a new terminal:
```bash
cd backend
# Activate venv if needed: source .venv/bin/activate
python3 main.py
```

### 3. Start Frontend
Open another terminal:
```bash
cd frontend
npm run dev
```

## Accessing the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Keycloak Admin**: http://localhost:8080

## Troubleshooting

### Port Conflicts
If ports 3000, 8000, or 8080 are in use:
- **Frontend**: `npm run dev -- -p 3001`
- **Backend**: Update `PORT` in `.env`
- **Keycloak**: Update ports in `docker-compose.yml`

### Keycloak Connection Issues
- Ensure Docker is running.
- Check logs: `docker-compose logs -f keycloak`
- Ensure `NEXT_PUBLIC_KEYCLOAK_URL` in frontend `.env.local` matches the Docker setup.

### Python Issues
- Ensure you are using the virtual environment (`.venv`).
- Upgrade pip: `pip install --upgrade pip`
