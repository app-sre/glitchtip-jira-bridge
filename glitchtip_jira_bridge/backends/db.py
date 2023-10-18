import time
from datetime import (
    datetime,
    timedelta,
)
from typing import Any

from boto3.resources.base import ServiceResource

from ..models import Issue


class Db:
    def __init__(self, dyn_resource: ServiceResource, table_name: str) -> None:
        self.table = dyn_resource.Table(table_name)
        self.table.load()

    def get(self, pk: str) -> dict | None:
        response = self.table.get_item(Key={"key": pk}, ReturnConsumedCapacity="NONE")
        return response.get("Item")

    def set(self, pk: str, data: dict[str, Any]) -> None:
        self.table.put_item(Item={"key": pk, **data})


class IssueCache:
    def __init__(self, backend: Db, ttl: int):
        self.backend = backend
        self.ttl = ttl
        self._jira_key_attr = "jira_key"

    def get(self, glitchtip_issue_url: str) -> Issue | None:
        if item := self.backend.get(glitchtip_issue_url):
            return Issue(
                jira_key=item[self._jira_key_attr],
                glitchtip_issue_url=glitchtip_issue_url,
            )
        return None

    def set(self, jira_key: str, issue_url: str) -> None:
        self.backend.set(
            pk=issue_url,
            data={self._jira_key_attr: jira_key, "ttl": int(time.time()) + self.ttl},
        )


class Limits:
    def __init__(
        self,
        backend: Db,
        limit: int = 10,
        limit_time_span: timedelta = timedelta(hours=1),
    ):
        self.backend = backend
        self.limit = limit
        self.limit_time_span = limit_time_span

    def is_allowed(self, pk: str) -> bool:
        in_one_hour = datetime.utcnow() + self.limit_time_span
        ttl = int(in_one_hour.timestamp())

        if item := self.backend.get(pk):
            # item exists, that means the last request was made within the last hour
            if item["request_count"] >= self.limit:
                # over the limit
                return False

            # update request count and ttl
            self.backend.table.update_item(
                Key={"key": pk},
                UpdateExpression="SET request_count = request_count + :val, #ttl = :ttl",
                ExpressionAttributeValues={":val": 1, ":ttl": ttl},
                ExpressionAttributeNames={"#ttl": "timestamp"},
            )
        else:
            # no limits entry yet, set it
            self.backend.set(pk=pk, data={"request_count": 1, "ttl": ttl})

        return True
