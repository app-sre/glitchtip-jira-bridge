from pydantic_settings import BaseSettings


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
    retries: int = 3
    retry_delay: int = 10

    # cache config
    dynamodb_url: str = "http://localhost:4566"
    dynamodb_table_name: str = "gjb"
    dynamodb_aws_region: str = "us-east-1"
    dynamodb_aws_access_key_id: str = "localstack"
    dynamodb_aws_secret_access_key: str = "localstack"
    cache_ttl: int = 60 * 60 * 2  # 2 hours

    # jira config
    jira_api_url: str = "https://issues.stage.redhat.com"
    jira_api_key: str = ""

    # pydantic config
    model_config = {"env_prefix": "gjb_"}


settings = Settings()
