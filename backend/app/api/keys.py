from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database import get_db
from app.models.api_key import APIKey
from app.middleware.auth import get_current_user_id
from app.services.encryption import encrypt_api_key, decrypt_api_key
from pydantic import BaseModel
import uuid
import hashlib

router = APIRouter(prefix="/api/keys", tags=["keys"])


class APIKeyRequest(BaseModel):
    provider: str
    api_key: str


class APIKeyResponse(BaseModel):
    provider: str
    masked_key: str  # Last 4 characters only
    has_key: bool
    created_at: str | None = None


@router.get("")
async def get_api_keys(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get all API keys for current user (masked)."""
    user_id = uuid.UUID(current_user_id)
    
    # Get all keys for user
    keys = db.query(APIKey).filter(APIKey.user_id == user_id).all()
    
    # Create a map of provider -> key info
    key_map = {key.provider: key for key in keys}
    
    # Return status for all supported providers
    providers = ["openai", "anthropic", "google"]
    result = []
    
    for provider in providers:
        if provider in key_map:
            key = key_map[provider]
            # Show last 4 characters
            try:
                decrypted = decrypt_api_key(key.encrypted_key)
                masked = "****" + decrypted[-4:] if len(decrypted) >= 4 else "****"
            except Exception:
                masked = "****"
            result.append(APIKeyResponse(
                provider=provider,
                masked_key=masked,
                has_key=True,
                created_at=key.created_at.isoformat() if key.created_at else None
            ))
        else:
            result.append(APIKeyResponse(
                provider=provider,
                masked_key="",
                has_key=False,
                created_at=None
            ))
    
    return result


@router.post("")
async def save_api_key(
    request: APIKeyRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Save or update an API key for a provider."""
    if request.provider not in ["openai", "anthropic", "google"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid provider. Must be one of: openai, anthropic, google"
        )
    
    if not request.api_key or not request.api_key.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key cannot be empty"
        )
    
    user_id = uuid.UUID(current_user_id)
    
    # Encrypt the API key
    encrypted_key = encrypt_api_key(request.api_key.strip())
    
    # Create hash for verification (optional, for detecting changes)
    key_hash = hashlib.sha256(request.api_key.strip().encode()).hexdigest()[:16]
    
    # Check if key already exists for this user and provider
    existing_key = db.query(APIKey).filter(
        and_(
            APIKey.user_id == user_id,
            APIKey.provider == request.provider
        )
    ).first()
    
    if existing_key:
        # Update existing key
        existing_key.encrypted_key = encrypted_key
        existing_key.key_hash = key_hash
        db.commit()
        db.refresh(existing_key)
        return {"message": f"API key for {request.provider} updated successfully"}
    else:
        # Create new key
        new_key = APIKey(
            id=uuid.uuid4(),
            user_id=user_id,
            provider=request.provider,
            encrypted_key=encrypted_key,
            key_hash=key_hash
        )
        db.add(new_key)
        db.commit()
        db.refresh(new_key)
        return {"message": f"API key for {request.provider} saved successfully"}


@router.delete("/{provider}")
async def delete_api_key(
    provider: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Delete an API key for a provider."""
    if provider not in ["openai", "anthropic", "google"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid provider"
        )
    
    user_id = uuid.UUID(current_user_id)
    
    key = db.query(APIKey).filter(
        and_(
            APIKey.user_id == user_id,
            APIKey.provider == provider
        )
    ).first()
    
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No API key found for provider {provider}"
        )
    
    db.delete(key)
    db.commit()
    
    return {"message": f"API key for {provider} deleted successfully"}


@router.post("/{provider}/test")
async def test_api_key(
    provider: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Test if the stored API key is valid by making a simple API call."""
    if provider not in ["openai", "anthropic", "google"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid provider"
        )
    
    user_id = uuid.UUID(current_user_id)
    
    # Get the API key
    key = db.query(APIKey).filter(
        and_(
            APIKey.user_id == user_id,
            APIKey.provider == provider
        )
    ).first()
    
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No API key found for provider {provider}"
        )
    
    # Decrypt the key
    try:
        api_key = decrypt_api_key(key.encrypted_key)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to decrypt API key"
        )
    
    # Test the key by making a simple API call
    try:
        if provider == "openai":
            from app.services.llm.openai import test_openai_key
            is_valid = await test_openai_key(api_key)
        elif provider == "anthropic":
            from app.services.llm.anthropic import test_anthropic_key
            is_valid = await test_anthropic_key(api_key)
        elif provider == "google":
            from app.services.llm.google import test_google_key
            is_valid = await test_google_key(api_key)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unknown provider"
            )
        
        if is_valid:
            return {
                "valid": True,
                "message": f"API key for {provider} is valid"
            }
        else:
            return {
                "valid": False,
                "message": f"API key for {provider} is invalid"
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to test API key: {str(e)}"
        )

