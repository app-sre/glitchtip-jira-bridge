from glitchtip_jira_bridge.models import GlitchtipAlert


def test_glitchtip_alert(glitchtip_alert: GlitchtipAlert) -> None:
    assert glitchtip_alert.attachments[0].labels == [
        "project:test-project",
        "release:test-release",
        "environment:test-environment",
    ]
