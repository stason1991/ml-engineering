import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
  DB_HOST: str
  DB_PORT: int = 5432
  DB_USER: str
  DB_PASS: str
  DB_NAME: str


  @property
  def DATABASE_URL_asyncpg(self) -> str:
    return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

  @property
  def DATABASE_URL_psycopg(self) -> str:
    return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

  model_config = SettingsConfigDict(env_file=os.path.join(os.path.dirname(__file__), ".env"), extra="ignore")

@lru_cache()
def get_settings() -> Settings:
  return Settings()