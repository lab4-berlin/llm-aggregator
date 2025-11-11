import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, html_body: str, text_body: str = None) -> bool:
    """Send an email using SMTP."""
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP credentials not configured. Email not sent.")
        logger.info(f"📧 EMAIL (not sent - SMTP not configured):")
        logger.info(f"   To: {to_email}")
        logger.info(f"   Subject: {subject}")
        logger.info(f"   Body: {text_body or html_body}")
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
        msg['To'] = to_email
        
        if text_body:
            msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False


def send_verification_email(email: str, name: str, verification_token: str) -> bool:
    """Send email verification email."""
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
    
    subject = "Verify your email address"
    html_body = f"""
    <html>
      <body>
        <h2>Welcome to LLM Aggregator!</h2>
        <p>Hi {name},</p>
        <p>Please verify your email address by clicking the link below:</p>
        <p><a href="{verification_url}">{verification_url}</a></p>
        <p>If you didn't create an account, please ignore this email.</p>
      </body>
    </html>
    """
    text_body = f"""
    Welcome to LLM Aggregator!
    
    Hi {name},
    
    Please verify your email address by visiting:
    {verification_url}
    
    Verification Token: {verification_token}
    
    If you didn't create an account, please ignore this email.
    """
    
    logger.info(f"🔗 VERIFICATION LINK: {verification_url}")
    logger.info(f"🔑 VERIFICATION TOKEN: {verification_token}")
    
    return send_email(email, subject, html_body, text_body)


def send_password_reset_email(email: str, name: str, reset_token: str) -> bool:
    """Send password reset email."""
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
    
    subject = "Reset your password"
    html_body = f"""
    <html>
      <body>
        <h2>Password Reset Request</h2>
        <p>Hi {name},</p>
        <p>You requested to reset your password. Click the link below to reset it:</p>
        <p><a href="{reset_url}">{reset_url}</a></p>
        <p>This link will expire in 1 hour.</p>
        <p>If you didn't request this, please ignore this email.</p>
      </body>
    </html>
    """
    text_body = f"""
    Password Reset Request
    
    Hi {name},
    
    You requested to reset your password. Visit the link below to reset it:
    {reset_url}
    
    This link will expire in 1 hour.
    
    If you didn't request this, please ignore this email.
    """
    
    return send_email(email, subject, html_body, text_body)

