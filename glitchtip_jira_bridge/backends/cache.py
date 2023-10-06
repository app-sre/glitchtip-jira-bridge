import time

from boto3.resources.base import ServiceResource

from ..models import Issue


class Cache:
    def __init__(self, dyn_resource: ServiceResource, table_name: str) -> None:
        self.table = dyn_resource.Table(table_name)
        self.table.load()

    def get(self, pk: str) -> str | None:
        response = self.table.get_item(
            Key={"key": pk},
            ReturnConsumedCapacity="NONE",
            ProjectionExpression="v",
        )

        if item := response.get("Item"):
            return item["v"]
        return None

    def set(self, pk: str, value: str, ttl: int) -> None:
        self.table.put_item(Item={"key": pk, "v": value, "ttl": ttl})


class IssueCache:
    def __init__(self, cache_backend: Cache, ttl: int):
        self.cache_backend = cache_backend
        self.ttl = ttl

    def get(self, glitchtip_issue_url: str) -> Issue | None:
        if jira_key := self.cache_backend.get(glitchtip_issue_url):
            return Issue(
                jira_key=jira_key,
                glitchtip_issue_url=glitchtip_issue_url,
            )
        return None

    def set(self, jira_key: str, issue_url: str) -> None:
        self.cache_backend.set(
            pk=issue_url, value=jira_key, ttl=int(time.time()) + self.ttl
        )
