import logging

import glitchtip_jira_bridge.main  # ruff: ignore[unused-import]
from glitchtip_jira_bridge.logging_utils import RedactTokenQueryParamFilter


def test_uvicorn_access_logger_has_redact_token_filter() -> None:
    access_logger = logging.getLogger("uvicorn.access")

    assert any(
        isinstance(f, RedactTokenQueryParamFilter) for f in access_logger.filters
    )
