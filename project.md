# LLM Aggregator Platform - Project Plan

## Overview
A web platform that allows users to send prompts to multiple LLM providers simultaneously, compare responses in a tabbed interface, and generate intelligent summaries highlighting overlaps and outliers.

## Architecture

### Tech Stack (Decided)

**Frontend:**
- **Framework:** Vite + React with TypeScript (lightweight, fast dev server)
- **UI Library:** Tailwind CSS for styling (minimal, utility-first)
- **State Management:** React Context API for simple state management
- **HTTP Client:** Fetch API (native, no extra dependencies)
- **Build Tool:** Vite (fast, lightweight, modern)

**Backend:**
- **Runtime:** Python 3.11+ with FastAPI
- **API:** RESTful API
- **Database:** PostgreSQL (always, for all environments)
- **ORM:** SQLAlchemy for database operations
- **Task Queue:** FastAPI background tasks or asyncio for concurrent LLM requests

**Security:**
- **API Key Storage:** 
  - Encrypted at rest using AES-256
  - Environment variables for development
  - Secure vault (HashiCorp Vault, AWS Secrets Manager) for production
- **Encryption Library:** `cryptography` (Python) or `crypto` (Node.js)

**LLM Providers to Support:**
- OpenAI (GPT-3.5, GPT-4, GPT-4 Turbo)
- Anthropic (Claude 3 Opus, Sonnet, Haiku)
- Google (Gemini Pro, Gemini Ultra)
- Optional: Cohere, Mistral AI, Meta Llama (via API)

## Core Features

### 1. API Key Management
- **UI Component:** Settings/Configuration page
- **Features:**
  - Add/edit/delete API keys for different providers
  - Mask keys in UI (show only last 4 characters)
  - Test connection before saving
  - Enable/disable specific providers
- **Backend:**
  - Encrypt keys before storing in database
  - Decrypt only when needed for API calls
  - Never return full keys to frontend

### 2. Prompt Input Interface
- **UI Component:** Main input area with:
  - Large textarea for prompt input
  - Provider selection checkboxes (only enabled providers)
  - Submit button
  - Loading states
- **Backend:**
  - Accept prompt and selected providers
  - Save prompt to database immediately
  - Queue requests to all selected providers concurrently
  - Stream responses in real-time using Server-Sent Events (SSE) or WebSockets
  - Handle rate limits and errors gracefully
  - Save each response as it arrives
  - Generate and save summary after all responses complete

### 3. Results Display (Tabbed Interface)
- **UI Component:** Tabbed container
  - One tab per provider
  - Show provider name, model used, timestamp
  - Display response in formatted text area (updates in real-time)
  - Copy to clipboard functionality
  - Export individual responses
  - Loading indicators per provider
- **Features:**
  - Real-time streaming updates as responses arrive (Server-Sent Events)
  - Error handling display (if provider fails)
  - Response time metrics
  - Visual feedback when each provider completes

### 4. Summary & Analysis
- **UI Component:** Summary panel/tab
- **Analysis Logic (Text-based):**
  - **Overlap Detection:**
    - Use text similarity algorithms (TF-IDF, cosine similarity on word vectors)
    - Extract keywords and phrases using NLTK/spaCy
    - Identify common themes, phrases, or concepts across responses
    - Show percentage of agreement/overlap
    - Highlight matching sentences/phrases
  - **Outlier Detection:**
    - Compare each response against the group average
    - Identify responses with low similarity scores to others
    - Mark unique points/claims that appear in only one response
    - Visual indicators (colors, badges) for outliers
- **Implementation Libraries:**
  - **NLTK** or **spaCy** for text processing and keyword extraction
  - **scikit-learn** for TF-IDF vectorization and cosine similarity
  - **difflib** for sequence matching
  - Future: Can add embeddings-based analysis as enhancement

### 5. Authentication & User Management
- **UI Component:** Login/Register page with Google OAuth
- **Features:**
  - Google OAuth 2.0 authentication
  - User registration on first login
  - Session management (JWT tokens)
  - Protected routes
  - User profile display
- **Backend:**
  - Google OAuth integration
  - JWT token generation and validation
  - User session management
  - User-specific data isolation

### 6. History & Past Queries
- **UI Component:** History page/sidebar
- **Features:**
  - List all past prompts (chronological)
  - View individual prompt details
  - See all LLM responses for each prompt
  - View generated summary for each query
  - Search/filter history
  - Delete history entries
- **Backend:**
  - Store all prompts, responses, and summaries
  - User-specific history retrieval
  - Efficient querying and pagination

### 7. Additional Features
- Export all responses as JSON/CSV
- Compare specific responses side-by-side
- Regenerate individual responses
- Cost tracking (optional)

## Security Considerations

### API Key Storage
1. **Encryption:**
   - Use symmetric encryption (AES-256-GCM)
   - Store encryption key in environment variable (never in code)
   - Rotate encryption keys periodically

2. **Database Schema:**
   ```sql
   users (
     id (UUID, PK), google_id (unique), email, name, 
     picture_url, created_at, updated_at
   )
   
   api_keys (
     id (UUID, PK), user_id (FK), provider, encrypted_key, 
     key_hash (for verification), created_at, updated_at
   )
   
   prompts (
     id (UUID, PK), user_id (FK), prompt_text, 
     created_at, updated_at
   )
   
   llm_responses (
     id (UUID, PK), prompt_id (FK), provider, model_used, 
     response_text, response_time_ms, error_message, 
     created_at
   )
   
   summaries (
     id (UUID, PK), prompt_id (FK), summary_text, 
     overlap_data (JSONB), outlier_data (JSONB), 
     created_at, updated_at
   )
   ```

3. **Access Control:**
   - API keys only accessible to authenticated user
   - Rate limiting on API endpoints
   - Input validation and sanitization

### Best Practices
- Never log API keys
- Use HTTPS for all communications
- Implement CORS properly
- Sanitize user inputs
- Use parameterized queries (prevent SQL injection)

## Project Structure

```
llm-aggregator/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── auth/
│   │   │   │   ├── Login.tsx
│   │   │   │   └── GoogleAuthButton.tsx
│   │   │   ├── PromptInput.tsx
│   │   │   ├── ProviderSelector.tsx
│   │   │   ├── ResultsTabs.tsx
│   │   │   ├── SummaryPanel.tsx
│   │   │   ├── ApiKeyManager.tsx
│   │   │   └── History.tsx
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   └── auth.ts
│   │   ├── hooks/
│   │   │   ├── useLLMResponses.ts
│   │   │   └── useAuth.ts
│   │   ├── context/
│   │   │   └── AuthContext.tsx
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── Dockerfile
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── prompts.py
│   │   │   ├── history.py
│   │   │   ├── providers.py
│   │   │   └── keys.py
│   │   ├── services/
│   │   │   ├── llm_providers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py
│   │   │   │   ├── openai_client.py
│   │   │   │   ├── anthropic_client.py
│   │   │   │   └── google_client.py
│   │   │   ├── encryption.py
│   │   │   ├── analysis.py
│   │   │   └── auth.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── api_key.py
│   │   │   ├── prompt.py
│   │   │   ├── response.py
│   │   │   └── summary.py
│   │   ├── schemas/
│   │   │   └── __init__.py
│   │   ├── middleware/
│   │   │   └── auth.py
│   │   └── main.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   └── alembic/ (for migrations)
├── docker/
│   ├── docker-compose.yml
│   └── postgres/
│       └── init.sql
├── docs/
│   └── API.md
├── .dockerignore
├── .gitignore
├── project.md (this file)
└── README.md
```

## Implementation Phases

### Phase 1: Foundation
1. Set up project structure
2. Initialize frontend (Vite + React + TypeScript)
3. Initialize backend (FastAPI)
4. Set up Docker containers (PostgreSQL, backend, frontend)
5. Set up PostgreSQL database connection
6. Create database schema with Alembic migrations (users, api_keys, prompts, responses, summaries)
7. Implement basic encryption utilities

### Phase 2: Authentication
1. Set up Google OAuth 2.0 credentials
2. Implement Google OAuth backend endpoints
3. Implement JWT token generation and validation
4. Create authentication middleware
5. Build login/register UI components
6. Implement protected routes in frontend
7. Test authentication flow

### Phase 3: API Key Management
1. Create API key management UI
2. Implement encryption/decryption backend
3. Database operations for keys
4. API endpoints for CRUD operations
5. Test key storage and retrieval

### Phase 4: LLM Integration
1. Implement provider clients (OpenAI, Anthropic, Google)
2. Create unified provider interface
3. Error handling and retry logic
4. Rate limiting per provider
5. Test with sample prompts

### Phase 5: Prompt Interface & Results
1. Build prompt input UI
2. Implement provider selection
3. Create tabbed results display
4. Backend endpoint for multi-provider queries with streaming (Server-Sent Events)
5. Implement real-time response streaming to frontend
6. Save prompts and responses to database as they arrive
7. Display loading states and real-time updates

### Phase 6: Analysis & Summary
1. Implement text-based overlap detection (TF-IDF, cosine similarity)
2. Implement outlier detection using similarity scores
3. Create summary UI component
4. Visual indicators for overlaps/outliers
5. Export functionality
6. Install and configure NLTK/spaCy for text processing

### Phase 7: History & Past Queries
1. Create history UI component
2. Implement history API endpoints
3. Display past prompts, responses, and summaries
4. Add search/filter functionality
5. Implement pagination for history
6. Add delete functionality

### Phase 8: Polish & Security
1. Comprehensive error handling
2. Loading states and UX improvements
3. Security audit
4. Docker optimization
5. Documentation
6. Cloud deployment preparation (AWS/GCP)

## Technical Decisions (Finalized)

### 1. Backend Language
- **✅ Python with FastAPI** - Chosen for better async handling and ML/AI library integration

### 2. Analysis Method
- **✅ Text-based** - Using NLTK/spaCy and scikit-learn for keyword extraction and similarity
- **Future:** Can add embeddings-based analysis as optional enhancement

### 3. Database
- **✅ PostgreSQL** - Always used, for all environments (development and production)

### 4. Frontend Framework
- **✅ Vite + React + TypeScript** - Lightweight, fast, modern
- **✅ Tailwind CSS** - Minimal styling framework

### 5. Authentication
- **✅ Google OAuth 2.0** - Multi-user support with Google account registration/login
- **✅ JWT Tokens** - For session management
- **✅ User Isolation** - Each user has their own API keys and history

### 6. Data Persistence
- **✅ Full History** - All prompts, responses, and summaries saved per user
- **✅ User-Specific** - Complete data isolation between users

### 7. Real-time Updates
- **✅ Server-Sent Events (SSE)** - Stream responses as they arrive from LLM providers

### 8. Deployment
- **✅ Docker Containerization** - All components (DB, BE, FE) in containers
- **✅ Cloud-Ready** - Designed for AWS/GCP deployment

## Environment Variables

### Backend (.env)
```env
# Encryption
ENCRYPTION_KEY=<32-byte hex string>

# Database (PostgreSQL)
DATABASE_URL=postgresql://llm_user:llm_password@postgres:5432/llm_aggregator
# For local development: postgresql://llm_user:llm_password@localhost:5432/llm_aggregator

# Server
PORT=8000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000  # Vite default port

# Google OAuth
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# JWT
JWT_SECRET_KEY=<random-secret-key>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Optional: For future embeddings-based analysis
# OPENAI_API_KEY_FOR_ANALYSIS=<key>
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=<your-google-client-id>
```

### Docker Compose
- Database credentials configured in docker-compose.yml
- Environment variables passed to containers

## API Endpoints

### Authentication
- `GET /api/auth/google` - Initiate Google OAuth flow
- `GET /api/auth/google/callback` - Google OAuth callback
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/me` - Get current user info (protected)

### API Keys (Protected)
- `GET /api/keys` - List all providers and key status for current user
- `POST /api/keys` - Add/update API key for current user
  - Body: `{ provider: string, api_key: string }`
- `DELETE /api/keys/{provider}` - Delete API key for current user
- `POST /api/keys/{provider}/test` - Test connection with stored key

### Prompts (Protected)
- `POST /api/prompts` - Send prompt to selected providers (streaming)
  - Body: `{ prompt: string, providers: string[] }`
  - Response: Server-Sent Events stream with real-time updates
  - Format: `data: {"type": "response", "provider": "openai", "text": "...", "done": false}`
- `GET /api/prompts/{prompt_id}` - Get specific prompt with all responses and summary
- `GET /api/prompts` - Get prompt history for current user (paginated)
  - Query params: `?page=1&limit=20&search=...`

### History (Protected)
- `GET /api/history` - Get all prompts for current user
  - Query params: `?page=1&limit=20&search=...`
- `GET /api/history/{prompt_id}` - Get full details of a past prompt
- `DELETE /api/history/{prompt_id}` - Delete a prompt and all associated data

### Analysis
- `POST /api/analyze` - Generate summary (internal, called automatically)
  - Body: `{ prompt_id: string, responses: { provider: string, text: string }[] }`
  - Response: `{ overlaps: [], outliers: [], summary: string }`

## Dependencies

### Backend (Python)
- `fastapi` - Web framework
- `uvicorn[standard]` - ASGI server with standard extras
- `sqlalchemy` - ORM
- `alembic` - Database migrations
- `psycopg2-binary` - PostgreSQL adapter
- `cryptography` - Encryption utilities
- `openai` - OpenAI API client
- `anthropic` - Anthropic API client
- `google-generativeai` - Google Gemini API client
- `google-auth` - Google OAuth authentication
- `google-auth-oauthlib` - Google OAuth flow
- `python-jose[cryptography]` - JWT token handling
- `passlib[bcrypt]` - Password hashing (if needed)
- `nltk` or `spacy` - Text processing
- `scikit-learn` - TF-IDF and similarity calculations
- `python-dotenv` - Environment variable management
- `pydantic` - Data validation
- `sse-starlette` - Server-Sent Events support for streaming
- `python-multipart` - Form data parsing

### Frontend (Node.js)
- `react` - UI framework
- `react-dom` - React DOM bindings
- `react-router-dom` - Routing
- `typescript` - Type safety
- `vite` - Build tool and dev server
- `tailwindcss` - CSS framework
- `autoprefixer` - CSS vendor prefixes
- `postcss` - CSS processing
- `@react-oauth/google` - Google OAuth React integration (optional)
- `axios` or native `fetch` - HTTP client

## Docker Configuration

### docker-compose.yml Structure
```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: llm_user
      POSTGRES_PASSWORD: llm_password
      POSTGRES_DB: llm_aggregator
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://llm_user:llm_password@postgres:5432/llm_aggregator
      # ... other env vars
    ports:
      - "8000:8000"
    depends_on:
      - postgres
  
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend
```

### Dockerfiles
- **Backend:** Python 3.11 slim base, install dependencies, run uvicorn
- **Frontend:** Node.js base, build with Vite, serve static files (or use nginx for production)
- **PostgreSQL:** Official postgres image with init scripts

## Cloud Deployment Considerations

### AWS
- **RDS PostgreSQL** - Managed database
- **ECS/EKS** - Container orchestration
- **ECR** - Container registry
- **ALB** - Load balancer
- **Secrets Manager** - For API keys and secrets

### GCP
- **Cloud SQL PostgreSQL** - Managed database
- **Cloud Run** - Serverless containers
- **GCR** - Container registry
- **Cloud Load Balancing** - Load balancer
- **Secret Manager** - For API keys and secrets

## Next Steps

1. **Ready to implement** - All technical decisions finalized:
   - ✅ Backend: Python with FastAPI
   - ✅ Frontend: Vite + React + TypeScript
   - ✅ Database: PostgreSQL
   - ✅ Analysis: Text-based (NLTK/spaCy + scikit-learn)
   - ✅ Authentication: Google OAuth with JWT
   - ✅ History: Full persistence of prompts, responses, summaries
   - ✅ Streaming: Real-time updates via Server-Sent Events
   - ✅ Deployment: Docker containers, cloud-ready

2. **Generate code** starting with Phase 1:
   - Project scaffolding
   - Docker setup (docker-compose.yml, Dockerfiles)
   - Basic frontend/backend setup
   - PostgreSQL database connection
   - Database schema with Alembic (users, api_keys, prompts, responses, summaries)
   - Encryption utilities

3. **Iterate** through phases, testing each before moving to next

