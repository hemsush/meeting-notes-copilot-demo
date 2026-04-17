from fastapi.testclient import TestClient

from app.main import app
from app import service

client = TestClient(app)


def setup_function() -> None:
    """Clear in-memory wiki store before each test function."""
    service._wiki_store.clear()


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


# --- Wiki endpoint tests ---


def test_create_wiki_entry_success() -> None:
    payload = {
        "ticket_id": "JIRA-300",
        "notes": "Alice will prepare release notes by Monday. Risk: third-party API downtime.",
    }
    response = client.post("/wiki", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["ticket_id"] == "JIRA-300"
    assert body["title"] == "Meeting Notes – JIRA-300"
    assert "summary" in body
    assert isinstance(body["action_items"], list)
    assert isinstance(body["risks"], list)
    assert "created_at" in body


def test_create_wiki_entry_with_custom_title() -> None:
    payload = {
        "ticket_id": "JIRA-301",
        "notes": "Bob needs to update the deployment script.",
        "title": "Sprint 5 Planning",
    }
    response = client.post("/wiki", json=payload)

    assert response.status_code == 201
    assert response.json()["title"] == "Sprint 5 Planning"


def test_create_wiki_entry_overwrites_existing() -> None:
    payload = {"ticket_id": "JIRA-302", "notes": "Team will review test coverage."}
    first = client.post("/wiki", json=payload).json()
    assert first["updated_at"] is None

    updated_payload = {"ticket_id": "JIRA-302", "notes": "Updated: QA should sign off by Friday.", "title": "Updated Notes"}
    response = client.post("/wiki", json=updated_payload)

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Updated Notes"
    assert body["created_at"] == first["created_at"]
    assert body["updated_at"] is not None


def test_create_wiki_entry_missing_notes() -> None:
    response = client.post("/wiki", json={"ticket_id": "JIRA-303"})
    assert response.status_code == 422


def test_list_wiki_entries_empty() -> None:
    response = client.get("/wiki")
    assert response.status_code == 200
    assert response.json() == []


def test_list_wiki_entries_returns_all() -> None:
    client.post("/wiki", json={"ticket_id": "JIRA-400", "notes": "Alice will finish docs."})
    client.post("/wiki", json={"ticket_id": "JIRA-401", "notes": "Bob needs to run tests."})

    response = client.get("/wiki")
    assert response.status_code == 200
    ticket_ids = {e["ticket_id"] for e in response.json()}
    assert {"JIRA-400", "JIRA-401"}.issubset(ticket_ids)


def test_get_wiki_entry_success() -> None:
    client.post("/wiki", json={"ticket_id": "JIRA-500", "notes": "Team should review the PR by tomorrow."})
    response = client.get("/wiki/JIRA-500")

    assert response.status_code == 200
    assert response.json()["ticket_id"] == "JIRA-500"


def test_get_wiki_entry_not_found() -> None:
    response = client.get("/wiki/JIRA-NONEXISTENT")
    assert response.status_code == 404
