(.venv) C:\Users\rezaf\dev\mailtriage>set OLLAMA_MODEL=llama3.1:8b

(.venv) C:\Users\rezaf\dev\mailtriage>python -m pytest -m integration -q
..F.......F.......FF....FFF.                                                                                                                              [100%]
=========================================================================== FAILURES ===========================================================================
_________________________________________________________ test_corpus_case[calendar_or_travel_03.json] _________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/calendar_or_travel_03.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000001902A2574D0>

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
E           "confidence": 0.9,
E           "action": "move_to_folder",
E           "auto_move_ok": true,
E           "reason": "Booking confirmation with order number and link to modify reservation.",
E           "signals": [
E             "looks_like_transaction",
E             "has_order_number"
E           ]
E         },
E         "perf": {
E           "prompt_tokens": 951,
E           "gen_tokens": 67,
E           "total_ms": 1766.2854
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
  "confidence": 0.9,
  "action": "move_to_folder",
  "reason": "Booking confirmation with order number and link to modify reservation.",
  "signals": [
    "looks_like_transaction",
    "has_order_number"
  ],
  "auto_move_ok": true
}
PERF: {
  "prompt_tokens": 951,
  "gen_tokens": 67,
  "prompt_ms": 89.1483,
  "gen_ms": 561.4735,
  "total_ms": 1766.2854
}
_______________________________________________________________ test_corpus_case[phish_01.json] ________________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/phish_01.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000001902A2574D0>

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
E           "confidence": 0.9,
E           "action": "keep_in_inbox",
E           "auto_move_ok": false,
E           "reason": "contains phrases like 'Your payroll account will be suspended' and has a link to verify",
E           "signals": []
E         },
E         "perf": {
E           "prompt_tokens": 932,
E           "gen_tokens": 61,
E           "total_ms": 1614.4099
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
  "confidence": 0.9,
  "action": "keep_in_inbox",
  "reason": "contains phrases like 'Your payroll account will be suspended' and has a link to verify",
  "signals": [],
  "auto_move_ok": false
}
PERF: {
  "prompt_tokens": 932,
  "gen_tokens": 61,
  "prompt_ms": 82.7405,
  "gen_ms": 506.0366,
  "total_ms": 1614.4099
}
___________________________________________________________ test_corpus_case[spam_or_scams_01.json] ____________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/spam_or_scams_01.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000001902A2574D0>

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
E           "confidence": 0.9,
E           "action": "keep_in_inbox",
E           "auto_move_ok": false,
E           "reason": "contains phrases like 'Verify your identity immediately' and a short deadline (1 hour)",
E           "signals": []
E         },
E         "perf": {
E           "prompt_tokens": 945,
E           "gen_tokens": 60,
E           "total_ms": 1560.9223
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
  "confidence": 0.9,
  "action": "keep_in_inbox",
  "reason": "contains phrases like 'Verify your identity immediately' and a short deadline (1 hour)",
  "signals": [],
  "auto_move_ok": false
}
PERF: {
  "prompt_tokens": 945,
  "gen_tokens": 60,
  "prompt_ms": 88.4199,
  "gen_ms": 493.415,
  "total_ms": 1560.9223
}
___________________________________________________________ test_corpus_case[spam_or_scams_02.json] ____________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/spam_or_scams_02.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000001902A2574D0>

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
E           "confidence": 1.0,
E           "action": "keep_in_inbox",
E           "auto_move_ok": false,
E           "reason": "direct_request, has_deadline",
E           "signals": []
E         },
E         "perf": {
E           "prompt_tokens": 945,
E           "gen_tokens": 50,
E           "total_ms": 1304.4186
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
  "confidence": 1.0,
  "action": "keep_in_inbox",
  "reason": "direct_request, has_deadline",
  "signals": [],
  "auto_move_ok": false
}
PERF: {
  "prompt_tokens": 945,
  "gen_tokens": 50,
  "prompt_ms": 87.8494,
  "gen_ms": 405.6721,
  "total_ms": 1304.4186
}
_____________________________________________________________ test_corpus_case[uncertain_01.json] ______________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/uncertain_01.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000001902A2574D0>

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
E           "confidence": 1.0,
E           "action": "keep_in_inbox",
E           "auto_move_ok": false,
E           "reason": "direct_request",
E           "signals": []
E         },
E         "perf": {
E           "prompt_tokens": 905,
E           "gen_tokens": 46,
E           "total_ms": 1178.1947
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
  "confidence": 1.0,
  "action": "keep_in_inbox",
  "reason": "direct_request",
  "signals": [],
  "auto_move_ok": false
}
PERF: {
  "prompt_tokens": 905,
  "gen_tokens": 46,
  "prompt_ms": 68.3674,
  "gen_ms": 373.7136,
  "total_ms": 1178.1947
}
_____________________________________________________________ test_corpus_case[uncertain_02.json] ______________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/uncertain_02.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000001902A2574D0>

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
E           "confidence": 1.0,
E           "action": "move_to_folder",
E           "auto_move_ok": true,
E           "reason": "looks_like_social_notification",
E           "signals": []
E         },
E         "perf": {
E           "prompt_tokens": 893,
E           "gen_tokens": 47,
E           "total_ms": 1201.7417
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
  "confidence": 1.0,
  "action": "move_to_folder",
  "reason": "looks_like_social_notification",
  "signals": [],
  "auto_move_ok": true
}
PERF: {
  "prompt_tokens": 893,
  "gen_tokens": 47,
  "prompt_ms": 68.4984,
  "gen_ms": 379.2192,
  "total_ms": 1201.7417
}
_____________________________________________________________ test_corpus_case[uncertain_03.json] ______________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/uncertain_03.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000001902A2574D0>

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
E           "confidence": 1.0,
E           "action": "keep_in_inbox",
E           "auto_move_ok": false,
E           "reason": "direct_request",
E           "signals": []
E         },
E         "perf": {
E           "prompt_tokens": 899,
E           "gen_tokens": 46,
E           "total_ms": 1175.5869
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
  "confidence": 1.0,
  "action": "keep_in_inbox",
  "reason": "direct_request",
  "signals": [],
  "auto_move_ok": false
}
PERF: {
  "prompt_tokens": 899,
  "gen_tokens": 46,
  "prompt_ms": 67.9983,
  "gen_ms": 372.6878,
  "total_ms": 1175.5869
}
=================================================================== short test summary info ====================================================================
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[calendar_or_travel_03.json] - AssertionError: [calendar_or_travel_03.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[phish_01.json] - AssertionError: [phish_01.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[spam_or_scams_01.json] - AssertionError: [spam_or_scams_01.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[spam_or_scams_02.json] - AssertionError: [spam_or_scams_02.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[uncertain_01.json] - AssertionError: [uncertain_01.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[uncertain_02.json] - AssertionError: [uncertain_02.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[uncertain_03.json] - AssertionError: [uncertain_03.json] bucket_in failed
7 failed, 21 passed, 11 deselected in 47.48s