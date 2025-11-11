from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import UUID as SQLUUID
from sqlalchemy import and_
from app.database import get_db
from app.models.prompt import Prompt
from app.models.response import LLMResponse
from app.models.api_key import APIKey
from app.middleware.auth import get_current_user_id
from app.services.encryption import decrypt_api_key
from app.services.llm.openai import stream_openai_response
from app.services.llm.anthropic import stream_anthropic_response
from app.services.llm.google import stream_google_response
from sse_starlette.sse import EventSourceResponse
import uuid
import asyncio
import json
import time
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/prompts", tags=["prompts"])


@router.post("")
async def create_prompt(
    prompt_data: dict,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Create a prompt and get mock responses from selected providers."""
    prompt_text = prompt_data.get("prompt")
    providers = prompt_data.get("providers", [])
    
    if not prompt_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt text is required",
        )
    
    if not providers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one provider must be selected",
        )
    
    # Create prompt in database
    prompt = Prompt(
        id=uuid.uuid4(),
        user_id=uuid.UUID(current_user_id),
        prompt_text=prompt_text,
    )
    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    
    async def generate_llm_responses():
        """Generate real LLM responses for each provider."""
        try:
            user_id = uuid.UUID(current_user_id)
            logger.info(f"Starting LLM response generation for {len(providers)} providers")
            
            # Get API keys for selected providers
            api_keys = {}
            for provider in providers:
                key_record = db.query(APIKey).filter(
                    and_(
                        APIKey.user_id == user_id,
                        APIKey.provider == provider
                    )
                ).first()
                
                if not key_record:
                    error_data = {
                        "type": "error",
                        "provider": provider,
                        "message": f"No API key configured for {provider}. Please add it in Settings.",
                    }
                    yield {
                        "event": "error",
                        "data": json.dumps(error_data)
                    }
                    continue
                
                try:
                    api_keys[provider] = decrypt_api_key(key_record.encrypted_key)
                except Exception as e:
                    logger.error(f"Failed to decrypt key for {provider}: {str(e)}")
                    error_data = {
                        "type": "error",
                        "provider": provider,
                        "message": f"Failed to decrypt API key for {provider}",
                    }
                    yield {
                        "event": "error",
                        "data": json.dumps(error_data)
                    }
                    continue
            
            # Process all providers sequentially (streaming chunks in real-time)
            async def process_provider(provider: str):
                """Process a single provider's response."""
                if provider not in api_keys:
                    return
                
                start_time = time.time()
                response_text = ""
                response_id = uuid.uuid4()
                
                try:
                    # Stream response from LLM and send chunks immediately
                    if provider == "openai":
                        async for chunk in stream_openai_response(api_keys[provider], prompt_text):
                            response_text += chunk
                            # Send chunk to client immediately
                            chunk_data = {
                                "type": "chunk",
                                "provider": provider,
                                "text": chunk,
                            }
                            yield {
                                "event": "message",
                                "data": json.dumps(chunk_data)
                            }
                    elif provider == "anthropic":
                        async for chunk in stream_anthropic_response(api_keys[provider], prompt_text):
                            response_text += chunk
                            chunk_data = {
                                "type": "chunk",
                                "provider": provider,
                                "text": chunk,
                            }
                            yield {
                                "event": "message",
                                "data": json.dumps(chunk_data)
                            }
                    elif provider == "google":
                        async for chunk in stream_google_response(api_keys[provider], prompt_text):
                            response_text += chunk
                            chunk_data = {
                                "type": "chunk",
                                "provider": provider,
                                "text": chunk,
                            }
                            yield {
                                "event": "message",
                                "data": json.dumps(chunk_data)
                            }
                    
                    # Save complete response to database
                    response_time_ms = int((time.time() - start_time) * 1000)
                    response = LLMResponse(
                        id=response_id,
                        prompt_id=prompt.id,
                        provider=provider,
                        model_used=f"{provider}-model",  # Could be enhanced to get actual model name
                        response_text=response_text,
                        response_time_ms=response_time_ms,
                    )
                    db.add(response)
                    db.commit()
                    
                    # Send completion for this provider
                    done_data = {
                        "type": "response",
                        "provider": provider,
                        "text": response_text,
                        "done": True,
                    }
                    yield {
                        "event": "message",
                        "data": json.dumps(done_data)
                    }
                    
                except Exception as e:
                    logger.error(f"Error processing {provider}: {str(e)}", exc_info=True)
                    error_data = {
                        "type": "error",
                        "provider": provider,
                        "message": str(e),
                    }
                    yield {
                        "event": "error",
                        "data": json.dumps(error_data)
                    }
            
            # Process providers sequentially (streaming chunks in real-time)
            # Note: True concurrency with async generators is complex, this works well for now
            for provider in providers:
                if provider in api_keys:
                    async for item in process_provider(provider):
                        yield item
            
            # Send final completion event
            completion_data = {
                "type": "complete",
                "prompt_id": str(prompt.id),
            }
            yield {
                "event": "message",
                "data": json.dumps(completion_data)
            }
                
        except Exception as e:
            logger.error(f"Error in generate_llm_responses: {str(e)}", exc_info=True)
            error_data = {
                "type": "error",
                "message": str(e),
            }
            yield {
                "event": "error",
                "data": json.dumps(error_data)
            }
    
    return EventSourceResponse(generate_llm_responses())


@router.get("/{prompt_id}")
async def get_prompt(
    prompt_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get a specific prompt with all responses."""
    prompt = db.query(Prompt).filter(
        Prompt.id == uuid.UUID(prompt_id),
        Prompt.user_id == uuid.UUID(current_user_id),
    ).first()
    
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found",
        )
    
    responses = db.query(LLMResponse).filter(LLMResponse.prompt_id == prompt.id).all()
    
    return {
        "id": str(prompt.id),
        "prompt_text": prompt.prompt_text,
        "created_at": prompt.created_at.isoformat(),
        "responses": [
            {
                "id": str(r.id),
                "provider": r.provider,
                "model_used": r.model_used,
                "response_text": r.response_text,
                "response_time_ms": r.response_time_ms,
                "error_message": r.error_message,
                "created_at": r.created_at.isoformat(),
            }
            for r in responses
        ],
    }


@router.get("")
async def get_prompts(
    page: int = 1,
    limit: int = 20,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get prompt history for current user."""
    offset = (page - 1) * limit
    
    prompts = db.query(Prompt).filter(
        Prompt.user_id == uuid.UUID(current_user_id),
    ).order_by(Prompt.created_at.desc()).offset(offset).limit(limit).all()
    
    total = db.query(Prompt).filter(Prompt.user_id == uuid.UUID(current_user_id)).count()
    
    return {
        "prompts": [
            {
                "id": str(p.id),
                "prompt_text": p.prompt_text[:100] + "..." if len(p.prompt_text) > 100 else p.prompt_text,
                "created_at": p.created_at.isoformat(),
            }
            for p in prompts
        ],
        "total": total,
        "page": page,
        "limit": limit,
    }

