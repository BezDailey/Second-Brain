from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    vault_path: str = ""


settings = Settings()
