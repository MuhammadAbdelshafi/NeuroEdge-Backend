import logging
import time
from openai import OpenAI
from app.modules.summarization.config import summarization_settings

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.client = OpenAI(
            base_url=summarization_settings.OPENROUTER_BASE_URL,
            api_key=summarization_settings.get_api_key,
        )
        self.model = summarization_settings.SUMMARIZATION_MODEL

    def generate(self, prompt: str) -> str:
        """
        Send prompt to OpenRouter via OpenAI SDK.
        """
        for attempt in range(summarization_settings.MAX_RETRIES):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1024,
                )
                
                content = response.choices[0].message.content
                if content:
                    return content
                return ""
                    
            except Exception as e:
                logger.error(f"OpenRouter API Request Failed: {e}")
                if attempt < summarization_settings.MAX_RETRIES - 1:
                    time.sleep(summarization_settings.RETRY_DELAY_SECONDS)
                else:
                    raise e
                    
        raise Exception("Max retries exceeded for OpenRouter API")
