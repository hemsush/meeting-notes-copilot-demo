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

    assert set(body.keys()) == {"ticket_id", "summary", "decisions", "action_items", "risks", "participants"}
    assert all("task" in item for item in body["action_items"])


def test_decisions_extracted() -> None:
    payload = {
        "ticket_id": "JIRA-300",
        "notes": "The team decided to postpone the release. Everyone agreed to a two-week sprint.",
    }
    response = client.post("/summarize", json=payload)
    body = response.json()
    assert isinstance(body["decisions"], list)
    assert len(body["decisions"]) >= 1
    decisions_text = " ".join(body["decisions"]).lower()
    assert "decided" in decisions_text or "agreed" in decisions_text


def test_participants_extracted_from_header() -> None:
    payload = {
        "ticket_id": "JIRA-301",
        "notes": "Participants: Alice, Bob, Carol\nAlice will update the docs by Friday.",
    }
    response = client.post("/summarize", json=payload)
    body = response.json()
    assert isinstance(body["participants"], list)
    assert "Alice" in body["participants"]
    assert "Bob" in body["participants"]
    assert "Carol" in body["participants"]


def test_empty_decisions_and_participants_for_minimal_transcript() -> None:
    payload = {
        "ticket_id": "JIRA-302",
        "notes": "We had a meeting today.",
    }
    response = client.post("/summarize", json=payload)
    body = response.json()
    assert isinstance(body["decisions"], list)
    assert isinstance(body["participants"], list)
