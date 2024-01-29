#__________________2.13.Env_______________________________________________________________________________________
from typing import Any

from pydantic import ConfigDict, field_validator, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = "postgresql+asyncpg://postgres:11111111!@localhost:5432/contacts_db"
    SECRET_KEY_JWT: str = "1234567890"
    ALGORITHM: str = "HS256"
    MAIL_USERNAME: EmailStr = "postgres@meail.com"
    MAIL_PASSWORD: str = "postgres"
    MAIL_FROM: str = "postgres"
    MAIL_PORT: int = 567234
    MAIL_SERVER: str = "postgres"
    REDIS_DOMAIN: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    #____________________________5.13____cloudinary___
    CLD_NAME: str = 'dv3yqbj4b'
    CLD_API_KEY: int = 735932881259231
    CLD_API_SECRET: str = "secret"
    #____________________________5.13____cloudinary___|

    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorithm(cls, v: Any):
        if v not in ["HS256", "HS512"]:
            raise ValueError("algorithm must be HS256 or HS512")
        return v


    model_config = ConfigDict(extra='ignore', env_file=".env", env_file_encoding="utf-8")  # noqa


config = Settings()
#__________________2.13.Env_______________________________________________________________________________________|

# class Config:
#     DATABASE_URL = "postgresql+asyncpg://postgres:t5r4e3w2Q!@localhost:5432/contacts_db"

# config = Config