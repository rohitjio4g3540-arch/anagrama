from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_reports_gemini_configuration_without_secret():
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["services"] == "anagrama"
    assert "gemini_configured" in payload

def test_stream_reports_tools_deltas_and_completion():
    response = client.post("/stream", json={"message": "Help me plan research"})
    assert response.status_code == 200
    assert '"type": "tool"' in response.text
    assert '"type": "delta"' in response.text
    assert '"type": "complete"' in response.text
