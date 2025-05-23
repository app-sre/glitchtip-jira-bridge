import logging
from typing import TYPE_CHECKING, Any, cast

from jira import JIRA

if TYPE_CHECKING:
    from jira.client import ResultList
    from jira.resources import Issue

from glitchtip_jira_bridge.backends.db import (
    IssueCache,
    Limits,
)
from glitchtip_jira_bridge.metrics import (
    limit_reached,
    tickets_created,
    tickets_reopened,
)

log = logging.getLogger(__name__)


def create_issue(  # pylint: disable=too-many-arguments
    project_key: str,
    summary: str,
    description: str,
    url: str,
    labels: list[str],
    components: list[str],
    issue_type: str,
    jira: JIRA,
    issue_cache: IssueCache,
    limits: Limits,
) -> None:
    if issue_cache.get(url):
        # ticket cached, return
        log.info(f"Ticket for {url} found in cache, skipping")
        return

    # ticket not cached, fetch from jira if it exists
    issues = cast("ResultList[Issue]", jira.search_issues(f"labels='{url}'"))
    if not issues:
        if not limits.is_allowed(project_key):
            limit_reached.labels(project_key).inc()
            log.error(
                f"Cannot create new ticket for {url}, limit reached for {project_key}"
            )
            return
        # create new ticket
        log.info(f"Creating new Jira ticket for {url}")
        extra_fields: dict[str, Any] = {}
        if components:
            extra_fields["components"] = [
                {"name": component} for component in components
            ]
        issue = jira.create_issue(
            project=project_key,
            summary=summary,
            description=description,
            labels=[*labels, url],
            issuetype={"name": issue_type},
            **extra_fields,
        )
        tickets_created.labels(project_key).inc()
        log.info(f"Jira ticket created {issue.key} ({issue.permalink()})")
    else:
        if len(issues) > 1:
            # this should never happen, but just in case
            log.warning(f"Found {len(issues)} issues for {url}, taking the first one")
        issue = issues[0]

        if (
            issue.fields.resolution
            and issue.fields.resolution.name.lower() != "won't do"
        ):
            log.info(f"Reopening ticket for {url}")
            available_transitions = jira.transitions(issue)
            if not available_transitions:
                log.error(f"Cannot reopen ticket for {url}, no transitions available")
                return
            transition_id = available_transitions[0]["id"]  # take the first transition
            jira.transition_issue(issue, transition_id)
            tickets_reopened.labels(project_key).inc()

    # cache Jira ticket id
    log.info(f"Caching ticket {issue.key} for {url}")
    issue_cache.set(jira_key=issue.key, issue_url=url)
