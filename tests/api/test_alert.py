from celery import Task
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from glitchtip_jira_bridge.api.v1.alert import get_create_jira_ticket_func


def test_handle_alert(
    mocker: MockerFixture, config_api_key: list[str], client: TestClient
) -> None:
    task_mock = mocker.MagicMock(Task, autospec=True)
    client.app.dependency_overrides[  # type: ignore
        get_create_jira_ticket_func
    ] = lambda: task_mock
    response = client.post(
        "/api/v1/alert/JIRA-PROJECT-KEY",
        headers={"Authorization": f"Bearer {config_api_key[0]}"},
        json=dict(
            alias="test alias",
            text="test text",
            attachments=[
                dict(
                    title="issue title",
                    title_link="https://glitchtip.devshift.net/app-sre/issues/12345",
                    text="issue text",
                    image_url="https://google.com",
                    color="#FF0000",
                    fields=[
                        dict(
                            title="test",
                            value="test",
                            short=True,
                        ),
                        dict(
                            title="Project",
                            value="test-project",
                            short=True,
                        ),
                    ],
                    mrkdown_in=["text"],
                )
            ],
        ),
    )
    assert response.status_code == 202
    task_mock.delay.assert_called_once_with("JIRA-PROJECT-KEY", mocker.ANY)
