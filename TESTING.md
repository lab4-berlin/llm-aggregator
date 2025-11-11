# Testing Registration Flow

## Quick Test Guide

### Option 1: Using the Test Script

1. Make sure backend is running:
   ```bash
   docker-compose up backend
   ```

2. Run the test script:
   ```bash
   python test_registration.py
   ```

3. The script will:
   - Register a new user
   - Show you the verification token from backend logs
   - Verify the email
   - Login
   - Test logout

### Option 2: Manual Testing via Frontend

1. Start all services:
   ```bash
   docker-compose up
   ```

2. Open browser: http://localhost:5173

3. **Register:**
   - Click "Register" or go to `/register`
   - Fill in email, password, and optional name
   - Submit
   - You'll see a success message

4. **Get Verification Token:**
   - Check backend logs (docker-compose logs backend)
   - Look for: `🔗 VERIFICATION LINK:` and `🔑 VERIFICATION TOKEN:`
   - Copy the token

5. **Verify Email:**
   - Go to: http://localhost:5173/verify-email?token=YOUR_TOKEN
   - Or manually call the API:
     ```bash
     curl -X POST http://localhost:8000/api/auth/verify-email \
       -H "Content-Type: application/json" \
       -d '{"token": "YOUR_TOKEN"}'
     ```

6. **Login:**
   - Go to `/login`
   - Enter email and password
   - Should successfully login

7. **Logout:**
   - Click logout button in the dashboard

### Option 3: Using API Directly

1. **Register:**
   ```bash
   curl -X POST http://localhost:8000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "testpass123",
       "name": "Test User"
     }'
   ```

2. **Check backend logs for verification token:**
   ```bash
   docker-compose logs backend | grep "VERIFICATION TOKEN"
   ```

3. **Verify email:**
   ```bash
   curl -X POST http://localhost:8000/api/auth/verify-email \
     -H "Content-Type: application/json" \
     -d '{"token": "TOKEN_FROM_LOGS"}'
   ```

4. **Login:**
   ```bash
   curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "testpass123"
     }'
   ```

5. **Get user info (with token):**
   ```bash
   curl -X GET http://localhost:8000/api/auth/me \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

## Expected Behavior

### Happy Path:
1. ✅ Registration succeeds → Returns success message
2. ✅ Verification token appears in backend logs
3. ✅ Email verification succeeds → Email marked as verified
4. ✅ Login succeeds (only after verification) → Returns JWT token
5. ✅ Can access protected endpoints with token
6. ✅ Logout works (client-side token removal)

### Error Cases:
- ❌ Login before verification → Error: "Email not verified"
- ❌ Invalid verification token → Error: "Invalid or expired token"
- ❌ Already verified email → Error: "Email already verified"
- ❌ Wrong password → Error: "Incorrect email or password"

## Debugging

### Check Backend Logs:
```bash
docker-compose logs -f backend
```

Look for:
- `🔗 VERIFICATION LINK:` - Full URL to verify email
- `🔑 VERIFICATION TOKEN:` - Token to use for verification
- `📧 EMAIL (not sent - SMTP not configured)` - If SMTP not set up

### Check Database:
```bash
docker-compose exec postgres psql -U llm_user -d llm_aggregator

# Check users
SELECT id, email, email_verified, email_verification_token FROM users;

# Check specific user
SELECT * FROM users WHERE email = 'test@example.com';
```

### Common Issues:

1. **"Email not verified" error on login:**
   - Make sure you verified the email first
   - Check `email_verified` column in database

2. **Verification token not found:**
   - Check backend logs for the token
   - Make sure you're using the correct token
   - Token is one-time use only

3. **SMTP not configured:**
   - This is OK for testing - tokens will appear in logs
   - For production, configure SMTP settings in `.env`

