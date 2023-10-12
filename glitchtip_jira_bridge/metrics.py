from prometheus_client import Counter

processed_alerts = Counter(
    "processed_alerts", "Processed alerts by Jira Project", ["jira_project_key"]
)
