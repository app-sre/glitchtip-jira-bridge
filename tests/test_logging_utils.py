import logging

from glitchtip_jira_bridge.logging_utils import RedactTokenQueryParamFilter


def _make_record(path_with_query: str) -> logging.LogRecord:
    return logging.LogRecord(
        name="uvicorn.access",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg='%s - "%s %s HTTP/%s" %d',
        args=("127.0.0.1:12345", "POST", path_with_query, "1.1", 202),
        exc_info=None,
    )


def test_redacts_token_query_param() -> None:
    record = _make_record("/api/v1/alert/PROJECT?token=super-secret-key")

    assert RedactTokenQueryParamFilter().filter(record) is True
    assert record.getMessage() == (
        '127.0.0.1:12345 - "POST /api/v1/alert/PROJECT?token=REDACTED HTTP/1.1" 202'
    )


def test_redacts_token_query_param_among_other_params() -> None:
    record = _make_record("/api/v1/alert/PROJECT?labels=foo&token=super-secret-key")

    assert RedactTokenQueryParamFilter().filter(record) is True
    assert record.getMessage() == (
        '127.0.0.1:12345 - "POST /api/v1/alert/PROJECT?labels=foo&token=REDACTED '
        'HTTP/1.1" 202'
    )


def test_leaves_requests_without_token_untouched() -> None:
    record = _make_record("/healthz?foo=bar")

    assert RedactTokenQueryParamFilter().filter(record) is True
    assert record.getMessage() == (
        '127.0.0.1:12345 - "POST /healthz?foo=bar HTTP/1.1" 202'
    )
