from pydantic_settings import BaseSettings, SettingsConfigDict

class SummarizationSettings(BaseSettings):
    OPENROUTER_API_KEY: str = ""
    # Using Mistral 7B via OpenRouter
    SUMMARIZATION_MODEL: str = "mistralai/mistral-7b-instruct"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # Retry configuration
    MAX_RETRIES: int = 3
    RETRY_DELAY_SECONDS: int = 5
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    @property
    def get_api_key(self):
        return self.OPENROUTER_API_KEY.strip()

summarization_settings = SummarizationSettings()
