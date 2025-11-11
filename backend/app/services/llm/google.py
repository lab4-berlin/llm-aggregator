"""Google Gemini API client for streaming responses."""
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)


async def stream_google_response(api_key: str, prompt: str, model: str = "gemini-pro"):
    """
    Stream response from Google Gemini API.
    
    Args:
        api_key: Google API key
        prompt: User prompt
        model: Model to use (default: gemini-pro)
    
    Yields:
        str: Chunks of response text
    """
    try:
        genai.configure(api_key=api_key)
        model_instance = genai.GenerativeModel(model)
        
        response = model_instance.generate_content(
            prompt,
            stream=True,
        )
        
        for chunk in response:
            if chunk.text:
                yield chunk.text
                
    except Exception as e:
        logger.error(f"Google API error: {str(e)}")
        raise


async def test_google_key(api_key: str) -> bool:
    """Test if Google API key is valid."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-pro")
        # Make a minimal API call to test the key
        model.generate_content("test")
        return True
    except Exception as e:
        logger.error(f"Google key test failed: {str(e)}")
        return False

