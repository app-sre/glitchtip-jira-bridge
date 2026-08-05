import logging
import re
from typing import override

_TOKEN_QUERY_PARAM_RE = re.compile(r"(?i)([?&]token=)[^&\s]*")


class RedactTokenQueryParamFilter(logging.Filter):
    """Redact the `token` query parameter from log records.

    The `/api/v1/alert` endpoint accepts the API key as a `?token=` query
    parameter (Glitchtip cannot send custom headers), which uvicorn's access
    logger would otherwise write to stdout/container logs in full.
    """

    @override
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.args, tuple):
            record.args = tuple(
                _TOKEN_QUERY_PARAM_RE.sub(r"\1REDACTED", arg)
                if isinstance(arg, str)
                else arg
                for arg in record.args
            )
        return True
