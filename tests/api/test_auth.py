import requests
from fastapi.testclient import TestClient


def test_authentication_via_header(
    config_api_key: list[str], client: TestClient
) -> None:
    for secret in config_api_key:
        response = client.get("/api/v1/", headers={"Authorization": f"Bearer {secret}"})
    assert response.status_code == requests.codes.ok
    response = client.get("/api/v1/", headers={"Authorization": "Bearer wrong"})
    assert response.status_code == requests.codes.unauthorized


def test_authentication_via_query_param(
    config_api_key: list[str], client: TestClient
) -> None:
    for secret in config_api_key:
        response = client.get("/api/v1/", params={"token": secret})
    assert response.status_code == requests.codes.ok
    response = client.get("/api/v1/", params={"token": "wrong"})
    assert response.status_code == requests.codes.unauthorized


def test_debug_no_authentication(config_debug: bool, client: TestClient) -> None:
    response = client.get(
        "/api/v1/", headers={"Authorization": "Bearer does-not-matter"}
    )
    assert response.status_code == requests.codes.ok
    response = client.get("/api/v1/")
    assert response.status_code == requests.codes.ok
