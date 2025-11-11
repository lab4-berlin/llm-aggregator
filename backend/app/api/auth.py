from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from app.database import get_db
from app.models.user import User
from app.services.auth import (
    create_access_token,
    verify_password,
    get_password_hash,
    generate_verification_token,
    generate_reset_token,
)
from app.services.email import send_verification_email, send_password_reset_email
from app.middleware.auth import get_current_user_id
from app.config import settings
import uuid

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class VerifyEmailRequest(BaseModel):
    token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


@router.post("/register")
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Generate verification token
    verification_token = generate_verification_token()
    
    # Create new user (not verified yet)
    user = User(
        id=uuid.uuid4(),
        email=request.email,
        password_hash=get_password_hash(request.password),
        name=request.name or request.email.split("@")[0],
        email_verified=False,
        email_verification_token=verification_token,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Send verification email
    send_verification_email(
        email=user.email,
        name=user.name or user.email,
        verification_token=verification_token,
    )
    
    return {
        "message": "Registration successful. Please check your email to verify your account.",
        "user_id": str(user.id),
    }


@router.post("/verify-email")
async def verify_email(
    request: VerifyEmailRequest,
    db: Session = Depends(get_db),
):
    """Verify user email with token."""
    user = db.query(User).filter(
        User.email_verification_token == request.token
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )
    
    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified",
        )
    
    # Verify the email
    user.email_verified = True
    user.email_verification_token = None
    db.commit()
    
    return {
        "message": "Email verified successfully",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
        },
    }


@router.post("/resend-verification")
async def resend_verification(
    request: ForgotPasswordRequest,  # Reusing the email request model
    db: Session = Depends(get_db),
):
    """Resend verification email."""
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        # Don't reveal if email exists
        return {"message": "If the email exists, a verification email has been sent."}
    
    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified",
        )
    
    # Generate new token
    verification_token = generate_verification_token()
    user.email_verification_token = verification_token
    db.commit()
    
    # Send verification email
    send_verification_email(
        email=user.email,
        name=user.name or user.email,
        verification_token=verification_token,
    )
    
    return {"message": "If the email exists, a verification email has been sent."}


@router.post("/login")
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    """Login user."""
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Check if email is verified
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your email for verification link.",
        )
    
    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
        },
    }


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    """Request password reset."""
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        # Don't reveal if email exists
        return {"message": "If the email exists, a password reset link has been sent."}
    
    # Generate reset token
    reset_token = generate_reset_token()
    user.password_reset_token = reset_token
    user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
    db.commit()
    
    # Send reset email
    send_password_reset_email(
        email=user.email,
        name=user.name or user.email,
        reset_token=reset_token,
    )
    
    return {"message": "If the email exists, a password reset link has been sent."}


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    """Reset password with token."""
    user = db.query(User).filter(
        User.password_reset_token == request.token
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )
    
    # Check if token expired
    if user.password_reset_expires and user.password_reset_expires < datetime.utcnow():
        user.password_reset_token = None
        user.password_reset_expires = None
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired",
        )
    
    # Update password
    user.password_hash = get_password_hash(request.new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    db.commit()
    
    return {"message": "Password reset successfully"}


@router.get("/me")
async def get_current_user(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get current user info."""
    user = db.query(User).filter(User.id == uuid.UUID(current_user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "email_verified": user.email_verified,
    }


@router.post("/logout")
async def logout():
    """Logout user (client-side token removal)."""
    return {"message": "Logged out successfully"}
