import os
import pytest
import requests
import mailtriage as mt

def _ollama_reachable(base_url: str) -> bool:
    try:
        return requests.get(f"{base_url.rstrip('/')}/api/tags", timeout=2).ok
    except requests.RequestException:
        return False

@pytest.mark.integration
def test_ollama_smoke_structured_json():
    if os.getenv("RUN_OLLAMA_INTEGRATION") != "1":
        pytest.skip("Set RUN_OLLAMA_INTEGRATION=1 to run Ollama integration tests.")

    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

    if not _ollama_reachable(base_url):
        pytest.skip(f"Ollama not reachable at {base_url}")

    client = mt.OllamaClient(base_url=base_url, model=model, timeout_s=60)
    result, _ = client.triage_email({
        "from": "Test <test@example.com>",
        "to": "You <you@example.com>",
        "subject": "hello",
        "date": "Fri, 20 Feb 2026 10:00:00 -0800",
        "message_id": "<test-1@example.com>",
        "body_excerpt": "Just a quick note: can you reply when you can?",
    })

    # Just ensure schema parse works and bucket is valid
    assert result.bucket in mt.BUCKETS