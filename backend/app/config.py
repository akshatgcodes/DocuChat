from pydantic_settings import BaseSettings, SettingsConfigDict

# OpenAI-compatible endpoints, so one client (LangChain's ChatOpenAI) covers all three
PROVIDERS = {
    "groq": ("https://api.groq.com/openai/v1", "openai/gpt-oss-120b"),
    "openai": ("https://api.openai.com/v1", "gpt-4o-mini"),
    "ollama": ("http://localhost:11434/v1", "llama3.2"),
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./data/docuchat.db"
    data_dir: str = "./data"
    app_password: str = ""
    session_secret: str = "dev-insecure-secret"
    frontend_url: str = "http://localhost:5173"
    cross_site_cookies: bool = False

    # Generation
    llm_provider: str = "groq"
    llm_api_key: str = ""
    llm_base_url: str = ""  # defaults to the provider's endpoint
    llm_model: str = ""  # defaults to the provider's model above
    groq_api_key: str = ""  # accepted as an alias for llm_api_key

    # Retrieval. "hash" is a dependency-free stand-in used by the tests.
    embeddings: str = "fastembed"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    top_k: int = 4
    # Cosine similarity of the best chunk below which we refuse to answer. Calibrated on
    # a real paper with bge-small: on-topic questions scored 0.62-0.82, off-topic ones
    # 0.44-0.59 (see docs/DECISIONS.md). The ranges overlap, which is why the model
    # also gets told to decline.
    min_similarity: float = 0.55
    high_similarity: float = 0.7

    max_upload_mb: int = 20
    max_pages: int = 300

    @property
    def llm(self) -> tuple[str, str, str]:
        """(base_url, model, api_key) with provider defaults filled in."""
        base, model = PROVIDERS.get(self.llm_provider, PROVIDERS["openai"])
        key = (
            self.llm_api_key
            or self.groq_api_key
            or ("ollama" if self.llm_provider == "ollama" else "")
        )
        return self.llm_base_url or base, self.llm_model or model, key


settings = Settings()
