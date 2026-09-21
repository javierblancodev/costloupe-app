import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from tests.utils.project import create_random_project


def test_create_project(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {
        "name": "My design",
        "answers": {
            "stage": "greenfield",
            "traffic_volume": "low",
            "requests_per_month": 100000,
            "storage_gb": 5,
            "transfer_gb": 5,
        },
    }
    response = client.post(
        f"{settings.API_V1_STR}/projects/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["recommendation"]["archetype"]
    assert content["recommendation"]["monthly_cost"] >= 0
    assert "id" in content
    assert "owner_id" in content


def test_read_project(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    project = create_random_project(db)
    response = client.get(
        f"{settings.API_V1_STR}/projects/{project.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == str(project.id)
    assert content["owner_id"] == str(project.owner_id)


def test_read_project_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/projects/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_read_projects(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    create_random_project(db)
    create_random_project(db)
    response = client.get(
        f"{settings.API_V1_STR}/projects/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2


def test_read_questionnaire(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/projects/questionnaire",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    questions = response.json()
    assert isinstance(questions, list)
    assert any(question["id"] == "stage" for question in questions)


def test_delete_project(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    project = create_random_project(db)
    response = client.delete(
        f"{settings.API_V1_STR}/projects/{project.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Project deleted successfully"
