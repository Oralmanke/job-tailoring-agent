from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the whole app.

    Every tunable value (URLs, model names, thresholds, search defaults) lives
    here so there is a single place to change behaviour. Values are read from
    environment variables / a local .env file, with sane defaults below.
    """

    # --- Database ---
    db_url: str

    # --- LLM providers ---
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    llm_provider: str = "anthropic"
    model_name: str = "claude-sonnet-5"

    # --- Job source API credentials ---
    adzuna_app_id: str = ""
    adzuna_app_key: str = ""
    kariyernet_api_key: str = ""

    # --- Scraper defaults (previously hardcoded in the fetch functions) ---
    search_query: str = "ai ml software"
    country: str = "de"
    results_per_page: int = 100
    adzuna_base_url: str = "https://api.adzuna.com/v1/api/jobs"
    remotive_base_url: str = "https://remotive.com/api/remote-jobs"
    http_timeout: int = 10

    # --- Matching / evaluation ---
    embedding_model: str = "all-MiniLM-L6-v2"
    coverage_threshold: float = 0.5

    # --- Tailoring / API ---
    default_cv_path: str = "data/cv.pdf"
    output_dir: str = "output"

    # --- Resilience ---
    max_retries: int = 3

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
