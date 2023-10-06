from prometheus_client import start_http_server

# import celery app to start the worker
from .tasks import app  # noqa: F401 # pylint: disable=W0611

start_http_server(8000)
