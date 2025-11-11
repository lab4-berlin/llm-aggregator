"""OpenAI API client for streaming responses."""
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)


async def stream_openai_response(api_key: str, prompt: str, model: str = "gpt-3.5-turbo"):
    """
    Stream response from OpenAI API.
    
    Args:
        api_key: OpenAI API key
        prompt: User prompt
        model: Model to use (default: gpt-3.5-turbo)
    
    Yields:
        str: Chunks of response text
    """
    try:
        client = OpenAI(api_key=api_key)
        
        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            stream=True,
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
                
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise


async def test_openai_key(api_key: str) -> bool:
    """Test if OpenAI API key is valid."""
    try:
        client = OpenAI(api_key=api_key)
        # Make a minimal API call to test the key
        client.models.list(limit=1)
        return True
    except Exception as e:
        logger.error(f"OpenAI key test failed: {str(e)}")
        return False

