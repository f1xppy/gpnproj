from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    mysql_user: str = Field(
        default='gpn',
        env='MYSQL_USER',
        alias='MYSQL_USER'
    )

    mysql_host: str = Field(
        default='localhost',
        env='MYSQL_HOST',
        alias='MYSQL_HOST'
    )

    mysql_password: str = Field(
        default='gpnpa$$Word',
        env='MYSQL_PASSWORD',
        alias='MYSQL_PASSWORD'
    )

    mysql_database: str = Field(
        default='gpn',
        env='MYSQL_DATABASE',
        alias='MYSQL_DATABASE'
    )

    redis_url: str = Field(
        default='redis://localhost:6379/0',
        env='REDIS_URL',
        alias='REDIS_URL'
    )

    class Config:
        env_file = ".env"


def load_config():
    return Config()
