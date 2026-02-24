import json
from unittest.mock import patch, MagicMock
import mailtriage as mt

def _fake_ollama_response(content_json: dict):
    # Mimic Ollama /api/chat response shape
    return {
        "message": {"role": "assistant", "content": json.dumps(content_json)},
        "prompt_eval_count": 123,
        "eval_count": 45,
        "total_duration": 10_000_000,  # ns
        "prompt_eval_duration": 4_000_000,
        "eval_duration": 6_000_000,
    }

@patch("mailtriage.requests.post")
def test_ollama_client_parses_structured_json(mock_post):
    good = {
        "bucket": "newsletter_or_marketing",
        "confidence": 0.95,
        "action": "move_to_folder",
        "reason": "Marketing email",
        "signals": ["list_unsubscribe"],
        "auto_move_ok": True,
    }

    mock_resp = MagicMock()
    mock_resp.json.return_value = _fake_ollama_response(good)
    mock_resp.raise_for_status.return_value = None
    mock_post.return_value = mock_resp

    client = mt.OllamaClient(base_url="http://localhost:11434", model="llama3.1:8b")
    parsed, raw = client.triage_email({"subject": "Sale", "body_excerpt": "Buy now"})

    assert parsed.bucket == "newsletter_or_marketing"
    assert parsed.confidence == 0.95
    assert parsed.auto_move_ok is True

    # Ensure we sent schema format + messages
    sent_payload = mock_post.call_args.kwargs["json"]
    assert "format" in sent_payload
    assert "messages" in sent_payload
    assert sent_payload["model"] == "llama3.1:8b"