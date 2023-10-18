import logging
from collections.abc import Callable

from celery import Task
from fastapi import (
    APIRouter,
    Depends,
)

from ...models import GlitchtipAlert
from ...tasks import create_jira_ticket as create_jira_ticket_task

router = APIRouter()
log = logging.getLogger(__name__)


def get_create_jira_ticket_func() -> Callable:
    """Return a function that creates a Jira ticket."""
    return create_jira_ticket_task


@router.post(
    "/alert/{jira_project_key}",
    summary="Create a Jira ticket.",
    status_code=202,
)
def handle_alert(
    jira_project_key: str,
    alert: GlitchtipAlert,
    create_jira_ticket: Task = Depends(get_create_jira_ticket_func),
) -> None:
    """Create new snapshot on all volumes."""
    for attachment in alert.attachments:
        create_jira_ticket.delay(jira_project_key, attachment)
