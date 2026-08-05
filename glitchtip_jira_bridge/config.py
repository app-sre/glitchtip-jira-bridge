# ruff: file-ignore[hardcoded-password-string]
from datetime import timedelta
from pathlib import Path

from pydantic_settings import BaseSettings

# OpenShift mounts the glitchtip-jira-bridge-secret Secret here as files (one
# per key) instead of injecting it via environment variables. Not present in
# local/dev environments, which keep using env vars (see docker-compose.yml).
SECRETS_DIR = Path("/var/run/secrets/glitchtip-jira-bridge")


def resolve_secrets_dir(path: Path) -> Path | None:
    """Return `path` if it exists, else None (avoids a pydantic-settings warning)."""
    return path if path.is_dir() else None


class Settings(BaseSettings):
    # app config
    debug: bool = False
    root_path: str = ""

    # fastapi auth config
    api_keys: list[str] = []

    # worker config
    broker_url: str = "sqs://localhost:4566"
    sqs_url: str = "http://localhost:4566/000000000000/app-interface"
    broker_aws_region: str = "us-east-1"
    broker_aws_access_key_id: str = "localstack"
    broker_aws_secret_access_key: str = "localstack"
    retries: int | None = None
    retry_delay: int = 10

    # cache config
    dynamodb_url: str = "http://localhost:4566"
    dynamodb_aws_region: str = "us-east-1"
    dynamodb_aws_access_key_id: str = "localstack"
    dynamodb_aws_secret_access_key: str = "localstack"
    cache_table_name: str = "gjb"
    cache_ttl: int = int(timedelta(hours=2).total_seconds())
    limits_table_name: str = "limits"
    issues_per_project_limit: int = 10

    # jira config
    jira_api_url: str = "https://issues.stage.redhat.com"
    jira_api_username: str = ""
    jira_api_token: str = ""

    # worker metrics config
    worker_metrics_port: int = 8000

    # pydantic config
    model_config = {
        "env_prefix": "gjb_",
        "secrets_dir": resolve_secrets_dir(SECRETS_DIR),
    }


settings = Settings()
