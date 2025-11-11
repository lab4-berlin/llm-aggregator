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
  - Queue requests to all selected providers
  - Handle rate limits and errors gracefully
  - Return streaming responses if supported

### 3. Results Display (Tabbed Interface)
- **UI Component:** Tabbed container
  - One tab per provider
  - Show provider name, model used, timestamp
  - Display response in formatted text area
  - Copy to clipboard functionality
  - Export individual responses
- **Features:**
  - Real-time updates as responses arrive
  - Error handling display (if provider fails)
  - Response time metrics

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

### 5. Additional Features
- Export all responses as JSON/CSV
- Save prompt history
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
   api_keys (
     id, user_id, provider, encrypted_key, 
     key_hash (for verification), created_at, updated_at
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
│   │   │   ├── PromptInput.tsx
│   │   │   ├── ProviderSelector.tsx
│   │   │   ├── ResultsTabs.tsx
│   │   │   ├── SummaryPanel.tsx
│   │   │   └── ApiKeyManager.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── hooks/
│   │   │   └── useLLMResponses.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── prompts.py
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
│   │   │   └── analysis.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── database.py
│   │   ├── schemas/
│   │   │   └── __init__.py
│   │   └── main.py
│   ├── requirements.txt
│   ├── .env.example
│   └── alembic/ (for migrations)
├── database/
│   └── migrations/ (Alembic migrations)
├── docs/
│   └── API.md
├── project.md (this file)
└── README.md
```

## Implementation Phases

### Phase 1: Foundation
1. Set up project structure
2. Initialize frontend (Vite + React + TypeScript)
3. Initialize backend (FastAPI)
4. Set up PostgreSQL database connection
5. Create database schema with Alembic migrations
6. Implement basic encryption utilities

### Phase 2: API Key Management
1. Create API key management UI
2. Implement encryption/decryption backend
3. Database operations for keys
4. API endpoints for CRUD operations
5. Test key storage and retrieval

### Phase 3: LLM Integration
1. Implement provider clients (OpenAI, Anthropic, Google)
2. Create unified provider interface
3. Error handling and retry logic
4. Rate limiting per provider
5. Test with sample prompts

### Phase 4: Prompt Interface & Results
1. Build prompt input UI
2. Implement provider selection
3. Create tabbed results display
4. Backend endpoint for multi-provider queries
5. Real-time response streaming (optional)

### Phase 5: Analysis & Summary
1. Implement text-based overlap detection (TF-IDF, cosine similarity)
2. Implement outlier detection using similarity scores
3. Create summary UI component
4. Visual indicators for overlaps/outliers
5. Export functionality
6. Install and configure NLTK/spaCy for text processing

### Phase 6: Polish & Security
1. Add authentication (if multi-user)
2. Comprehensive error handling
3. Loading states and UX improvements
4. Security audit
5. Documentation

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
- **TBD:** Single-user vs multi-user (to be decided during implementation)

## Environment Variables

```env
# Encryption
ENCRYPTION_KEY=<32-byte hex string>

# Database (PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost:5432/llm_aggregator

# Server
PORT=8000
CORS_ORIGINS=http://localhost:5173  # Vite default port

# Optional: For future embeddings-based analysis
# OPENAI_API_KEY_FOR_ANALYSIS=<key>
```

## API Endpoints (Proposed)

### API Keys
- `GET /api/keys` - List all providers and key status
- `POST /api/keys` - Add/update API key
- `DELETE /api/keys/{provider}` - Delete API key
- `POST /api/keys/{provider}/test` - Test connection

### Prompts
- `POST /api/prompts` - Send prompt to selected providers
  - Body: `{ prompt: string, providers: string[] }`
  - Response: `{ job_id: string }` or streaming
- `GET /api/prompts/{job_id}` - Get results
- `GET /api/prompts` - Get prompt history

### Analysis
- `POST /api/analyze` - Generate summary
  - Body: `{ responses: { provider: string, text: string }[] }`
  - Response: `{ overlaps: [], outliers: [], summary: string }`

## Dependencies

### Backend (Python)
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `sqlalchemy` - ORM
- `alembic` - Database migrations
- `psycopg2-binary` - PostgreSQL adapter
- `cryptography` - Encryption utilities
- `openai` - OpenAI API client
- `anthropic` - Anthropic API client
- `google-generativeai` - Google Gemini API client
- `nltk` or `spacy` - Text processing
- `scikit-learn` - TF-IDF and similarity calculations
- `python-dotenv` - Environment variable management
- `pydantic` - Data validation

### Frontend (Node.js)
- `react` - UI framework
- `react-dom` - React DOM bindings
- `typescript` - Type safety
- `vite` - Build tool and dev server
- `tailwindcss` - CSS framework
- `autoprefixer` - CSS vendor prefixes
- `postcss` - CSS processing

## Next Steps

1. **Ready to implement** - All technical decisions finalized:
   - ✅ Backend: Python with FastAPI
   - ✅ Frontend: Vite + React + TypeScript
   - ✅ Database: PostgreSQL
   - ✅ Analysis: Text-based (NLTK/spaCy + scikit-learn)

2. **Generate code** starting with Phase 1:
   - Project scaffolding
   - Basic frontend/backend setup
   - PostgreSQL database connection
   - Database schema with Alembic
   - Encryption utilities

3. **Iterate** through phases, testing each before moving to next

## Remaining Questions to Consider

1. Do you need multi-user support or single-user? (affects authentication)
2. Should responses be saved/historical? (affects database schema)
3. Do you want streaming responses (real-time) or wait for all? (affects API design)
4. Deployment target (local, cloud, self-hosted)? (affects configuration)

