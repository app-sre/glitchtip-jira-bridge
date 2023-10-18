from prometheus_client import Counter

received_alerts = Counter(
    "gjb_received_alerts", "Received alerts by Jira project", ["jira_project_key"]
)
limit_reached = Counter(
    "gjb_limit_reached", "Limit reached by Jira project", ["jira_project_key"]
)
tickets_created = Counter(
    "gjb_tickets_created", "Tickets created by Jira project", ["jira_project_key"]
)
tickets_reopened = Counter(
    "gjb_tickets_reopened", "Tickets reopened by Jira project", ["jira_project_key"]
)
