import pytest
from fastapi.testclient import TestClient

from glitchtip_jira_bridge.config import Settings
from glitchtip_jira_bridge.config import settings as current_settings
from glitchtip_jira_bridge.main import create_app
from glitchtip_jira_bridge.models import (
    Attachment,
    GlitchtipAlert,
)


@pytest.fixture
def settings() -> Settings:
    return current_settings


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


@pytest.fixture
def config_api_key(settings: Settings) -> list[str]:
    settings.api_keys = ["secret-1", "secret-2"]
    return settings.api_keys


@pytest.fixture
def config_debug(settings: Settings) -> bool:
    settings.debug = True
    return settings.debug


@pytest.fixture
def issue() -> Attachment:
    return Attachment(
        **dict(
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
                dict(
                    title="Release",
                    value="test-release",
                    short=True,
                ),
                dict(
                    title="Environment",
                    value="test-environment",
                    short=True,
                ),
            ],
            mrkdown_in=["text"],
        )
    )


@pytest.fixture
def glitchtip_alert(issue: Attachment) -> GlitchtipAlert:
    return GlitchtipAlert(
        **dict(
            alias="test alias",
            text="test text",
            attachments=[issue.model_dump()],
        ),
    )
