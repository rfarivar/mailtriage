(.venv) C:\Users\rezaf\dev\mailtriage>set OLLAMA_MODEL=llama3.2

(.venv) C:\Users\rezaf\dev\mailtriage>python -m pytest -m integration -q
.F................FFF...FFF.                                                                                                                              [100%]
=========================================================================== FAILURES ===========================================================================
_________________________________________________________ test_corpus_case[calendar_or_travel_02.json] _________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/calendar_or_travel_02.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x00000166FDB234D0>

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

>       _assert_expectations(case_name, result, raw, expect)

tests\test_ollama_integration_corpus.py:208:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_ollama_integration_corpus.py:107: in _assert_expectations
    fail("auto_move_ok", bool(auto_move_ok), result.auto_move_ok)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'auto_move_ok', expected = False, actual = True

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [calendar_or_travel_02.json] auto_move_ok failed
E         expected: False
E         actual:   True
E
E       DEBUG:
E       {
E         "case": "calendar_or_travel_02.json",
E         "expect": {
E           "bucket_in": [
E             "calendar_or_travel"
E           ],
E           "min_confidence": 0.75,
E           "auto_move_ok": false,
E           "action": "keep_in_inbox"
E         },
E         "actual": {
E           "bucket": "calendar_or_travel",
E           "confidence": 0.99,
E           "action": "move_to_folder",
E           "auto_move_ok": true,
E           "reason": "looks_like_invite and looks_like_travel",
E           "signals": []
E         },
E         "perf": {
E           "prompt_tokens": 920,
E           "gen_tokens": 34,
E           "total_ms": 797.0308
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: calendar_or_travel_02.json ---
EMAIL:
{
  "from": "Alaska Airlines <itinerary@alaskaair.com>",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "Itinerary change: Flight time updated",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<itinerary-ch-ic70dfm3@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "Your itinerary has changed.\n\n        Flight: AS 123\n        New departure: 6:15 PM (was 5:40 PM)\n        Date: Mar 6\n\n        Review your trip details in the app or website."
}
EXPECT:
{
  "bucket_in": [
    "calendar_or_travel"
  ],
  "min_confidence": 0.75,
  "auto_move_ok": false,
  "action": "keep_in_inbox"
}
LLM RESULT:
{
  "bucket": "calendar_or_travel",
  "confidence": 0.99,
  "action": "move_to_folder",
  "reason": "looks_like_invite and looks_like_travel",
  "signals": [],
  "auto_move_ok": true
}
PERF: {
  "prompt_tokens": 920,
  "gen_tokens": 34,
  "prompt_ms": 43.7772,
  "gen_ms": 155.9785,
  "total_ms": 797.0308
}
___________________________________________________________ test_corpus_case[spam_or_scams_01.json] ____________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/spam_or_scams_01.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x00000166FDB234D0>

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

>       _assert_expectations(case_name, result, raw, expect)

tests\test_ollama_integration_corpus.py:208:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_ollama_integration_corpus.py:84: in _assert_expectations
    fail("bucket_in", bucket_in, result.bucket)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'bucket_in', expected = ['spam_or_scams'], actual = 'security_alert'

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [spam_or_scams_01.json] bucket_in failed
E         expected: ['spam_or_scams']
E         actual:   security_alert
E
E       DEBUG:
E       {
E         "case": "spam_or_scams_01.json",
E         "expect": {
E           "bucket_in": [
E             "spam_or_scams"
E           ],
E           "min_confidence": 0.8,
E           "auto_move_ok": false,
E           "action": "quarantine"
E         },
E         "actual": {
E           "bucket": "security_alert",
E           "confidence": 0.99,
E           "action": "keep_in_inbox",
E           "auto_move_ok": false,
E           "reason": "contains 'suspicious activity' and 'verify your identity immediately', common phrases in security alerts",
E           "signals": []
E         },
E         "perf": {
E           "prompt_tokens": 913,
E           "gen_tokens": 45,
E           "total_ms": 1109.6203
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: spam_or_scams_01.json ---
EMAIL:
{
  "from": "PayPal Support <service@paypaI-security.com>",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "Your account is limited — action required",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<your-account-knxtmooc@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "We detected suspicious activity and limited your account.\n\n        Verify your identity immediately to restore access:\n        http://paypaI-security.com/verify\n\n        Failure to verify within 1 hour will permanently suspend your account."
}
EXPECT:
{
  "bucket_in": [
    "spam_or_scams"
  ],
  "min_confidence": 0.8,
  "auto_move_ok": false,
  "action": "quarantine"
}
LLM RESULT:
{
  "bucket": "security_alert",
  "confidence": 0.99,
  "action": "keep_in_inbox",
  "reason": "contains 'suspicious activity' and 'verify your identity immediately', common phrases in security alerts",
  "signals": [],
  "auto_move_ok": false
}
PERF: {
  "prompt_tokens": 913,
  "gen_tokens": 45,
  "prompt_ms": 67.4317,
  "gen_ms": 240.9939,
  "total_ms": 1109.6203
}
___________________________________________________________ test_corpus_case[spam_or_scams_02.json] ____________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/spam_or_scams_02.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x00000166FDB234D0>

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

>       _assert_expectations(case_name, result, raw, expect)

tests\test_ollama_integration_corpus.py:208:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_ollama_integration_corpus.py:84: in _assert_expectations
    fail("bucket_in", bucket_in, result.bucket)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'bucket_in', expected = ['spam_or_scams'], actual = 'needs_attention'

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [spam_or_scams_02.json] bucket_in failed
E         expected: ['spam_or_scams']
E         actual:   needs_attention
E
E       DEBUG:
E       {
E         "case": "spam_or_scams_02.json",
E         "expect": {
E           "bucket_in": [
E             "spam_or_scams"
E           ],
E           "min_confidence": 0.8,
E           "auto_move_ok": false,
E           "action": "quarantine"
E         },
E         "actual": {
E           "bucket": "needs_attention",
E           "confidence": 0.99,
E           "action": "keep_in_inbox",
E           "auto_move_ok": false,
E           "reason": "Human-to-human email with a deadline (revalidate account by today)",
E           "signals": []
E         },
E         "perf": {
E           "prompt_tokens": 913,
E           "gen_tokens": 39,
E           "total_ms": 919.9073
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: spam_or_scams_02.json ---
EMAIL:
{
  "from": "IT Helpdesk <helpdesk@illinois-security.com>",
  "to": "Reza <reza@illinois.edu>",
  "cc": "",
  "subject": "Mailbox storage exceeded — confirm now",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<mailbox-stor-cjth4j1v@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "Your mailbox has exceeded the storage limit.\n\n        Click to re-validate your account and avoid deactivation:\n        http://illinois-security.com/reauth\n\n        This must be completed today."
}
EXPECT:
{
  "bucket_in": [
    "spam_or_scams"
  ],
  "min_confidence": 0.8,
  "auto_move_ok": false,
  "action": "quarantine"
}
LLM RESULT:
{
  "bucket": "needs_attention",
  "confidence": 0.99,
  "action": "keep_in_inbox",
  "reason": "Human-to-human email with a deadline (revalidate account by today)",
  "signals": [],
  "auto_move_ok": false
}
PERF: {
  "prompt_tokens": 913,
  "gen_tokens": 39,
  "prompt_ms": 43.9212,
  "gen_ms": 180.5267,
  "total_ms": 919.9073
}
___________________________________________________________ test_corpus_case[spam_or_scams_03.json] ____________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/spam_or_scams_03.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x00000166FDB234D0>

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

>       _assert_expectations(case_name, result, raw, expect)

tests\test_ollama_integration_corpus.py:208:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_ollama_integration_corpus.py:84: in _assert_expectations
    fail("bucket_in", bucket_in, result.bucket)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'bucket_in', expected = ['spam_or_scams'], actual = 'transactional'

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [spam_or_scams_03.json] bucket_in failed
E         expected: ['spam_or_scams']
E         actual:   transactional
E
E       DEBUG:
E       {
E         "case": "spam_or_scams_03.json",
E         "expect": {
E           "bucket_in": [
E             "spam_or_scams"
E           ],
E           "min_confidence": 0.8,
E           "auto_move_ok": false,
E           "action": "quarantine"
E         },
E         "actual": {
E           "bucket": "transactional",
E           "confidence": 0.99,
E           "action": "move_to_folder",
E           "auto_move_ok": true,
E           "reason": "Receipts, invoices, shipping updates, payment confirmations, bills, confirmations with amounts/order numbers.",
E           "signals": []
E         },
E         "perf": {
E           "prompt_tokens": 916,
E           "gen_tokens": 46,
E           "total_ms": 1115.5739
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: spam_or_scams_03.json ---
EMAIL:
{
  "from": "Delivery Notice <noreply@shipments-track.net>",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "We couldn't deliver your package (fee required)",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<we-couldn't--uyrskbv1@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "We attempted delivery but require a small redelivery fee.\n\n        Pay the fee here to schedule redelivery:\n        http://shipments-track.net/pay\n\n        If unpaid, your package will be returned."
}
EXPECT:
{
  "bucket_in": [
    "spam_or_scams"
  ],
  "min_confidence": 0.8,
  "auto_move_ok": false,
  "action": "quarantine"
}
LLM RESULT:
{
  "bucket": "transactional",
  "confidence": 0.99,
  "action": "move_to_folder",
  "reason": "Receipts, invoices, shipping updates, payment confirmations, bills, confirmations with amounts/order numbers.",
  "signals": [],
  "auto_move_ok": true
}
PERF: {
  "prompt_tokens": 916,
  "gen_tokens": 46,
  "prompt_ms": 63.1639,
  "gen_ms": 240.1902,
  "total_ms": 1115.5739
}
_____________________________________________________________ test_corpus_case[uncertain_01.json] ______________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/uncertain_01.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x00000166FDB234D0>

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

>       _assert_expectations(case_name, result, raw, expect)

tests\test_ollama_integration_corpus.py:208:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_ollama_integration_corpus.py:84: in _assert_expectations
    fail("bucket_in", bucket_in, result.bucket)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'bucket_in', expected = ['uncertain'], actual = 'needs_attention'

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [uncertain_01.json] bucket_in failed
E         expected: ['uncertain']
E         actual:   needs_attention
E
E       DEBUG:
E       {
E         "case": "uncertain_01.json",
E         "expect": {
E           "bucket_in": [
E             "uncertain"
E           ],
E           "max_confidence": 0.69,
E           "auto_move_ok": false,
E           "action": "do_nothing"
E         },
E         "actual": {
E           "bucket": "needs_attention",
E           "confidence": 0.99,
E           "action": "keep_in_inbox",
E           "auto_move_ok": false,
E           "reason": "Human-to-human email asking for confirmation",
E           "signals": []
E         },
E         "perf": {
E           "prompt_tokens": 873,
E           "gen_tokens": 33,
E           "total_ms": 787.1296
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: uncertain_01.json ---
EMAIL:
{
  "from": "Pat <pat@unknown-domain.net>",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "Re: your request",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<re:-your-req-ajrh0oos@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "Following up on your request — can you confirm the details?"
}
EXPECT:
{
  "bucket_in": [
    "uncertain"
  ],
  "max_confidence": 0.69,
  "auto_move_ok": false,
  "action": "do_nothing"
}
LLM RESULT:
{
  "bucket": "needs_attention",
  "confidence": 0.99,
  "action": "keep_in_inbox",
  "reason": "Human-to-human email asking for confirmation",
  "signals": [],
  "auto_move_ok": false
}
PERF: {
  "prompt_tokens": 873,
  "gen_tokens": 33,
  "prompt_ms": 37.4057,
  "gen_ms": 161.651,
  "total_ms": 787.1296
}
_____________________________________________________________ test_corpus_case[uncertain_02.json] ______________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/uncertain_02.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x00000166FDB234D0>

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

>       _assert_expectations(case_name, result, raw, expect)

tests\test_ollama_integration_corpus.py:208:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_ollama_integration_corpus.py:84: in _assert_expectations
    fail("bucket_in", bucket_in, result.bucket)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'bucket_in', expected = ['uncertain'], actual = 'social_notification'

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [uncertain_02.json] bucket_in failed
E         expected: ['uncertain']
E         actual:   social_notification
E
E       DEBUG:
E       {
E         "case": "uncertain_02.json",
E         "expect": {
E           "bucket_in": [
E             "uncertain"
E           ],
E           "max_confidence": 0.69,
E           "auto_move_ok": false,
E           "action": "do_nothing"
E         },
E         "actual": {
E           "bucket": "social_notification",
E           "confidence": 0.99,
E           "action": "move_to_folder",
E           "auto_move_ok": true,
E           "reason": "list_id and list_unsubscribe are absent, but looks_like_social_notification is true",
E           "signals": []
E         },
E         "perf": {
E           "prompt_tokens": 861,
E           "gen_tokens": 42,
E           "total_ms": 977.4843
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: uncertain_02.json ---
EMAIL:
{
  "from": "noreply@service.example",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "Notification",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<notification-ndvruz3t@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "This is an automated notification regarding your recent activity."
}
EXPECT:
{
  "bucket_in": [
    "uncertain"
  ],
  "max_confidence": 0.69,
  "auto_move_ok": false,
  "action": "do_nothing"
}
LLM RESULT:
{
  "bucket": "social_notification",
  "confidence": 0.99,
  "action": "move_to_folder",
  "reason": "list_id and list_unsubscribe are absent, but looks_like_social_notification is true",
  "signals": [],
  "auto_move_ok": true
}
PERF: {
  "prompt_tokens": 861,
  "gen_tokens": 42,
  "prompt_ms": 39.4025,
  "gen_ms": 204.4338,
  "total_ms": 977.4843
}
_____________________________________________________________ test_corpus_case[uncertain_03.json] ______________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/uncertain_03.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x00000166FDB234D0>

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

>       _assert_expectations(case_name, result, raw, expect)

tests\test_ollama_integration_corpus.py:208:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_ollama_integration_corpus.py:84: in _assert_expectations
    fail("bucket_in", bucket_in, result.bucket)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'bucket_in', expected = ['uncertain'], actual = 'needs_attention'

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [uncertain_03.json] bucket_in failed
E         expected: ['uncertain']
E         actual:   needs_attention
E
E       DEBUG:
E       {
E         "case": "uncertain_03.json",
E         "expect": {
E           "bucket_in": [
E             "uncertain"
E           ],
E           "max_confidence": 0.69,
E           "auto_move_ok": false,
E           "action": "do_nothing"
E         },
E         "actual": {
E           "bucket": "needs_attention",
E           "confidence": 0.99,
E           "action": "keep_in_inbox",
E           "auto_move_ok": false,
E           "reason": "Human-to-human email with a deadline (update) and no list headers",
E           "signals": []
E         },
E         "perf": {
E           "prompt_tokens": 867,
E           "gen_tokens": 40,
E           "total_ms": 939.2944
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: uncertain_03.json ---
EMAIL:
{
  "from": "Support <support@vendor.example>",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "Ticket update",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<ticket-updat-76rtdmfl@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "Your ticket has been updated. Please see the portal for details."
}
EXPECT:
{
  "bucket_in": [
    "uncertain"
  ],
  "max_confidence": 0.69,
  "auto_move_ok": false,
  "action": "do_nothing"
}
LLM RESULT:
{
  "bucket": "needs_attention",
  "confidence": 0.99,
  "action": "keep_in_inbox",
  "reason": "Human-to-human email with a deadline (update) and no list headers",
  "signals": [],
  "auto_move_ok": false
}
PERF: {
  "prompt_tokens": 867,
  "gen_tokens": 40,
  "prompt_ms": 39.0268,
  "gen_ms": 186.5739,
  "total_ms": 939.2944
}
=================================================================== short test summary info ====================================================================
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[calendar_or_travel_02.json] - AssertionError: [calendar_or_travel_02.json] auto_move_ok failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[spam_or_scams_01.json] - AssertionError: [spam_or_scams_01.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[spam_or_scams_02.json] - AssertionError: [spam_or_scams_02.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[spam_or_scams_03.json] - AssertionError: [spam_or_scams_03.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[uncertain_01.json] - AssertionError: [uncertain_01.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[uncertain_02.json] - AssertionError: [uncertain_02.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[uncertain_03.json] - AssertionError: [uncertain_03.json] bucket_in failed
7 failed, 21 passed, 11 deselected in 28.50s

(.venv) C:\Users\rezaf\dev\mailtriage>set OLLAMA_MODEL=qwen3:8b

(.venv) C:\Users\rezaf\dev\mailtriage>python -m pytest -m integration -q
.F................FFF...FFF.                                                                                                                              [100%]
=========================================================================== FAILURES ===========================================================================
_________________________________________________________ test_corpus_case[calendar_or_travel_02.json] _________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/calendar_or_travel_02.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000002633F7B74D0>

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

>       _assert_expectations(case_name, result, raw, expect)

tests\test_ollama_integration_corpus.py:208:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_ollama_integration_corpus.py:107: in _assert_expectations
    fail("auto_move_ok", bool(auto_move_ok), result.auto_move_ok)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'auto_move_ok', expected = False, actual = True

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [calendar_or_travel_02.json] auto_move_ok failed
E         expected: False
E         actual:   True
E
E       DEBUG:
E       {
E         "case": "calendar_or_travel_02.json",
E         "expect": {
E           "bucket_in": [
E             "calendar_or_travel"
E           ],
E           "min_confidence": 0.75,
E           "auto_move_ok": false,
E           "action": "keep_in_inbox"
E         },
E         "actual": {
E           "bucket": "calendar_or_travel",
E           "confidence": 0.95,
E           "action": "move_to_folder",
E           "auto_move_ok": true,
E           "reason": "Itinerary change with flight details and action request.",
E           "signals": [
E             "looks_like_travel",
E             "has_direct_request"
E           ]
E         },
E         "perf": {
E           "prompt_tokens": 932,
E           "gen_tokens": 56,
E           "total_ms": 842.3644
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: calendar_or_travel_02.json ---
EMAIL:
{
  "from": "Alaska Airlines <itinerary@alaskaair.com>",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "Itinerary change: Flight time updated",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<itinerary-ch-ic70dfm3@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "Your itinerary has changed.\n\n        Flight: AS 123\n        New departure: 6:15 PM (was 5:40 PM)\n        Date: Mar 6\n\n        Review your trip details in the app or website."
}
EXPECT:
{
  "bucket_in": [
    "calendar_or_travel"
  ],
  "min_confidence": 0.75,
  "auto_move_ok": false,
  "action": "keep_in_inbox"
}
LLM RESULT:
{
  "bucket": "calendar_or_travel",
  "confidence": 0.95,
  "action": "move_to_folder",
  "reason": "Itinerary change with flight details and action request.",
  "signals": [
    "looks_like_travel",
    "has_direct_request"
  ],
  "auto_move_ok": true
}
PERF: {
  "prompt_tokens": 932,
  "gen_tokens": 56,
  "prompt_ms": 94.5462,
  "gen_ms": 543.7512,
  "total_ms": 842.3644
}
___________________________________________________________ test_corpus_case[spam_or_scams_01.json] ____________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/spam_or_scams_01.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000002633F7B74D0>

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

>       _assert_expectations(case_name, result, raw, expect)

tests\test_ollama_integration_corpus.py:208:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_ollama_integration_corpus.py:84: in _assert_expectations
    fail("bucket_in", bucket_in, result.bucket)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'bucket_in', expected = ['spam_or_scams'], actual = 'security_alert'

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [spam_or_scams_01.json] bucket_in failed
E         expected: ['spam_or_scams']
E         actual:   security_alert
E
E       DEBUG:
E       {
E         "case": "spam_or_scams_01.json",
E         "expect": {
E           "bucket_in": [
E             "spam_or_scams"
E           ],
E           "min_confidence": 0.8,
E           "auto_move_ok": false,
E           "action": "quarantine"
E         },
E         "actual": {
E           "bucket": "security_alert",
E           "confidence": 0.95,
E           "action": "keep_in_inbox",
E           "auto_move_ok": false,
E           "reason": "Account limited with verification link and deadline",
E           "signals": [
E             "account_threat",
E             "suspicious_link",
E             "direct_request"
E           ]
E         },
E         "perf": {
E           "prompt_tokens": 920,
E           "gen_tokens": 59,
E           "total_ms": 844.4812
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: spam_or_scams_01.json ---
EMAIL:
{
  "from": "PayPal Support <service@paypaI-security.com>",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "Your account is limited — action required",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<your-account-knxtmooc@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "We detected suspicious activity and limited your account.\n\n        Verify your identity immediately to restore access:\n        http://paypaI-security.com/verify\n\n        Failure to verify within 1 hour will permanently suspend your account."
}
EXPECT:
{
  "bucket_in": [
    "spam_or_scams"
  ],
  "min_confidence": 0.8,
  "auto_move_ok": false,
  "action": "quarantine"
}
LLM RESULT:
{
  "bucket": "security_alert",
  "confidence": 0.95,
  "action": "keep_in_inbox",
  "reason": "Account limited with verification link and deadline",
  "signals": [
    "account_threat",
    "suspicious_link",
    "direct_request"
  ],
  "auto_move_ok": false
}
PERF: {
  "prompt_tokens": 920,
  "gen_tokens": 59,
  "prompt_ms": 93.9822,
  "gen_ms": 568.3989,
  "total_ms": 844.4812
}
___________________________________________________________ test_corpus_case[spam_or_scams_02.json] ____________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/spam_or_scams_02.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000002633F7B74D0>

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

>       _assert_expectations(case_name, result, raw, expect)

tests\test_ollama_integration_corpus.py:208:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_ollama_integration_corpus.py:84: in _assert_expectations
    fail("bucket_in", bucket_in, result.bucket)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'bucket_in', expected = ['spam_or_scams'], actual = 'needs_attention'

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [spam_or_scams_02.json] bucket_in failed
E         expected: ['spam_or_scams']
E         actual:   needs_attention
E
E       DEBUG:
E       {
E         "case": "spam_or_scams_02.json",
E         "expect": {
E           "bucket_in": [
E             "spam_or_scams"
E           ],
E           "min_confidence": 0.8,
E           "auto_move_ok": false,
E           "action": "quarantine"
E         },
E         "actual": {
E           "bucket": "needs_attention",
E           "confidence": 0.95,
E           "action": "keep_in_inbox",
E           "auto_move_ok": false,
E           "reason": "Urgent request to re-validate account to avoid deactivation.",
E           "signals": [
E             "has_direct_request",
E             "has_link",
E             "has_deadline"
E           ]
E         },
E         "perf": {
E           "prompt_tokens": 920,
E           "gen_tokens": 63,
E           "total_ms": 879.7094
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: spam_or_scams_02.json ---
EMAIL:
{
  "from": "IT Helpdesk <helpdesk@illinois-security.com>",
  "to": "Reza <reza@illinois.edu>",
  "cc": "",
  "subject": "Mailbox storage exceeded — confirm now",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<mailbox-stor-cjth4j1v@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "Your mailbox has exceeded the storage limit.\n\n        Click to re-validate your account and avoid deactivation:\n        http://illinois-security.com/reauth\n\n        This must be completed today."
}
EXPECT:
{
  "bucket_in": [
    "spam_or_scams"
  ],
  "min_confidence": 0.8,
  "auto_move_ok": false,
  "action": "quarantine"
}
LLM RESULT:
{
  "bucket": "needs_attention",
  "confidence": 0.95,
  "action": "keep_in_inbox",
  "reason": "Urgent request to re-validate account to avoid deactivation.",
  "signals": [
    "has_direct_request",
    "has_link",
    "has_deadline"
  ],
  "auto_move_ok": false
}
PERF: {
  "prompt_tokens": 920,
  "gen_tokens": 63,
  "prompt_ms": 93.2274,
  "gen_ms": 606.1463,
  "total_ms": 879.7094
}
___________________________________________________________ test_corpus_case[spam_or_scams_03.json] ____________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/spam_or_scams_03.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000002633F7B74D0>

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

>       _assert_expectations(case_name, result, raw, expect)

tests\test_ollama_integration_corpus.py:208:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_ollama_integration_corpus.py:84: in _assert_expectations
    fail("bucket_in", bucket_in, result.bucket)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'bucket_in', expected = ['spam_or_scams'], actual = 'transactional'

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [spam_or_scams_03.json] bucket_in failed
E         expected: ['spam_or_scams']
E         actual:   transactional
E
E       DEBUG:
E       {
E         "case": "spam_or_scams_03.json",
E         "expect": {
E           "bucket_in": [
E             "spam_or_scams"
E           ],
E           "min_confidence": 0.8,
E           "auto_move_ok": false,
E           "action": "quarantine"
E         },
E         "actual": {
E           "bucket": "transactional",
E           "confidence": 0.95,
E           "action": "move_to_folder",
E           "auto_move_ok": true,
E           "reason": "Fee required for package redelivery with payment link.",
E           "signals": [
E             "has_link",
E             "looks_like_transaction"
E           ]
E         },
E         "perf": {
E           "prompt_tokens": 923,
E           "gen_tokens": 54,
E           "total_ms": 805.9033
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: spam_or_scams_03.json ---
EMAIL:
{
  "from": "Delivery Notice <noreply@shipments-track.net>",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "We couldn't deliver your package (fee required)",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<we-couldn't--uyrskbv1@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "We attempted delivery but require a small redelivery fee.\n\n        Pay the fee here to schedule redelivery:\n        http://shipments-track.net/pay\n\n        If unpaid, your package will be returned."
}
EXPECT:
{
  "bucket_in": [
    "spam_or_scams"
  ],
  "min_confidence": 0.8,
  "auto_move_ok": false,
  "action": "quarantine"
}
LLM RESULT:
{
  "bucket": "transactional",
  "confidence": 0.95,
  "action": "move_to_folder",
  "reason": "Fee required for package redelivery with payment link.",
  "signals": [
    "has_link",
    "looks_like_transaction"
  ],
  "auto_move_ok": true
}
PERF: {
  "prompt_tokens": 923,
  "gen_tokens": 54,
  "prompt_ms": 99.7691,
  "gen_ms": 519.1682,
  "total_ms": 805.9033
}
_____________________________________________________________ test_corpus_case[uncertain_01.json] ______________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/uncertain_01.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000002633F7B74D0>

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

>       _assert_expectations(case_name, result, raw, expect)

tests\test_ollama_integration_corpus.py:208:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_ollama_integration_corpus.py:84: in _assert_expectations
    fail("bucket_in", bucket_in, result.bucket)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'bucket_in', expected = ['uncertain'], actual = 'needs_attention'

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [uncertain_01.json] bucket_in failed
E         expected: ['uncertain']
E         actual:   needs_attention
E
E       DEBUG:
E       {
E         "case": "uncertain_01.json",
E         "expect": {
E           "bucket_in": [
E             "uncertain"
E           ],
E           "max_confidence": 0.69,
E           "auto_move_ok": false,
E           "action": "do_nothing"
E         },
E         "actual": {
E           "bucket": "needs_attention",
E           "confidence": 0.95,
E           "action": "keep_in_inbox",
E           "auto_move_ok": false,
E           "reason": "Direct request for confirmation",
E           "signals": [
E             "has_direct_request"
E           ]
E         },
E         "perf": {
E           "prompt_tokens": 880,
E           "gen_tokens": 44,
E           "total_ms": 686.9884
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: uncertain_01.json ---
EMAIL:
{
  "from": "Pat <pat@unknown-domain.net>",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "Re: your request",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<re:-your-req-ajrh0oos@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "Following up on your request — can you confirm the details?"
}
EXPECT:
{
  "bucket_in": [
    "uncertain"
  ],
  "max_confidence": 0.69,
  "auto_move_ok": false,
  "action": "do_nothing"
}
LLM RESULT:
{
  "bucket": "needs_attention",
  "confidence": 0.95,
  "action": "keep_in_inbox",
  "reason": "Direct request for confirmation",
  "signals": [
    "has_direct_request"
  ],
  "auto_move_ok": false
}
PERF: {
  "prompt_tokens": 880,
  "gen_tokens": 44,
  "prompt_ms": 81.6128,
  "gen_ms": 427.4354,
  "total_ms": 686.9884
}
_____________________________________________________________ test_corpus_case[uncertain_02.json] ______________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/uncertain_02.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000002633F7B74D0>

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

>       _assert_expectations(case_name, result, raw, expect)

tests\test_ollama_integration_corpus.py:208:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_ollama_integration_corpus.py:84: in _assert_expectations
    fail("bucket_in", bucket_in, result.bucket)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'bucket_in', expected = ['uncertain'], actual = 'social_notification'

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [uncertain_02.json] bucket_in failed
E         expected: ['uncertain']
E         actual:   social_notification
E
E       DEBUG:
E       {
E         "case": "uncertain_02.json",
E         "expect": {
E           "bucket_in": [
E             "uncertain"
E           ],
E           "max_confidence": 0.69,
E           "auto_move_ok": false,
E           "action": "do_nothing"
E         },
E         "actual": {
E           "bucket": "social_notification",
E           "confidence": 0.95,
E           "action": "move_to_folder",
E           "auto_move_ok": true,
E           "reason": "Looks like a social platform notification",
E           "signals": [
E             "looks_like_social_notification"
E           ]
E         },
E         "perf": {
E           "prompt_tokens": 868,
E           "gen_tokens": 47,
E           "total_ms": 721.2933
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: uncertain_02.json ---
EMAIL:
{
  "from": "noreply@service.example",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "Notification",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<notification-ndvruz3t@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "This is an automated notification regarding your recent activity."
}
EXPECT:
{
  "bucket_in": [
    "uncertain"
  ],
  "max_confidence": 0.69,
  "auto_move_ok": false,
  "action": "do_nothing"
}
LLM RESULT:
{
  "bucket": "social_notification",
  "confidence": 0.95,
  "action": "move_to_folder",
  "reason": "Looks like a social platform notification",
  "signals": [
    "looks_like_social_notification"
  ],
  "auto_move_ok": true
}
PERF: {
  "prompt_tokens": 868,
  "gen_tokens": 47,
  "prompt_ms": 73.6854,
  "gen_ms": 452.0288,
  "total_ms": 721.2933
}
_____________________________________________________________ test_corpus_case[uncertain_03.json] ______________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/uncertain_03.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000002633F7B74D0>

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

>       _assert_expectations(case_name, result, raw, expect)

tests\test_ollama_integration_corpus.py:208:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_ollama_integration_corpus.py:84: in _assert_expectations
    fail("bucket_in", bucket_in, result.bucket)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'bucket_in', expected = ['uncertain'], actual = 'needs_attention'

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [uncertain_03.json] bucket_in failed
E         expected: ['uncertain']
E         actual:   needs_attention
E
E       DEBUG:
E       {
E         "case": "uncertain_03.json",
E         "expect": {
E           "bucket_in": [
E             "uncertain"
E           ],
E           "max_confidence": 0.69,
E           "auto_move_ok": false,
E           "action": "do_nothing"
E         },
E         "actual": {
E           "bucket": "needs_attention",
E           "confidence": 0.95,
E           "action": "keep_in_inbox",
E           "auto_move_ok": false,
E           "reason": "Requests user to check portal for ticket details",
E           "signals": [
E             "has_direct_request"
E           ]
E         },
E         "perf": {
E           "prompt_tokens": 875,
E           "gen_tokens": 48,
E           "total_ms": 733.9852
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: uncertain_03.json ---
EMAIL:
{
  "from": "Support <support@vendor.example>",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "Ticket update",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<ticket-updat-76rtdmfl@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "Your ticket has been updated. Please see the portal for details."
}
EXPECT:
{
  "bucket_in": [
    "uncertain"
  ],
  "max_confidence": 0.69,
  "auto_move_ok": false,
  "action": "do_nothing"
}
LLM RESULT:
{
  "bucket": "needs_attention",
  "confidence": 0.95,
  "action": "keep_in_inbox",
  "reason": "Requests user to check portal for ticket details",
  "signals": [
    "has_direct_request"
  ],
  "auto_move_ok": false
}
PERF: {
  "prompt_tokens": 875,
  "gen_tokens": 48,
  "prompt_ms": 85.6191,
  "gen_ms": 464.3967,
  "total_ms": 733.9852
}
=================================================================== short test summary info ====================================================================
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[calendar_or_travel_02.json] - AssertionError: [calendar_or_travel_02.json] auto_move_ok failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[spam_or_scams_01.json] - AssertionError: [spam_or_scams_01.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[spam_or_scams_02.json] - AssertionError: [spam_or_scams_02.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[spam_or_scams_03.json] - AssertionError: [spam_or_scams_03.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[uncertain_01.json] - AssertionError: [uncertain_01.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[uncertain_02.json] - AssertionError: [uncertain_02.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[uncertain_03.json] - AssertionError: [uncertain_03.json] bucket_in failed
7 failed, 21 passed, 11 deselected in 26.22s

(.venv) C:\Users\rezaf\dev\mailtriage>set OLLAMA_MODEL=llama3.1:8b

(.venv) C:\Users\rezaf\dev\mailtriage>python -m pytest -m integration -q
.FF.......F.......FF....FFF.                                                                                                                              [100%]
=========================================================================== FAILURES ===========================================================================
_________________________________________________________ test_corpus_case[calendar_or_travel_02.json] _________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/calendar_or_travel_02.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x00000131EFEB74D0>

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

>       _assert_expectations(case_name, result, raw, expect)

tests\test_ollama_integration_corpus.py:208:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_ollama_integration_corpus.py:107: in _assert_expectations
    fail("auto_move_ok", bool(auto_move_ok), result.auto_move_ok)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'auto_move_ok', expected = False, actual = True

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [calendar_or_travel_02.json] auto_move_ok failed
E         expected: False
E         actual:   True
E
E       DEBUG:
E       {
E         "case": "calendar_or_travel_02.json",
E         "expect": {
E           "bucket_in": [
E             "calendar_or_travel"
E           ],
E           "min_confidence": 0.75,
E           "auto_move_ok": false,
E           "action": "keep_in_inbox"
E         },
E         "actual": {
E           "bucket": "calendar_or_travel",
E           "confidence": 0.95,
E           "action": "move_to_folder",
E           "auto_move_ok": true,
E           "reason": "Itinerary change notification with flight time update and review details in app/website.",
E           "signals": [
E             "looks_like_travel",
E             "has_direct_request"
E           ]
E         },
E         "perf": {
E           "prompt_tokens": 910,
E           "gen_tokens": 61,
E           "total_ms": 1654.7118
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: calendar_or_travel_02.json ---
EMAIL:
{
  "from": "Alaska Airlines <itinerary@alaskaair.com>",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "Itinerary change: Flight time updated",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<itinerary-ch-ic70dfm3@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "Your itinerary has changed.\n\n        Flight: AS 123\n        New departure: 6:15 PM (was 5:40 PM)\n        Date: Mar 6\n\n        Review your trip details in the app or website."
}
EXPECT:
{
  "bucket_in": [
    "calendar_or_travel"
  ],
  "min_confidence": 0.75,
  "auto_move_ok": false,
  "action": "keep_in_inbox"
}
LLM RESULT:
{
  "bucket": "calendar_or_travel",
  "confidence": 0.95,
  "action": "move_to_folder",
  "reason": "Itinerary change notification with flight time update and review details in app/website.",
  "signals": [
    "looks_like_travel",
    "has_direct_request"
  ],
  "auto_move_ok": true
}
PERF: {
  "prompt_tokens": 910,
  "gen_tokens": 61,
  "prompt_ms": 87.6555,
  "gen_ms": 512.3081,
  "total_ms": 1654.7118
}
_________________________________________________________ test_corpus_case[calendar_or_travel_03.json] _________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/calendar_or_travel_03.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x00000131EFEB74D0>

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

>       _assert_expectations(case_name, result, raw, expect)

tests\test_ollama_integration_corpus.py:208:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_ollama_integration_corpus.py:84: in _assert_expectations
    fail("bucket_in", bucket_in, result.bucket)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'bucket_in', expected = ['calendar_or_travel'], actual = 'transactional'

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [calendar_or_travel_03.json] bucket_in failed
E         expected: ['calendar_or_travel']
E         actual:   transactional
E
E       DEBUG:
E       {
E         "case": "calendar_or_travel_03.json",
E         "expect": {
E           "bucket_in": [
E             "calendar_or_travel"
E           ],
E           "min_confidence": 0.75,
E           "auto_move_ok": true,
E           "action": "move_to_folder"
E         },
E         "actual": {
E           "bucket": "transactional",
E           "confidence": 0.95,
E           "action": "move_to_folder",
E           "auto_move_ok": true,
E           "reason": "Booking confirmation with hotel details and a link to modify the reservation.",
E           "signals": [
E             "looks_like_transaction",
E             "looks_like_travel"
E           ]
E         },
E         "perf": {
E           "prompt_tokens": 909,
E           "gen_tokens": 57,
E           "total_ms": 1577.7962
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: calendar_or_travel_03.json ---
EMAIL:
{
  "from": "Hotel Reservations <reservations@hotel-example.com>",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "Booking confirmation: Seattle stay",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<booking-conf-2v2eg6iq@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "Booking confirmed.\n\n        Hotel: Downtown Seattle Hotel\n        Check-in: Mar 6\n        Check-out: Mar 8\n        Confirmation: SEAT-88421\n\n        If you need to modify your reservation, use the link in your confirmation page."
}
EXPECT:
{
  "bucket_in": [
    "calendar_or_travel"
  ],
  "min_confidence": 0.75,
  "auto_move_ok": true,
  "action": "move_to_folder"
}
LLM RESULT:
{
  "bucket": "transactional",
  "confidence": 0.95,
  "action": "move_to_folder",
  "reason": "Booking confirmation with hotel details and a link to modify the reservation.",
  "signals": [
    "looks_like_transaction",
    "looks_like_travel"
  ],
  "auto_move_ok": true
}
PERF: {
  "prompt_tokens": 909,
  "gen_tokens": 57,
  "prompt_ms": 90.4804,
  "gen_ms": 487.3298,
  "total_ms": 1577.7962
}
_______________________________________________________________ test_corpus_case[phish_01.json] ________________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/phish_01.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x00000131EFEB74D0>

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

>       _assert_expectations(case_name, result, raw, expect)

tests\test_ollama_integration_corpus.py:208:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_ollama_integration_corpus.py:84: in _assert_expectations
    fail("bucket_in", bucket_in, result.bucket)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'bucket_in', expected = ['spam_or_scams', 'uncertain'], actual = 'security_alert'

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [phish_01.json] bucket_in failed
E         expected: ['spam_or_scams', 'uncertain']
E         actual:   security_alert
E
E       DEBUG:
E       {
E         "case": "phish_01.json",
E         "expect": {
E           "bucket_not": [
E             "needs_attention"
E           ],
E           "bucket_in": [
E             "spam_or_scams",
E             "uncertain"
E           ],
E           "action_in": [
E             "quarantine",
E             "do_nothing"
E           ],
E           "action_not": [
E             "do_nothing"
E           ],
E           "max_confidence_if_uncertain": 0.7
E         },
E         "actual": {
E           "bucket": "security_alert",
E           "confidence": 0.95,
E           "action": "keep_in_inbox",
E           "auto_move_ok": false,
E           "reason": "Suspicious link and account threat in subject line.",
E           "signals": [
E             "account_threat",
E             "suspicious_link"
E           ]
E         },
E         "perf": {
E           "prompt_tokens": 890,
E           "gen_tokens": 50,
E           "total_ms": 1372.0487
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: phish_01.json ---
EMAIL:
{
  "from": "Payroll Security <security@payr0ll-support.com>",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "URGENT: Your payroll account will be suspended in 2 hours",
  "date": "Fri, 20 Feb 2026 10:05:00 -0800",
  "message_id": "<spam-1234@payr0ll-support.com>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "We detected unusual activity... Click here: http://payr0ll-support.com/verify ..."
}
EXPECT:
{
  "bucket_not": [
    "needs_attention"
  ],
  "bucket_in": [
    "spam_or_scams",
    "uncertain"
  ],
  "action_in": [
    "quarantine",
    "do_nothing"
  ],
  "action_not": [
    "do_nothing"
  ],
  "max_confidence_if_uncertain": 0.7
}
LLM RESULT:
{
  "bucket": "security_alert",
  "confidence": 0.95,
  "action": "keep_in_inbox",
  "reason": "Suspicious link and account threat in subject line.",
  "signals": [
    "account_threat",
    "suspicious_link"
  ],
  "auto_move_ok": false
}
PERF: {
  "prompt_tokens": 890,
  "gen_tokens": 50,
  "prompt_ms": 81.4898,
  "gen_ms": 416.0219,
  "total_ms": 1372.0487
}
___________________________________________________________ test_corpus_case[spam_or_scams_01.json] ____________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/spam_or_scams_01.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x00000131EFEB74D0>

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

>       _assert_expectations(case_name, result, raw, expect)

tests\test_ollama_integration_corpus.py:208:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_ollama_integration_corpus.py:84: in _assert_expectations
    fail("bucket_in", bucket_in, result.bucket)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'bucket_in', expected = ['spam_or_scams'], actual = 'security_alert'

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [spam_or_scams_01.json] bucket_in failed
E         expected: ['spam_or_scams']
E         actual:   security_alert
E
E       DEBUG:
E       {
E         "case": "spam_or_scams_01.json",
E         "expect": {
E           "bucket_in": [
E             "spam_or_scams"
E           ],
E           "min_confidence": 0.8,
E           "auto_move_ok": false,
E           "action": "quarantine"
E         },
E         "actual": {
E           "bucket": "security_alert",
E           "confidence": 0.95,
E           "action": "keep_in_inbox",
E           "auto_move_ok": false,
E           "reason": "Suspicious activity detected and account limited; verify identity via link to restore access.",
E           "signals": [
E             "direct_request",
E             "account_threat"
E           ]
E         },
E         "perf": {
E           "prompt_tokens": 903,
E           "gen_tokens": 54,
E           "total_ms": 1675.4939
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: spam_or_scams_01.json ---
EMAIL:
{
  "from": "PayPal Support <service@paypaI-security.com>",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "Your account is limited — action required",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<your-account-knxtmooc@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "We detected suspicious activity and limited your account.\n\n        Verify your identity immediately to restore access:\n        http://paypaI-security.com/verify\n\n        Failure to verify within 1 hour will permanently suspend your account."
}
EXPECT:
{
  "bucket_in": [
    "spam_or_scams"
  ],
  "min_confidence": 0.8,
  "auto_move_ok": false,
  "action": "quarantine"
}
LLM RESULT:
{
  "bucket": "security_alert",
  "confidence": 0.95,
  "action": "keep_in_inbox",
  "reason": "Suspicious activity detected and account limited; verify identity via link to restore access.",
  "signals": [
    "direct_request",
    "account_threat"
  ],
  "auto_move_ok": false
}
PERF: {
  "prompt_tokens": 903,
  "gen_tokens": 54,
  "prompt_ms": 88.5018,
  "gen_ms": 486.4323,
  "total_ms": 1675.4939
}
___________________________________________________________ test_corpus_case[spam_or_scams_02.json] ____________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/spam_or_scams_02.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x00000131EFEB74D0>

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

>       _assert_expectations(case_name, result, raw, expect)

tests\test_ollama_integration_corpus.py:208:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_ollama_integration_corpus.py:84: in _assert_expectations
    fail("bucket_in", bucket_in, result.bucket)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'bucket_in', expected = ['spam_or_scams'], actual = 'security_alert'

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [spam_or_scams_02.json] bucket_in failed
E         expected: ['spam_or_scams']
E         actual:   security_alert
E
E       DEBUG:
E       {
E         "case": "spam_or_scams_02.json",
E         "expect": {
E           "bucket_in": [
E             "spam_or_scams"
E           ],
E           "min_confidence": 0.8,
E           "auto_move_ok": false,
E           "action": "quarantine"
E         },
E         "actual": {
E           "bucket": "security_alert",
E           "confidence": 0.95,
E           "action": "keep_in_inbox",
E           "auto_move_ok": false,
E           "reason": "contains phrases like 'If this wasn't you...' and has a direct request to re-validate account",
E           "signals": [
E             "direct_request",
E             "has_link"
E           ]
E         },
E         "perf": {
E           "prompt_tokens": 903,
E           "gen_tokens": 57,
E           "total_ms": 1667.1651
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: spam_or_scams_02.json ---
EMAIL:
{
  "from": "IT Helpdesk <helpdesk@illinois-security.com>",
  "to": "Reza <reza@illinois.edu>",
  "cc": "",
  "subject": "Mailbox storage exceeded — confirm now",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<mailbox-stor-cjth4j1v@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "Your mailbox has exceeded the storage limit.\n\n        Click to re-validate your account and avoid deactivation:\n        http://illinois-security.com/reauth\n\n        This must be completed today."
}
EXPECT:
{
  "bucket_in": [
    "spam_or_scams"
  ],
  "min_confidence": 0.8,
  "auto_move_ok": false,
  "action": "quarantine"
}
LLM RESULT:
{
  "bucket": "security_alert",
  "confidence": 0.95,
  "action": "keep_in_inbox",
  "reason": "contains phrases like 'If this wasn't you...' and has a direct request to re-validate account",
  "signals": [
    "direct_request",
    "has_link"
  ],
  "auto_move_ok": false
}
PERF: {
  "prompt_tokens": 903,
  "gen_tokens": 57,
  "prompt_ms": 92.1782,
  "gen_ms": 519.8167,
  "total_ms": 1667.1651
}
_____________________________________________________________ test_corpus_case[uncertain_01.json] ______________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/uncertain_01.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x00000131EFEB74D0>

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

>       _assert_expectations(case_name, result, raw, expect)

tests\test_ollama_integration_corpus.py:208:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_ollama_integration_corpus.py:84: in _assert_expectations
    fail("bucket_in", bucket_in, result.bucket)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'bucket_in', expected = ['uncertain'], actual = 'needs_attention'

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [uncertain_01.json] bucket_in failed
E         expected: ['uncertain']
E         actual:   needs_attention
E
E       DEBUG:
E       {
E         "case": "uncertain_01.json",
E         "expect": {
E           "bucket_in": [
E             "uncertain"
E           ],
E           "max_confidence": 0.69,
E           "auto_move_ok": false,
E           "action": "do_nothing"
E         },
E         "actual": {
E           "bucket": "needs_attention",
E           "confidence": 0.95,
E           "action": "keep_in_inbox",
E           "auto_move_ok": false,
E           "reason": "Direct request to confirm details with no deadline or transactional content.",
E           "signals": [
E             "direct_request"
E           ]
E         },
E         "perf": {
E           "prompt_tokens": 863,
E           "gen_tokens": 46,
E           "total_ms": 1297.2124
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: uncertain_01.json ---
EMAIL:
{
  "from": "Pat <pat@unknown-domain.net>",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "Re: your request",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<re:-your-req-ajrh0oos@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "Following up on your request — can you confirm the details?"
}
EXPECT:
{
  "bucket_in": [
    "uncertain"
  ],
  "max_confidence": 0.69,
  "auto_move_ok": false,
  "action": "do_nothing"
}
LLM RESULT:
{
  "bucket": "needs_attention",
  "confidence": 0.95,
  "action": "keep_in_inbox",
  "reason": "Direct request to confirm details with no deadline or transactional content.",
  "signals": [
    "direct_request"
  ],
  "auto_move_ok": false
}
PERF: {
  "prompt_tokens": 863,
  "gen_tokens": 46,
  "prompt_ms": 71.8534,
  "gen_ms": 400.3085,
  "total_ms": 1297.2124
}
_____________________________________________________________ test_corpus_case[uncertain_02.json] ______________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/uncertain_02.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x00000131EFEB74D0>

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

>       _assert_expectations(case_name, result, raw, expect)

tests\test_ollama_integration_corpus.py:208:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_ollama_integration_corpus.py:84: in _assert_expectations
    fail("bucket_in", bucket_in, result.bucket)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'bucket_in', expected = ['uncertain'], actual = 'social_notification'

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [uncertain_02.json] bucket_in failed
E         expected: ['uncertain']
E         actual:   social_notification
E
E       DEBUG:
E       {
E         "case": "uncertain_02.json",
E         "expect": {
E           "bucket_in": [
E             "uncertain"
E           ],
E           "max_confidence": 0.69,
E           "auto_move_ok": false,
E           "action": "do_nothing"
E         },
E         "actual": {
E           "bucket": "social_notification",
E           "confidence": 0.95,
E           "action": "move_to_folder",
E           "auto_move_ok": true,
E           "reason": "Automated notification with social notification features.",
E           "signals": [
E             "looks_like_social_notification"
E           ]
E         },
E         "perf": {
E           "prompt_tokens": 851,
E           "gen_tokens": 43,
E           "total_ms": 1247.4749
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: uncertain_02.json ---
EMAIL:
{
  "from": "noreply@service.example",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "Notification",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<notification-ndvruz3t@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "This is an automated notification regarding your recent activity."
}
EXPECT:
{
  "bucket_in": [
    "uncertain"
  ],
  "max_confidence": 0.69,
  "auto_move_ok": false,
  "action": "do_nothing"
}
LLM RESULT:
{
  "bucket": "social_notification",
  "confidence": 0.95,
  "action": "move_to_folder",
  "reason": "Automated notification with social notification features.",
  "signals": [
    "looks_like_social_notification"
  ],
  "auto_move_ok": true
}
PERF: {
  "prompt_tokens": 851,
  "gen_tokens": 43,
  "prompt_ms": 70.4233,
  "gen_ms": 379.5665,
  "total_ms": 1247.4749
}
_____________________________________________________________ test_corpus_case[uncertain_03.json] ______________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/uncertain_03.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x00000131EFEB74D0>

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

>       _assert_expectations(case_name, result, raw, expect)

tests\test_ollama_integration_corpus.py:208:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_ollama_integration_corpus.py:84: in _assert_expectations
    fail("bucket_in", bucket_in, result.bucket)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'bucket_in', expected = ['uncertain'], actual = 'needs_attention'

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [uncertain_03.json] bucket_in failed
E         expected: ['uncertain']
E         actual:   needs_attention
E
E       DEBUG:
E       {
E         "case": "uncertain_03.json",
E         "expect": {
E           "bucket_in": [
E             "uncertain"
E           ],
E           "max_confidence": 0.69,
E           "auto_move_ok": false,
E           "action": "do_nothing"
E         },
E         "actual": {
E           "bucket": "needs_attention",
E           "confidence": 0.95,
E           "action": "keep_in_inbox",
E           "auto_move_ok": false,
E           "reason": "Direct request to see portal for details.",
E           "signals": [
E             "direct_request"
E           ]
E         },
E         "perf": {
E           "prompt_tokens": 857,
E           "gen_tokens": 41,
E           "total_ms": 1164.3707
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: uncertain_03.json ---
EMAIL:
{
  "from": "Support <support@vendor.example>",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "Ticket update",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<ticket-updat-76rtdmfl@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "Your ticket has been updated. Please see the portal for details."
}
EXPECT:
{
  "bucket_in": [
    "uncertain"
  ],
  "max_confidence": 0.69,
  "auto_move_ok": false,
  "action": "do_nothing"
}
LLM RESULT:
{
  "bucket": "needs_attention",
  "confidence": 0.95,
  "action": "keep_in_inbox",
  "reason": "Direct request to see portal for details.",
  "signals": [
    "direct_request"
  ],
  "auto_move_ok": false
}
PERF: {
  "prompt_tokens": 857,
  "gen_tokens": 41,
  "prompt_ms": 73.6555,
  "gen_ms": 361.8253,
  "total_ms": 1164.3707
}
=================================================================== short test summary info ====================================================================
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[calendar_or_travel_02.json] - AssertionError: [calendar_or_travel_02.json] auto_move_ok failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[calendar_or_travel_03.json] - AssertionError: [calendar_or_travel_03.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[phish_01.json] - AssertionError: [phish_01.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[spam_or_scams_01.json] - AssertionError: [spam_or_scams_01.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[spam_or_scams_02.json] - AssertionError: [spam_or_scams_02.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[uncertain_01.json] - AssertionError: [uncertain_01.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[uncertain_02.json] - AssertionError: [uncertain_02.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[uncertain_03.json] - AssertionError: [uncertain_03.json] bucket_in failed
8 failed, 20 passed, 11 deselected in 43.00s

(.venv) C:\Users\rezaf\dev\mailtriage>set OLLAMA_MODEL=deepseek-r1:8b

(.venv) C:\Users\rezaf\dev\mailtriage>python -m pytest -m integration -q
.F................FFF...FFF.                                                                                                                              [100%]
=========================================================================== FAILURES ===========================================================================
_________________________________________________________ test_corpus_case[calendar_or_travel_02.json] _________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/calendar_or_travel_02.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x0000018C5F2274D0>

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

>       _assert_expectations(case_name, result, raw, expect)

tests\test_ollama_integration_corpus.py:208:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_ollama_integration_corpus.py:107: in _assert_expectations
    fail("auto_move_ok", bool(auto_move_ok), result.auto_move_ok)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'auto_move_ok', expected = False, actual = True

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [calendar_or_travel_02.json] auto_move_ok failed
E         expected: False
E         actual:   True
E
E       DEBUG:
E       {
E         "case": "calendar_or_travel_02.json",
E         "expect": {
E           "bucket_in": [
E             "calendar_or_travel"
E           ],
E           "min_confidence": 0.75,
E           "auto_move_ok": false,
E           "action": "keep_in_inbox"
E         },
E         "actual": {
E           "bucket": "calendar_or_travel",
E           "confidence": 0.95,
E           "action": "move_to_folder",
E           "auto_move_ok": true,
E           "reason": "Email about itinerary change with flight details.",
E           "signals": [
E             "looks_like_travel"
E           ]
E         },
E         "perf": {
E           "prompt_tokens": 917,
E           "gen_tokens": 48,
E           "total_ms": 796.5914
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: calendar_or_travel_02.json ---
EMAIL:
{
  "from": "Alaska Airlines <itinerary@alaskaair.com>",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "Itinerary change: Flight time updated",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<itinerary-ch-ic70dfm3@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "Your itinerary has changed.\n\n        Flight: AS 123\n        New departure: 6:15 PM (was 5:40 PM)\n        Date: Mar 6\n\n        Review your trip details in the app or website."
}
EXPECT:
{
  "bucket_in": [
    "calendar_or_travel"
  ],
  "min_confidence": 0.75,
  "auto_move_ok": false,
  "action": "keep_in_inbox"
}
LLM RESULT:
{
  "bucket": "calendar_or_travel",
  "confidence": 0.95,
  "action": "move_to_folder",
  "reason": "Email about itinerary change with flight details.",
  "signals": [
    "looks_like_travel"
  ],
  "auto_move_ok": true
}
PERF: {
  "prompt_tokens": 917,
  "gen_tokens": 48,
  "prompt_ms": 101.0207,
  "gen_ms": 466.8954,
  "total_ms": 796.5914
}
___________________________________________________________ test_corpus_case[spam_or_scams_01.json] ____________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/spam_or_scams_01.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x0000018C5F2274D0>

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

>       _assert_expectations(case_name, result, raw, expect)

tests\test_ollama_integration_corpus.py:208:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_ollama_integration_corpus.py:84: in _assert_expectations
    fail("bucket_in", bucket_in, result.bucket)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'bucket_in', expected = ['spam_or_scams'], actual = 'security_alert'

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [spam_or_scams_01.json] bucket_in failed
E         expected: ['spam_or_scams']
E         actual:   security_alert
E
E       DEBUG:
E       {
E         "case": "spam_or_scams_01.json",
E         "expect": {
E           "bucket_in": [
E             "spam_or_scams"
E           ],
E           "min_confidence": 0.8,
E           "auto_move_ok": false,
E           "action": "quarantine"
E         },
E         "actual": {
E           "bucket": "security_alert",
E           "confidence": 0.95,
E           "action": "keep_in_inbox",
E           "auto_move_ok": false,
E           "reason": "Suspicious activity detected, account limitation with immediate action required and deadline.",
E           "signals": [
E             "account_threat",
E             "direct_request"
E           ]
E         },
E         "perf": {
E           "prompt_tokens": 905,
E           "gen_tokens": 58,
E           "total_ms": 872.9283
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: spam_or_scams_01.json ---
EMAIL:
{
  "from": "PayPal Support <service@paypaI-security.com>",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "Your account is limited — action required",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<your-account-knxtmooc@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "We detected suspicious activity and limited your account.\n\n        Verify your identity immediately to restore access:\n        http://paypaI-security.com/verify\n\n        Failure to verify within 1 hour will permanently suspend your account."
}
EXPECT:
{
  "bucket_in": [
    "spam_or_scams"
  ],
  "min_confidence": 0.8,
  "auto_move_ok": false,
  "action": "quarantine"
}
LLM RESULT:
{
  "bucket": "security_alert",
  "confidence": 0.95,
  "action": "keep_in_inbox",
  "reason": "Suspicious activity detected, account limitation with immediate action required and deadline.",
  "signals": [
    "account_threat",
    "direct_request"
  ],
  "auto_move_ok": false
}
PERF: {
  "prompt_tokens": 905,
  "gen_tokens": 58,
  "prompt_ms": 96.2905,
  "gen_ms": 564.5703,
  "total_ms": 872.9283
}
___________________________________________________________ test_corpus_case[spam_or_scams_02.json] ____________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/spam_or_scams_02.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x0000018C5F2274D0>

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

>       _assert_expectations(case_name, result, raw, expect)

tests\test_ollama_integration_corpus.py:208:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_ollama_integration_corpus.py:84: in _assert_expectations
    fail("bucket_in", bucket_in, result.bucket)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'bucket_in', expected = ['spam_or_scams'], actual = 'needs_attention'

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [spam_or_scams_02.json] bucket_in failed
E         expected: ['spam_or_scams']
E         actual:   needs_attention
E
E       DEBUG:
E       {
E         "case": "spam_or_scams_02.json",
E         "expect": {
E           "bucket_in": [
E             "spam_or_scams"
E           ],
E           "min_confidence": 0.8,
E           "auto_move_ok": false,
E           "action": "quarantine"
E         },
E         "actual": {
E           "bucket": "needs_attention",
E           "confidence": 0.95,
E           "action": "keep_in_inbox",
E           "auto_move_ok": false,
E           "reason": "Direct request to confirm account to avoid deactivation.",
E           "signals": [
E             "has_direct_request"
E           ]
E         },
E         "perf": {
E           "prompt_tokens": 905,
E           "gen_tokens": 49,
E           "total_ms": 805.8431
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: spam_or_scams_02.json ---
EMAIL:
{
  "from": "IT Helpdesk <helpdesk@illinois-security.com>",
  "to": "Reza <reza@illinois.edu>",
  "cc": "",
  "subject": "Mailbox storage exceeded — confirm now",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<mailbox-stor-cjth4j1v@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "Your mailbox has exceeded the storage limit.\n\n        Click to re-validate your account and avoid deactivation:\n        http://illinois-security.com/reauth\n\n        This must be completed today."
}
EXPECT:
{
  "bucket_in": [
    "spam_or_scams"
  ],
  "min_confidence": 0.8,
  "auto_move_ok": false,
  "action": "quarantine"
}
LLM RESULT:
{
  "bucket": "needs_attention",
  "confidence": 0.95,
  "action": "keep_in_inbox",
  "reason": "Direct request to confirm account to avoid deactivation.",
  "signals": [
    "has_direct_request"
  ],
  "auto_move_ok": false
}
PERF: {
  "prompt_tokens": 905,
  "gen_tokens": 49,
  "prompt_ms": 101.5806,
  "gen_ms": 483.1157,
  "total_ms": 805.8431
}
___________________________________________________________ test_corpus_case[spam_or_scams_03.json] ____________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/spam_or_scams_03.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x0000018C5F2274D0>

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

>       _assert_expectations(case_name, result, raw, expect)

tests\test_ollama_integration_corpus.py:208:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_ollama_integration_corpus.py:84: in _assert_expectations
    fail("bucket_in", bucket_in, result.bucket)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'bucket_in', expected = ['spam_or_scams'], actual = 'needs_attention'

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [spam_or_scams_03.json] bucket_in failed
E         expected: ['spam_or_scams']
E         actual:   needs_attention
E
E       DEBUG:
E       {
E         "case": "spam_or_scams_03.json",
E         "expect": {
E           "bucket_in": [
E             "spam_or_scams"
E           ],
E           "min_confidence": 0.8,
E           "auto_move_ok": false,
E           "action": "quarantine"
E         },
E         "actual": {
E           "bucket": "needs_attention",
E           "confidence": 0.95,
E           "action": "keep_in_inbox",
E           "auto_move_ok": false,
E           "reason": "Email requests payment for package delivery with a link, indicating a human action required.",
E           "signals": [
E             "has_direct_request"
E           ]
E         },
E         "perf": {
E           "prompt_tokens": 908,
E           "gen_tokens": 55,
E           "total_ms": 860.1749
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: spam_or_scams_03.json ---
EMAIL:
{
  "from": "Delivery Notice <noreply@shipments-track.net>",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "We couldn't deliver your package (fee required)",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<we-couldn't--uyrskbv1@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "We attempted delivery but require a small redelivery fee.\n\n        Pay the fee here to schedule redelivery:\n        http://shipments-track.net/pay\n\n        If unpaid, your package will be returned."
}
EXPECT:
{
  "bucket_in": [
    "spam_or_scams"
  ],
  "min_confidence": 0.8,
  "auto_move_ok": false,
  "action": "quarantine"
}
LLM RESULT:
{
  "bucket": "needs_attention",
  "confidence": 0.95,
  "action": "keep_in_inbox",
  "reason": "Email requests payment for package delivery with a link, indicating a human action required.",
  "signals": [
    "has_direct_request"
  ],
  "auto_move_ok": false
}
PERF: {
  "prompt_tokens": 908,
  "gen_tokens": 55,
  "prompt_ms": 97.0408,
  "gen_ms": 540.3108,
  "total_ms": 860.1749
}
_____________________________________________________________ test_corpus_case[uncertain_01.json] ______________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/uncertain_01.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x0000018C5F2274D0>

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

>       _assert_expectations(case_name, result, raw, expect)

tests\test_ollama_integration_corpus.py:208:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_ollama_integration_corpus.py:84: in _assert_expectations
    fail("bucket_in", bucket_in, result.bucket)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'bucket_in', expected = ['uncertain'], actual = 'needs_attention'

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [uncertain_01.json] bucket_in failed
E         expected: ['uncertain']
E         actual:   needs_attention
E
E       DEBUG:
E       {
E         "case": "uncertain_01.json",
E         "expect": {
E           "bucket_in": [
E             "uncertain"
E           ],
E           "max_confidence": 0.69,
E           "auto_move_ok": false,
E           "action": "do_nothing"
E         },
E         "actual": {
E           "bucket": "needs_attention",
E           "confidence": 0.95,
E           "action": "keep_in_inbox",
E           "auto_move_ok": false,
E           "reason": "Direct request to confirm details.",
E           "signals": [
E             "has_direct_request"
E           ]
E         },
E         "perf": {
E           "prompt_tokens": 865,
E           "gen_tokens": 45,
E           "total_ms": 744.2287
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: uncertain_01.json ---
EMAIL:
{
  "from": "Pat <pat@unknown-domain.net>",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "Re: your request",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<re:-your-req-ajrh0oos@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "Following up on your request — can you confirm the details?"
}
EXPECT:
{
  "bucket_in": [
    "uncertain"
  ],
  "max_confidence": 0.69,
  "auto_move_ok": false,
  "action": "do_nothing"
}
LLM RESULT:
{
  "bucket": "needs_attention",
  "confidence": 0.95,
  "action": "keep_in_inbox",
  "reason": "Direct request to confirm details.",
  "signals": [
    "has_direct_request"
  ],
  "auto_move_ok": false
}
PERF: {
  "prompt_tokens": 865,
  "gen_tokens": 45,
  "prompt_ms": 84.816,
  "gen_ms": 438.5987,
  "total_ms": 744.2287
}
_____________________________________________________________ test_corpus_case[uncertain_02.json] ______________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/uncertain_02.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x0000018C5F2274D0>

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

>       _assert_expectations(case_name, result, raw, expect)

tests\test_ollama_integration_corpus.py:208:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_ollama_integration_corpus.py:84: in _assert_expectations
    fail("bucket_in", bucket_in, result.bucket)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'bucket_in', expected = ['uncertain'], actual = 'social_notification'

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [uncertain_02.json] bucket_in failed
E         expected: ['uncertain']
E         actual:   social_notification
E
E       DEBUG:
E       {
E         "case": "uncertain_02.json",
E         "expect": {
E           "bucket_in": [
E             "uncertain"
E           ],
E           "max_confidence": 0.69,
E           "auto_move_ok": false,
E           "action": "do_nothing"
E         },
E         "actual": {
E           "bucket": "social_notification",
E           "confidence": 0.95,
E           "action": "move_to_folder",
E           "auto_move_ok": true,
E           "reason": "Automated notification from service, content indicates social/collaboration platform update.",
E           "signals": [
E             "looks_like_social_notification"
E           ]
E         },
E         "perf": {
E           "prompt_tokens": 853,
E           "gen_tokens": 56,
E           "total_ms": 860.2814
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: uncertain_02.json ---
EMAIL:
{
  "from": "noreply@service.example",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "Notification",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<notification-ndvruz3t@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "This is an automated notification regarding your recent activity."
}
EXPECT:
{
  "bucket_in": [
    "uncertain"
  ],
  "max_confidence": 0.69,
  "auto_move_ok": false,
  "action": "do_nothing"
}
LLM RESULT:
{
  "bucket": "social_notification",
  "confidence": 0.95,
  "action": "move_to_folder",
  "reason": "Automated notification from service, content indicates social/collaboration platform update.",
  "signals": [
    "looks_like_social_notification"
  ],
  "auto_move_ok": true
}
PERF: {
  "prompt_tokens": 853,
  "gen_tokens": 56,
  "prompt_ms": 77.6654,
  "gen_ms": 559.7626,
  "total_ms": 860.2814
}
_____________________________________________________________ test_corpus_case[uncertain_03.json] ______________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/uncertain_03.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x0000018C5F2274D0>

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

>       _assert_expectations(case_name, result, raw, expect)

tests\test_ollama_integration_corpus.py:208:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_ollama_integration_corpus.py:84: in _assert_expectations
    fail("bucket_in", bucket_in, result.bucket)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'bucket_in', expected = ['uncertain'], actual = 'needs_attention'

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [uncertain_03.json] bucket_in failed
E         expected: ['uncertain']
E         actual:   needs_attention
E
E       DEBUG:
E       {
E         "case": "uncertain_03.json",
E         "expect": {
E           "bucket_in": [
E             "uncertain"
E           ],
E           "max_confidence": 0.69,
E           "auto_move_ok": false,
E           "action": "do_nothing"
E         },
E         "actual": {
E           "bucket": "needs_attention",
E           "confidence": 0.95,
E           "action": "keep_in_inbox",
E           "auto_move_ok": false,
E           "reason": "Direct request to check ticket update.",
E           "signals": [
E             "has_direct_request"
E           ]
E         },
E         "perf": {
E           "prompt_tokens": 860,
E           "gen_tokens": 46,
E           "total_ms": 753.2616
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: uncertain_03.json ---
EMAIL:
{
  "from": "Support <support@vendor.example>",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "Ticket update",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<ticket-updat-76rtdmfl@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "Your ticket has been updated. Please see the portal for details."
}
EXPECT:
{
  "bucket_in": [
    "uncertain"
  ],
  "max_confidence": 0.69,
  "auto_move_ok": false,
  "action": "do_nothing"
}
LLM RESULT:
{
  "bucket": "needs_attention",
  "confidence": 0.95,
  "action": "keep_in_inbox",
  "reason": "Direct request to check ticket update.",
  "signals": [
    "has_direct_request"
  ],
  "auto_move_ok": false
}
PERF: {
  "prompt_tokens": 860,
  "gen_tokens": 46,
  "prompt_ms": 76.8458,
  "gen_ms": 453.7952,
  "total_ms": 753.2616
}
=================================================================== short test summary info ====================================================================
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[calendar_or_travel_02.json] - AssertionError: [calendar_or_travel_02.json] auto_move_ok failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[spam_or_scams_01.json] - AssertionError: [spam_or_scams_01.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[spam_or_scams_02.json] - AssertionError: [spam_or_scams_02.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[spam_or_scams_03.json] - AssertionError: [spam_or_scams_03.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[uncertain_01.json] - AssertionError: [uncertain_01.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[uncertain_02.json] - AssertionError: [uncertain_02.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[uncertain_03.json] - AssertionError: [uncertain_03.json] bucket_in failed
7 failed, 21 passed, 11 deselected in 27.40s