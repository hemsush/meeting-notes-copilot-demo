from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}



def test_summarize_success() -> None:
    payload = {
        "ticket_id": "JIRA-241",
        "notes": "Ravi completed login API. Priya will finish dashboard UI by Friday. DevOps needs to confirm deployment access. Risk: staging environment instability.",
    }
    response = client.post("/summarize", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["ticket_id"] == "JIRA-241"
    assert "summary" in body
    assert isinstance(body["action_items"], list)
    assert isinstance(body["risks"], list)
    assert len(body["action_items"]) >= 1
    assert "staging environment instability" in body["risks"]



def test_summarize_missing_notes() -> None:
    payload = {"ticket_id": "JIRA-241"}
    response = client.post("/summarize", json=payload)
    assert response.status_code == 422



def test_summarize_empty_notes() -> None:
    payload = {"ticket_id": "JIRA-241", "notes": "   "}
    response = client.post("/summarize", json=payload)
    assert response.status_code == 422



def test_response_structure_is_stable() -> None:
    payload = {
        "ticket_id": "JIRA-999",
        "notes": "Team reviewed deployment blockers. QA will validate fixes tomorrow.",
    }
    response = client.post("/summarize", json=payload)
    body = response.json()

    assert set(body.keys()) == {"ticket_id", "summary", "action_items", "risks"}
    assert all("task" in item for item in body["action_items"])
