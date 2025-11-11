#!/usr/bin/env python3
"""Simple email test script to debug SMTP connection."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
import sys

def test_send_email():
    """Test sending a simple email."""
    print("=" * 60)
    print("SMTP Email Test")
    print("=" * 60)
    print(f"SMTP_HOST: {settings.SMTP_HOST}")
    print(f"SMTP_PORT: {settings.SMTP_PORT}")
    print(f"SMTP_USER: {settings.SMTP_USER}")
    print(f"SMTP_PASSWORD length: {len(settings.SMTP_PASSWORD) if settings.SMTP_PASSWORD else 0}")
    print(f"SMTP_PASSWORD (first 4): {settings.SMTP_PASSWORD[:4] if settings.SMTP_PASSWORD else 'None'}...")
    print(f"SMTP_PASSWORD (last 4): ...{settings.SMTP_PASSWORD[-4:] if settings.SMTP_PASSWORD else 'None'}")
    print(f"SMTP_PASSWORD has spaces: {' ' in settings.SMTP_PASSWORD if settings.SMTP_PASSWORD else False}")
    print(f"SMTP_FROM_EMAIL: {settings.SMTP_FROM_EMAIL}")
    print("=" * 60)
    
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print("ERROR: SMTP credentials not configured!")
        return False
    
    to_email = "ilya@lab4.berlin"
    subject = "Test Email - Hello World"
    body = "Hello World! This is a test email from LLM Aggregator."
    
    try:
        print(f"\nCreating email message...")
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
        msg['To'] = to_email
        msg.attach(MIMEText(body, 'plain'))
        
        print(f"Connecting to {settings.SMTP_HOST}:{settings.SMTP_PORT}...")
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            print("Starting TLS...")
            server.starttls()
            
            print(f"Logging in as {settings.SMTP_USER}...")
            print(f"Password being used: '{settings.SMTP_PASSWORD}'")
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            print("✓ Login successful!")
            
            print(f"Sending email to {to_email}...")
            server.send_message(msg)
            print("✓ Email sent successfully!")
            return True
            
    except smtplib.SMTPAuthenticationError as e:
        print(f"✗ Authentication failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check if App Password is correct")
        print("2. Verify 2FA is enabled on the account")
        print("3. Make sure App Password was generated for the correct account")
        print("4. Try generating a new App Password")
        return False
    except smtplib.SMTPException as e:
        print(f"✗ SMTP error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_send_email()
    sys.exit(0 if success else 1)

