from glitchtip_jira_bridge.models import GlitchtipAlert


def test_glitchtip_alert(glitchtip_alert: GlitchtipAlert) -> None:
    alert = GlitchtipAlert(
        **dict(
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
            ],
        ),
    )
    assert glitchtip_alert.labels == [
        "project:test-project",
        "release:test-release",
        "environment:test-environment",
    ]
    assert glitchtip_alert.issue_title == "issue title"
    assert (
        glitchtip_alert.issue_url
        == "https://glitchtip.devshift.net/app-sre/issues/12345"
    )
    assert glitchtip_alert.issue_text == "issue text"
