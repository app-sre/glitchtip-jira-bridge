import logging
from typing import TYPE_CHECKING, Any

import boto3
from celery import Celery
from jira import JIRA

from .backends.db import (
    Db,
    IssueCache,
    Limits,
)
from .backends.jira import create_issue
from .config import settings
from .metrics import received_alerts
from .models import Attachment

if TYPE_CHECKING:
    from celery.app.task import Task

log = logging.getLogger(__name__)
app = Celery(
    "tasks",
    broker=settings.broker_url,
    broker_transport_options={
        "region": settings.broker_aws_region,
        "predefined_queues": {
            "celery": {
                "url": settings.sqs_url,
                "access_key_id": settings.broker_aws_access_key_id,
                "secret_access_key": settings.broker_aws_secret_access_key,
            }
        },
    },
    broker_connection_retry_on_startup=True,
    worker_enable_remote_control=False,
    worker_log_format="[%(asctime)s: GJB] %(message)s",
    task_serializer="json",
    result_serializer="json",
    event_serializer="json",
    accept_content=["application/json"],
    result_accept_content=["application/json"],
)


@app.task(bind=True)
def create_jira_ticket(  # pylint: disable=too-many-arguments
    self: Task,
    jira_project_key: str,
    issue: dict[str, Any],
    custom_labels: list[str],
    components: list[str],
    issue_type: str,
) -> None:
    """Create a Jira ticket."""
    attachment = Attachment.model_validate(issue)
    log.info(
        f"Handling alert '{attachment.text}' for '{jira_project_key}' jira project"
    )
    received_alerts.labels(jira_project_key).inc()
    try:
        dynamodb_service_resource = boto3.resource(
            "dynamodb",
            endpoint_url=settings.dynamodb_url,
            region_name=settings.dynamodb_aws_region,
            aws_access_key_id=settings.dynamodb_aws_access_key_id,
            aws_secret_access_key=settings.dynamodb_aws_secret_access_key,
        )
        create_issue(
            project_key=jira_project_key,
            summary=attachment.title,
            description=f"{attachment.text}\n-----\nGlitchtip issue: {attachment.title_link}",
            url=attachment.title_link,
            labels=["glitchtip", *attachment.labels, *custom_labels],
            components=components,
            issue_type=issue_type,
            jira=JIRA(
                server=settings.jira_api_url,
                basic_auth=(settings.jira_api_username, settings.jira_api_token),
            ),
            issue_cache=IssueCache(
                backend=Db(
                    dynamodb_service_resource=dynamodb_service_resource,
                    table_name=settings.cache_table_name,
                ),
                ttl=settings.cache_ttl,
            ),
            limits=Limits(
                backend=Db(
                    dynamodb_service_resource=dynamodb_service_resource,
                    table_name=settings.limits_table_name,
                ),
                limit=settings.issues_per_project_limit,
            ),
        )
    except Exception as exc:
        log.exception("Failed to create Jira ticket")
        raise self.retry(
            exc=exc, countdown=settings.retry_delay, max_retries=settings.retries
        ) from exc
