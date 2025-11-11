# LLM Aggregator

A platform to send prompts to multiple LLM providers simultaneously, compare responses, and generate intelligent summaries.

## Features

- 🔐 Email/Password authentication
- 🔑 Secure API key management (encrypted storage)
- 📝 Multi-provider prompt submission
- 📊 Real-time response streaming
- 📈 Response comparison and analysis
- 📚 Full history of prompts and responses

## Tech Stack

- **Backend:** Python + FastAPI
- **Frontend:** React + TypeScript + Vite + Tailwind CSS
- **Database:** PostgreSQL
- **Deployment:** Docker Compose

## Setup

### Prerequisites

- Docker and Docker Compose

### Environment Variables

1. Copy `.env.example` files:
   - `backend/.env.example` → `backend/.env`
   - `frontend/.env.example` → `frontend/.env`

2. Generate encryption key:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   Update `ENCRYPTION_KEY` in `backend/.env`

4. Generate JWT secret:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   Update `JWT_SECRET_KEY` in `backend/.env`

5. Configure Google Workspace SMTP (for email verification and password reset):
   
   **Quick Setup:**
   1. Enable 2FA on your Google account: https://myaccount.google.com/security
   2. Generate App Password: https://myaccount.google.com/apppasswords
   3. Create `.env` file in project root:
      ```bash
      SMTP_HOST=smtp.gmail.com
      SMTP_PORT=587
      SMTP_USER=your-email@yourdomain.com
      SMTP_PASSWORD=your-16-char-app-password
      SMTP_FROM_EMAIL=your-email@yourdomain.com
      FRONTEND_URL=http://localhost:5173
      ```
   4. Restart backend: `docker-compose restart backend`
   
   **See `docs/EMAIL_SETUP.md` for detailed instructions.**
   
   **Note:** If SMTP is not configured, verification tokens will be logged to backend console.

### Running with Docker

```bash
docker-compose up --build
```

This will start:
- PostgreSQL on port 5432
- Backend API on port 8000
- Frontend on port 5173

### Database Migrations

The database tables are created automatically on first run. For manual migrations:

```bash
cd backend
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Development

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Documentation

Once the backend is running, visit:
- API docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
llm-aggregator/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── docker-compose.yml
└── project.md        # Detailed project plan
```

## Current Status

✅ Database setup with PostgreSQL
✅ User authentication with email/password
✅ Email verification (mandatory)
✅ Password reset functionality
✅ Registration and login functionality
✅ Mock LLM provider responses
✅ Real-time response streaming
✅ Basic UI for prompts and results

🚧 In Progress:
- Real LLM provider integration
- Response analysis and summarization
- History view

## License

MIT
