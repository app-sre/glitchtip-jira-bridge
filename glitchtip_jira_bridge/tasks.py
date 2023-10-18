import logging

import boto3
from celery import Celery
from celery.app.task import Task
from jira import JIRA

from .backends.db import (
    Db,
    IssueCache,
    Limits,
)
from .backends.jira import create_issue
from .config import settings
from .metrics import processed_alerts
from .models import GlitchtipAlert

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
    # support pydantic models
    task_serializer="pickle",
    result_serializer="pickle",
    event_serializer="json",
    accept_content=["application/json", "application/x-python-serialize"],
    result_accept_content=["application/json", "application/x-python-serialize"],
)


@app.task(bind=True)
def create_jira_ticket(
    self: Task, jira_project_key: str, alert: GlitchtipAlert
) -> None:
    """Create a Jira ticket."""
    log.info(
        f"Handling alert '{alert.issue_text}' for '{jira_project_key}' jira project"
    )
    processed_alerts.labels(jira_project_key).inc()
    try:
        dyn_resource = boto3.resource(
            "dynamodb",
            endpoint_url=settings.dynamodb_url,
            region_name=settings.dynamodb_aws_region,
            aws_access_key_id=settings.dynamodb_aws_access_key_id,
            aws_secret_access_key=settings.dynamodb_aws_secret_access_key,
        )
        create_issue(
            project_key=jira_project_key,
            summary=alert.issue_title,
            description=f"{alert.issue_text}\n-----\nGlitchtip issue: {alert.issue_url}",
            url=alert.issue_url,
            labels=["glitchtip"] + alert.labels,
            jira=JIRA(
                server=settings.jira_api_url,
                token_auth=settings.jira_api_key,
            ),
            issue_cache=IssueCache(
                backend=Db(
                    dyn_resource=dyn_resource,
                    table_name=settings.cache_table_name,
                ),
                ttl=settings.cache_ttl,
            ),
            limits=Limits(
                backend=Db(
                    dyn_resource=dyn_resource,
                    table_name=settings.limits_table_name,
                ),
                limit=settings.issues_per_project_limit,
            ),
        )
    except Exception as exc:
        log.exception("Failed to create Jira ticket")
        raise self.retry(
            exc=exc, countdown=settings.retry_delay, max_retries=settings.retries
        )
