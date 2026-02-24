import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pytest
import requests

import mailtriage as mt


def _ollama_reachable(base_url: str) -> bool:
    try:
        r = requests.get(f"{base_url.rstrip('/')}/api/tags", timeout=2)
        return r.ok
    except requests.RequestException:
        return False


def _find_corpus_dir() -> Path:
    corpus_path = os.getenv("MAILTRIAGE_CORPUS_DIR")
    if corpus_path:
        return Path(corpus_path)

    here = Path(__file__).parent
    private = here / "corpus_private"
    example = here / "corpus_example"
    return private if private.exists() else example


def _iter_case_paths(corpus_dir: Path) -> List[Path]:
    paths: List[Path] = []
    for p in sorted(corpus_dir.rglob("*.json")):
        # preserve your existing "park drafts" behavior
        if p.name.startswith("_"):
            continue
        if "drafts" in p.parts:
            continue
        paths.append(p)
    return paths


def _load_case(path: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    email_obj = data.get("email")
    expect = data.get("expect", {})
    if not isinstance(email_obj, dict):
        raise ValueError(f"{path} missing top-level 'email' object")
    if not isinstance(expect, dict):
        raise ValueError(f"{path} has non-dict 'expect'")
    return email_obj, expect


def _assert_expectations(case_name: str, result: mt.TriageResult, raw: Dict[str, Any], expect: Dict[str, Any]) -> None:
    debug = {
        "case": case_name,
        "expect": expect,
        "actual": {
            "bucket": result.bucket,
            "confidence": result.confidence,
            "action": result.action,
            "auto_move_ok": result.auto_move_ok,
            "reason": result.reason,
            "signals": result.signals,
        },
        "perf": {
            "prompt_tokens": raw.get("prompt_eval_count"),
            "gen_tokens": raw.get("eval_count"),
            "total_ms": (raw.get("total_duration", 0) or 0) / 1e6,
        },
    }

    def fail(rule: str, expected: Any, actual: Any) -> None:
        raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )

    # ---- bucket checks ----
    bucket_in = expect.get("bucket_in")
    if bucket_in is not None and result.bucket not in bucket_in:
        fail("bucket_in", bucket_in, result.bucket)

    bucket_not = expect.get("bucket_not")
    if bucket_not is not None and result.bucket in bucket_not:
        fail("bucket_not", bucket_not, result.bucket)

    # ---- confidence checks ----
    min_conf = expect.get("min_confidence")
    if min_conf is not None and result.confidence < float(min_conf):
        fail("min_confidence", float(min_conf), result.confidence)

    max_conf = expect.get("max_confidence")
    if max_conf is not None and result.confidence > float(max_conf):
        fail("max_confidence", float(max_conf), result.confidence)

    max_conf_if_uncertain = expect.get("max_confidence_if_uncertain")
    if max_conf_if_uncertain is not None and result.bucket == "uncertain":
        if result.confidence > float(max_conf_if_uncertain):
            fail("max_confidence_if_uncertain", float(max_conf_if_uncertain), result.confidence)

    # ---- auto_move_ok checks ----
    auto_move_ok = expect.get("auto_move_ok")
    if auto_move_ok is not None and result.auto_move_ok is not bool(auto_move_ok):
        fail("auto_move_ok", bool(auto_move_ok), result.auto_move_ok)

    # ---- action checks (NEW) ----
    action = expect.get("action")
    if action is not None and result.action != action:
        fail("action", action, result.action)

    action_in = expect.get("action_in")
    if action_in is not None and result.action not in action_in:
        fail("action_in", action_in, result.action)

    action_not = expect.get("action_not")
    if action_not is not None and result.action in action_not:
        fail("action_not", action_not, result.action)


def pytest_generate_tests(metafunc):
    """
    Parametrize one test per JSON file.

    We keep behavior predictable:
      - If integration isn't enabled -> collect 1 skipped test.
      - If corpus dir missing/empty -> collect 1 skipped test.
      - Otherwise -> collect one test per JSON file.
    """
    if "case_path" not in metafunc.fixturenames:
        return

    if os.getenv("RUN_OLLAMA_INTEGRATION") != "1":
        metafunc.parametrize("case_path", [None], ids=["integration_disabled"])
        return

    corpus_dir = _find_corpus_dir()
    if not corpus_dir.exists():
        metafunc.parametrize("case_path", [None], ids=[f"corpus_missing:{corpus_dir}"])
        return

    files = _iter_case_paths(corpus_dir)
    if not files:
        metafunc.parametrize("case_path", [None], ids=[f"corpus_empty:{corpus_dir}"])
        return

    ids = [str(p.relative_to(corpus_dir)).replace("\\", "/") for p in files]
    metafunc.parametrize("case_path", files, ids=ids)


@pytest.fixture(scope="session")
def corpus_dir() -> Path:
    return _find_corpus_dir()


@pytest.fixture(scope="session")
def ollama_client():
    if os.getenv("RUN_OLLAMA_INTEGRATION") != "1":
        pytest.skip("Set RUN_OLLAMA_INTEGRATION=1 to run Ollama integration tests.")

    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

    if not _ollama_reachable(base_url):
        pytest.skip(f"Ollama not reachable at {base_url}. Is it running?")

    return mt.OllamaClient(base_url=base_url, model=model, timeout_s=180)


@pytest.mark.integration
def test_corpus_case(case_path: Optional[Path], corpus_dir: Path, ollama_client: mt.OllamaClient):
    # Handles the sentinel "None" params used when integration/corpus isn't ready
    if case_path is None:
        pytest.skip("Integration disabled or corpus missing/empty. See parametrization id for details.")

    case_name = str(case_path.relative_to(corpus_dir)).replace("\\", "/")
    email_obj, expect = _load_case(case_path)

    # Verbose output (use -s to see live)
    print(f"\n--- CASE: {case_name} ---")

    compact_email = dict(email_obj)
    body = compact_email.get("body_excerpt", "")
    if isinstance(body, str) and len(body) > 800:
        compact_email["body_excerpt"] = body[:800] + "\n...[truncated for display]..."

    print("EMAIL:")
    print(json.dumps(compact_email, indent=2, ensure_ascii=False))
    print("EXPECT:")
    print(json.dumps(expect, indent=2, ensure_ascii=False))

    result, raw = ollama_client.triage_email(email_obj)

    print("LLM RESULT:")
    print(result.model_dump_json(indent=2, exclude_none=True))

    stats = {
        "prompt_tokens": raw.get("prompt_eval_count"),
        "gen_tokens": raw.get("eval_count"),
        "prompt_ms": (raw.get("prompt_eval_duration", 0) or 0) / 1e6,
        "gen_ms": (raw.get("eval_duration", 0) or 0) / 1e6,
        "total_ms": (raw.get("total_duration", 0) or 0) / 1e6,
    }
    print("PERF:", json.dumps(stats, indent=2))

    _assert_expectations(case_name, result, raw, expect)