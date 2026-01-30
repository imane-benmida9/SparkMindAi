from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    APP_NAME: str = Field(default="AI Recruitment API")
    ENV: str = Field(default="dev")

    # DB
    DATABASE_URL: str

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # CORS (ajouter http://localhost:5173 pour Vite frontend)
    CORS_ORIGINS: str = Field(default="http://localhost:5173,http://localhost:3000,http://localhost:8501")

    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]
    
    # --- OPENAI (optionnel, utilisé si défini) ---
    OPENAI_API_KEY: str | None = Field(default=None)
    EMBEDDING_MODEL: str = Field(default="text-embedding-3-small")

    # --- CHROMA (Vector DB) ---
    CHROMA_PERSIST_DIR: str = Field(default="./chroma_data")
    CHROMA_COLLECTION_CVS: str = Field(default="cvs")
    CHROMA_COLLECTION_OFFRES: str = Field(default="offres")



settings = Settings()