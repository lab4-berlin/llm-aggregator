"""Anthropic API client for streaming responses."""
from anthropic import Anthropic
import logging

logger = logging.getLogger(__name__)


async def stream_anthropic_response(api_key: str, prompt: str, model: str = "claude-3-haiku-20240307"):
    """
    Stream response from Anthropic API.
    
    Args:
        api_key: Anthropic API key
        prompt: User prompt
        model: Model to use (default: claude-3-haiku-20240307)
    
    Yields:
        str: Chunks of response text
    """
    try:
        client = Anthropic(api_key=api_key)
        
        with client.messages.stream(
            model=model,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        ) as stream:
            for text in stream.text_stream:
                yield text
                
    except Exception as e:
        logger.error(f"Anthropic API error: {str(e)}")
        raise


async def test_anthropic_key(api_key: str) -> bool:
    """Test if Anthropic API key is valid."""
    try:
        client = Anthropic(api_key=api_key)
        # Make a minimal API call to test the key
        client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=10,
            messages=[{"role": "user", "content": "test"}]
        )
        return True
    except Exception as e:
        logger.error(f"Anthropic key test failed: {str(e)}")
        return False

