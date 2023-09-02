"""Settings and Configuration for workers. Read more: https://pydantic-docs.helpmanual.io/usage/settings/"""
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):  # type: ignore
    """Main Settings object for application.

    Never instantiate this class directly. Use the get_settings() method below.

    Will read environment variables and docker secrets automatically and map to
    lowercase
    https://pydantic-docs.helpmanual.io/usage/settings/
    """

    # broker example: "amqps://admin123:supersecret987@mq-connect.dev.mtzlab.com:5671"; #  pragma: allowlist secret # noqa: E501
    bigchem_broker_url: str = "amqp://localhost"
    # backend example: "rediss://:password123@redis.dev.mtzlab.com:6379/0?ssl_cert_reqs=CERT_NONE"; #  pragma: allowlist secret  # noqa: E501
    bigchem_backend_url: str = "redis://localhost/0"
    # Workers will grab this many tasks at once. Increase prefetch if tasks are small
    # relative to network overhead time.
    # # https://docs.celeryproject.org/en/stable/userguide/optimizing.html#prefetch-limits
    bigchem_prefetch_multiplier: int = 1
    # Set concurrent number of worker processes. If None defaults to # of logical cores
    # https://docs.celeryq.dev/en/stable/userguide/configuration.html#std-setting-worker_concurrency
    bigchem_worker_concurrency: Optional[int] = 1
    bigchem_default_hessian_dh: float = 5.0e-3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # If not in a docker container with secrets, /var/secrets will not exist
        secrets_dir="/var/secrets" if Path("/var/secrets").is_dir() else None,
        # Required so when operating in the context of another application, like
        # ChemCloud, and it has other .env variables, we don't fail.
        extra="allow",
    )


settings = Settings()
