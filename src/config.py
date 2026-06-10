from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    db_url: str
    anthropic_api_key: str
    adzuna_app_id: str
    adzuna_app_key: str
    kariyernet_api_key: str
    llm_provider: str 
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

print(settings.llm_provider)
