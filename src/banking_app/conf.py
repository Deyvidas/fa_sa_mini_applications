from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


APP_DIR = Path(__file__).parent


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASS: str

    @property
    def DB_URL(self) -> str:
        url = 'postgresql+psycopg://{user}:{password}@{host}:{port}/{db_name}'
        return url.format(
            user=self.DB_USER,
            password=self.DB_PASS,
            host=self.DB_HOST,
            port=self.DB_PORT,
            db_name=self.DB_NAME,
        )

    model_config = SettingsConfigDict(env_file=APP_DIR / '.env')


settings = Settings()  # type: ignore[call-arg]
