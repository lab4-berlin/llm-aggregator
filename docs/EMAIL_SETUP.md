# Email Setup Guide - Google Workspace SMTP

This guide explains how to configure Google Workspace SMTP for email verification and password reset.

## Google Workspace SMTP Configuration

### Prerequisites

1. **Google Workspace account** with admin access (or personal Gmail account)
2. **2-Factor Authentication (2FA)** enabled on your Google account
3. **App Password** generated (required when 2FA is enabled)

### Step-by-Step Setup

#### Step 1: Enable 2-Factor Authentication

1. Go to https://myaccount.google.com/security
2. Under "Signing in to Google", click "2-Step Verification"
3. Follow the prompts to enable 2FA (if not already enabled)

#### Step 2: Generate App Password

1. Go to https://myaccount.google.com/apppasswords
   - If you don't see this link, make sure 2FA is enabled first
2. Select:
   - **App**: Choose "Mail"
   - **Device**: Choose "Other (Custom name)" and enter "LLM Aggregator"
3. Click "Generate"
4. **Copy the 16-character password** (you'll only see it once!)
   - Format: `xxxx xxxx xxxx xxxx` (remove spaces when using)

#### Step 3: Configure Environment Variables

Create a `.env` file in the project root (or update existing one):

```bash
# Google Workspace SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@yourdomain.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
SMTP_FROM_EMAIL=your-email@yourdomain.com
FRONTEND_URL=http://localhost:5173
```

**Important Notes:**
- `SMTP_USER`: Your full Google Workspace email address
- `SMTP_PASSWORD`: The 16-character App Password (remove spaces)
- `SMTP_FROM_EMAIL`: Usually the same as SMTP_USER
- For production, update `FRONTEND_URL` to your actual domain

#### Step 4: Update Docker Compose

The `docker-compose.yml` is already configured to read these environment variables. You can either:

**Option A: Use .env file (Recommended)**
- Create `.env` file in project root
- Docker Compose will automatically load it

**Option B: Set in docker-compose.yml directly**
- Add the values directly in the `environment` section (not recommended for production)

#### Step 5: Restart Backend

```bash
docker-compose restart backend
```

#### Step 6: Test Email Sending

1. Register a new user or resend verification email
2. Check your email inbox for the verification email
3. Check backend logs if email doesn't arrive:
   ```bash
   docker-compose logs backend | grep -E "(Email|SMTP|VERIFICATION)"
   ```

## SMTP Settings Summary

| Setting | Value |
|---------|-------|
| **SMTP Host** | `smtp.gmail.com` |
| **SMTP Port** | `587` (TLS) or `465` (SSL) |
| **Security** | STARTTLS (port 587) or SSL (port 465) |
| **Authentication** | Required (App Password) |

## Troubleshooting

### "Username and Password not accepted" Error

**Solution:**
- Make sure you're using an **App Password**, not your regular Google password
- Verify 2FA is enabled on your account
- Check that the App Password was copied correctly (16 characters, no spaces)

### "Less secure app access" Error

**Solution:**
- This error means you're using your regular password instead of an App Password
- Generate a new App Password and use that instead

### Connection Timeout

**Solution:**
- Verify firewall isn't blocking port 587
- Try port 465 with SSL instead:
  ```bash
  SMTP_PORT=465
  ```
  (Note: You'll need to update the email service code to use SSL instead of STARTTLS)

### Emails Not Arriving

**Check:**
1. Backend logs: `docker-compose logs backend | grep Email`
2. Spam folder
3. SMTP credentials are correct
4. Google account isn't locked or restricted

### Daily Sending Limits

**Google Workspace Limits:**
- **Free Gmail**: 500 emails/day
- **Google Workspace**: 2000 emails/day (varies by plan)

If you hit the limit, you'll need to wait 24 hours or upgrade your plan.

## Alternative: Personal Gmail Account

If you don't have Google Workspace, you can use a personal Gmail account with the same setup:

1. Enable 2FA on your Gmail account
2. Generate App Password
3. Use `smtp.gmail.com:587`
4. Same configuration as above

**Note:** Personal Gmail has stricter sending limits (500 emails/day).

## Production Considerations

For production deployment:

1. **Use environment variables** (never hardcode credentials)
2. **Update FRONTEND_URL** to your production domain
3. **Consider using a dedicated email service** (SendGrid, AWS SES, etc.) for higher limits
4. **Monitor email delivery** and set up alerts for failures
5. **Use a dedicated email address** (e.g., `noreply@yourdomain.com`) for system emails

## Current Status

If SMTP is not configured:
- Verification tokens are logged to backend console
- You can manually verify using: `docker-compose logs backend | grep "VERIFICATION TOKEN"`
- Registration still works, but emails won't be sent

## Quick Reference

```bash
# Check if SMTP is configured
docker-compose logs backend | grep "SMTP credentials"

# View verification tokens (if SMTP not configured)
docker-compose logs backend | grep "VERIFICATION TOKEN"

# Test email sending
# Register a new user and check email inbox
```
