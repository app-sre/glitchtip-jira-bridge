import logging
from collections.abc import Callable
from typing import Annotated

from celery import Task
from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from glitchtip_jira_bridge.models import GlitchtipAlert
from glitchtip_jira_bridge.tasks import create_jira_ticket as create_jira_ticket_task

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
    create_jira_ticket: Annotated[Task, Depends(get_create_jira_ticket_func)],
    labels: Annotated[list[str] | None, Query()] = None,
    components: Annotated[list[str] | None, Query()] = None,
    issue_type: Annotated[str | None, Query()] = None,
) -> None:
    """Create new snapshot on all volumes."""
    for attachment in alert.attachments:
        create_jira_ticket.delay(
            jira_project_key,
            attachment,
            labels or [],
            components or [],
            issue_type or "Bug",
        )
