from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import timezone

from enum import Enum

from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

from typing import NewType


APP_DIR = Path(__file__).parent


NotSpecifiedParam = NewType('NotSpecifiedParam', type)


class TimeZone(Enum):
    UTC = timezone(offset=timedelta(hours=0), name='UTC')
    MSC = timezone(offset=timedelta(hours=+3), name='MSC')


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    ENGINE_ECHO: bool = True
    ENGINE_POOL_SIZE: int = 5
    ENGINE_MAX_OVERFLOW: int = 10
    SESSION_AUTOFLUSH: bool = True
    SESSION_EXPIRE_ON_COMMIT: bool = False

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

    @property
    def connect_args(self) -> dict[str, str]:
        return {
            'options': '-c timezone=utc',
        }

    @property
    def TZ(self) -> timezone:
        return TimeZone.UTC.value

    def get_datetime_now(self) -> datetime:
        return datetime.now(tz=self.TZ)

    def get_date_today(self) -> date:
        return datetime.now(tz=self.TZ).date()

    model_config = SettingsConfigDict(env_file=APP_DIR / '.env')


class TestSettings(Settings):

    model_config = SettingsConfigDict(env_file=APP_DIR / '.env.test')


settings = Settings()  # type: ignore[call-arg]
test_settings = TestSettings()  # type: ignore[call-arg]
