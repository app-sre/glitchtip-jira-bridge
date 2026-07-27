from prometheus_client import start_http_server

from glitchtip_jira_bridge.config import settings

# import celery app to start the worker
from glitchtip_jira_bridge.tasks import (
    app,  # ruff: ignore[unused-import] # pylint: disable=W0611
)

start_http_server(settings.worker_metrics_port)
