from typing import TYPE_CHECKING

import requests
from celery import Task

from glitchtip_jira_bridge.api.v1.alert import get_create_jira_ticket_func

if TYPE_CHECKING:
    from fastapi.testclient import TestClient
    from pytest_mock import MockerFixture


def test_handle_alert(
    mocker: MockerFixture, config_api_key: list[str], client: TestClient
) -> None:
    task_mock = mocker.MagicMock(Task, autospec=True)
    client.app.dependency_overrides[  # type: ignore[attr-defined]
        get_create_jira_ticket_func
    ] = lambda: task_mock
    response = client.post(
        "/api/v1/alert/JIRA-PROJECT-KEY",
        headers={"Authorization": f"Bearer {config_api_key[0]}"},
        json={
            "text": "test text",
            "attachments": [
                {
                    "title": "issue title",
                    "title_link": "https://glitchtip.devshift.net/app-sre/issues/12345",
                    "text": "issue text",
                    "image_url": "https://google.com",
                    "color": "#FF0000",
                    "fields": [
                        {
                            "title": "test",
                            "value": "test",
                            "short": True,
                        },
                        {
                            "title": "Project",
                            "value": "test-project",
                            "short": True,
                        },
                    ],
                    "mrkdown_in": ["text"],
                }
            ],
        },
        params={
            "labels": ["test-label"],
            "components": ["test-component", "test-component-2"],
            "issue_type": "issue-type",
        },
    )
    assert response.status_code == requests.codes.accepted
    task_mock.delay.assert_called_once_with(
        "JIRA-PROJECT-KEY",
        mocker.ANY,
        ["test-label"],
        ["test-component", "test-component-2"],
        "issue-type",
    )


def test_handle_alert_real_glitchtip_payload(
    mocker: MockerFixture, config_api_key: list[str], client: TestClient
) -> None:
    """Real GlitchTip 6.2.x payload: no top-level `alias`, no attachment `text`."""
    task_mock = mocker.MagicMock(Task, autospec=True)
    client.app.dependency_overrides[  # type: ignore[attr-defined]
        get_create_jira_ticket_func
    ] = lambda: task_mock
    response = client.post(
        "/api/v1/alert/CCXDEV",
        headers={"Authorization": f"Bearer {config_api_key[0]}"},
        json={
            "text": "GlitchTip Alert",
            "attachments": [
                {
                    "title": "kafka: error while consuming ccx.ocp.results/0",
                    "title_link": "https://glitchtip.devshift.net/ccx/issues/4580574",
                    "color": "#e52b50",
                    "fields": [
                        {
                            "title": "Project",
                            "value": "ccx-notification-writer",
                            "short": True,
                        },
                        {
                            "title": "Environment",
                            "value": "prod",
                            "short": True,
                        },
                    ],
                    "mrkdown_in": ["text"],
                }
            ],
        },
    )
    assert response.status_code == requests.codes.accepted
    task_mock.delay.assert_called_once_with("CCXDEV", mocker.ANY, [], [], "Bug")


def test_handle_alert_no_optional_fields(
    mocker: MockerFixture, config_api_key: list[str], client: TestClient
) -> None:
    task_mock = mocker.MagicMock(Task, autospec=True)
    client.app.dependency_overrides[  # type: ignore[attr-defined]
        get_create_jira_ticket_func
    ] = lambda: task_mock
    response = client.post(
        "/api/v1/alert/JIRA-PROJECT-KEY",
        headers={"Authorization": f"Bearer {config_api_key[0]}"},
        json={
            "text": "test text",
            "attachments": [
                {
                    "title": "issue title",
                    "title_link": "https://glitchtip.devshift.net/app-sre/issues/12345",
                    "text": "issue text",
                    "image_url": "https://google.com",
                    "color": "#FF0000",
                    "fields": [
                        {
                            "title": "test",
                            "value": "test",
                            "short": True,
                        },
                        {
                            "title": "Project",
                            "value": "test-project",
                            "short": True,
                        },
                    ],
                    "mrkdown_in": ["text"],
                }
            ],
        },
    )
    assert response.status_code == requests.codes.accepted
    task_mock.delay.assert_called_once_with(
        "JIRA-PROJECT-KEY", mocker.ANY, [], [], "Bug"
    )
