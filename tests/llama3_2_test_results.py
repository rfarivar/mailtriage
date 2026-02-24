(.venv) C:\Users\rezaf\dev\mailtriage>set OLLAMA_MODEL=llama3.2

(.venv) C:\Users\rezaf\dev\mailtriage>python -m pytest -m integration -q
FFF................FF...FFFF                                                                                                                              [100%]
=========================================================================== FAILURES ===========================================================================
_________________________________________________________ test_corpus_case[calendar_or_travel_01.json] _________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/calendar_or_travel_01.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x0000015AB81874D0>

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
E       AssertionError: [calendar_or_travel_01.json] auto_move_ok failed
E         expected: False
E         actual:   True
E
E       DEBUG:
E       {
E         "case": "calendar_or_travel_01.json",
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
E           "confidence": 1.0,
E           "action": "keep_in_inbox",
E           "auto_move_ok": true,
E           "reason": "looks_like_invite",
E           "signals": []
E         },
E         "perf": {
E           "prompt_tokens": 971,
E           "gen_tokens": 49,
E           "total_ms": 2783.5798
E         }
E       }

tests\test_ollama_integration_corpus.py:74: AssertionError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: calendar_or_travel_01.json ---
EMAIL:
{
  "from": "UIUC Calendar <calendar@illinois.edu>",
  "to": "Reza <reza@illinois.edu>",
  "cc": "",
  "subject": "Invitation: Weekly Capstone Sprint Review (Mon 2pm)",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<invitation:--s29onbdu@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "You have been invited to an event.\n\n        Title: Weekly Capstone Sprint Review\n        When: Mon Feb 23, 2:00–2:30 PM (PT)\n        Where: Zoom (link in calendar invite)\n\n        Please accept or decline."
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
  "confidence": 1.0,
  "action": "keep_in_inbox",
  "reason": "looks_like_invite",
  "signals": [],
  "auto_move_ok": true
}
PERF: {
  "prompt_tokens": 971,
  "gen_tokens": 49,
  "prompt_ms": 123.6019,
  "gen_ms": 236.4568,
  "total_ms": 2783.5798
}
_________________________________________________________ test_corpus_case[calendar_or_travel_02.json] _________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/calendar_or_travel_02.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x0000015AB81874D0>

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
E           "confidence": 1.0,
E           "action": "keep_in_inbox",
E           "auto_move_ok": true,
E           "reason": "looks_like_invite",
E           "signals": []
E         },
E         "perf": {
E           "prompt_tokens": 962,
E           "gen_tokens": 49,
E           "total_ms": 1022.4063
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
  "confidence": 1.0,
  "action": "keep_in_inbox",
  "reason": "looks_like_invite",
  "signals": [],
  "auto_move_ok": true
}
PERF: {
  "prompt_tokens": 962,
  "gen_tokens": 49,
  "prompt_ms": 42.4701,
  "gen_ms": 223.9873,
  "total_ms": 1022.4063
}
_________________________________________________________ test_corpus_case[calendar_or_travel_03.json] _________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/calendar_or_travel_03.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x0000015AB81874D0>

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
tests\test_ollama_integration_corpus.py:112: in _assert_expectations
    fail("action", action, result.action)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

rule = 'action', expected = 'move_to_folder', actual = 'keep_in_inbox'

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [calendar_or_travel_03.json] action failed
E         expected: move_to_folder
E         actual:   keep_in_inbox
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
E           "bucket": "calendar_or_travel",
E           "confidence": 1.0,
E           "action": "keep_in_inbox",
E           "auto_move_ok": true,
E           "reason": "looks_like_invite",
E           "signals": []
E         },
E         "perf": {
E           "prompt_tokens": 961,
E           "gen_tokens": 49,
E           "total_ms": 1026.999
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
  "bucket": "calendar_or_travel",
  "confidence": 1.0,
  "action": "keep_in_inbox",
  "reason": "looks_like_invite",
  "signals": [],
  "auto_move_ok": true
}
PERF: {
  "prompt_tokens": 961,
  "gen_tokens": 49,
  "prompt_ms": 43.6799,
  "gen_ms": 231.6282,
  "total_ms": 1026.999
}
___________________________________________________________ test_corpus_case[spam_or_scams_02.json] ____________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/spam_or_scams_02.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x0000015AB81874D0>

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
E           "reason": "direct_request",
E           "signals": []
E         },
E         "perf": {
E           "prompt_tokens": 955,
E           "gen_tokens": 45,
E           "total_ms": 991.9097
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
  "reason": "direct_request",
  "signals": [],
  "auto_move_ok": false
}
PERF: {
  "prompt_tokens": 955,
  "gen_tokens": 45,
  "prompt_ms": 44.5241,
  "gen_ms": 207.7499,
  "total_ms": 991.9097
}
___________________________________________________________ test_corpus_case[spam_or_scams_03.json] ____________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/spam_or_scams_03.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x0000015AB81874D0>

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
E           "reason": "looks_like_transaction",
E           "signals": [
E             "looks_like_transaction"
E           ]
E         },
E         "perf": {
E           "prompt_tokens": 958,
E           "gen_tokens": 38,
E           "total_ms": 858.0141
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
  "reason": "looks_like_transaction",
  "signals": [
    "looks_like_transaction"
  ],
  "auto_move_ok": true
}
PERF: {
  "prompt_tokens": 958,
  "gen_tokens": 38,
  "prompt_ms": 43.5552,
  "gen_ms": 173.0181,
  "total_ms": 858.0141
}
_____________________________________________________________ test_corpus_case[uncertain_01.json] ______________________________________________________________

self = <mailtriage.OllamaClient object at 0x0000015AB81874D0>
email_obj = {'body_excerpt': 'Following up on your request — can you confirm the details?', 'cc': '', 'date': 'Fri, 20 Feb 2026 10:00:00 -0800', 'from': 'Pat <pat@unknown-domain.net>', ...}

    def triage_email(self, email_obj: Dict[str, Any]) -> Tuple[TriageResult, Dict[str, Any]]:
        """
        Returns (parsed_result, raw_ollama_response)
        """
        # system = (
        #     "You are an email triage classifier. "
        #     "Goal: decide whether the user should personally pay attention. "
        #     "Be conservative with auto_move_ok: only true if it is clearly non-urgent and non-personal. "
        #     "Never recommend moving human-to-human emails to marketing folders. "
        #     "If uncertain, set bucket='uncertain', confidence<0.7, action='do_nothing', auto_move_ok=false."
        # )

        system = """
        You are an email triage classifier.

        IMPORTANT:
        - Choose the BEST bucket (what it IS). Do not use 'uncertain' just because it's urgent.
        - 'uncertain' is only for genuinely ambiguous/insufficient content.
        - Use the provided email fields and _features. Do NOT invent signals that contradict _features.
        - List headers (List-ID / List-Unsubscribe) indicate automated mail, but do NOT automatically mean marketing.

        BUCKET DEFINITIONS (pick exactly one):
        1) needs_attention:
        Human-to-human or team email that asks the user to do something (review/confirm/decide/respond) or has a deadline.
        Usually no list headers. May include attachments mentioned.

        2) transactional:
        Receipts, invoices, shipping updates, payment confirmations, bills, confirmations with amounts/order numbers.
        Not primarily promotional.

        3) security_alert:
        Login alerts, password reset requests, 2FA/OTP codes, account security notices.
        Often contains phrases like "If this wasn't you..." and may contain a short code.

        4) calendar_or_travel:
        Calendar invitations/RSVP/accept/decline; travel itinerary changes; hotel/flight booking confirmations.

        5) newsletter_or_marketing:
        Newsletters, promotions, sales, discounts, offers, marketing content (often periodic).
        List headers are common, but content must look like a promo/newsletter.

        6) social_notification:
        Notifications from social/collaboration platforms (LinkedIn, GitHub, X, etc.): new message, comment, follower, mention, digest.
        May have list headers but content is a notification, not a sale/offer.

        7) spam_or_scams:
        Phishing, scams, threats ("account suspended"), suspicious links to verify credentials, impersonation domains.
        Especially if _features.has_link and _features.has_direct_request with threats.

        8) uncertain:
        Too little information to classify confidently.

        PRECEDENCE (if multiple match, choose earlier):
        spam_or_scams > security_alert > calendar_or_travel > transactional > social_notification > newsletter_or_marketing > needs_attention > uncertain

        ACTIONS (be consistent):
        - needs_attention, security_alert, calendar_or_travel -> action=keep_in_inbox, auto_move_ok=false
        - transactional, social_notification, newsletter_or_marketing -> action=move_to_folder, auto_move_ok=true
        - spam_or_scams -> action=quarantine, auto_move_ok=false (conservative)
        - uncertain -> action=do_nothing, auto_move_ok=false

        SIGNALS:
        Return 1-3 short signals that are consistent with _features and the email content.
        Examples: direct_request, has_deadline, has_otp_code, has_discount_language, looks_like_transaction, looks_like_invite,
        looks_like_social_notification, suspicious_link, account_threat.

        Output MUST be ONLY JSON matching the schema.
        """.strip()

        email_for_llm = dict(email_obj)
        email_for_llm["_features"] = compute_features(email_obj)

        user = (
            "Classify this email. Return ONLY JSON that matches the provided schema.\n\n"
            f"Email:\n{json.dumps(email_for_llm, ensure_ascii=False, indent=2)}"
        )

        payload = {
            "model": self.model,
            "stream": False,
            "format": TRIAGE_SCHEMA,  # enforce schema
            "think": False,  # <-- KEY: disable thinking trace for thinking-capable models
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "options": {
                "temperature": 0.0,
                "num_ctx": 2048,      # <- context window; for llama 3.2:3b can go as high as 16K, but for
                                      # llama-3.1:8b and qwen3:8b and deepseek-r1:8b has to remain under 8K or spills into CPU
                "num_predict": 256,   # <- cap output tokens (optional but good practice)
            },
        }

        # Ollama chat API: POST /api/chat :contentReference[oaicite:1]{index=1}
        url = f"{self.base_url}/api/chat"
        resp = requests.post(url, json=payload, timeout=self.timeout_s)
        resp.raise_for_status()
        raw = resp.json()

        msg = raw.get("message", {}) or {}
        content = (msg.get("content") or "").strip()
        if not content:
            raise RuntimeError(
                f"Empty message.content from model={self.model}. "
                f"done_reason={raw.get('done_reason')} eval_count={raw.get('eval_count')}. "
                f"If this is a thinking model, set think=False and increase num_predict. "
                f"thinking_preview={repr((msg.get('thinking') or '')[:200])}"
            )

        try:
>           parsed = TriageResult.model_validate_json(content)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E           pydantic_core._pydantic_core.ValidationError: 1 validation error for TriageResult
E             Invalid JSON: EOF while parsing a string at line 1 column 1080 [type=json_invalid, input_value='{"bucket":"needs_attenti..._request, has_deadline,', input_type=str]
E               For further information visit https://errors.pydantic.dev/2.12/v/json_invalid

mailtriage.py:306: ValidationError

The above exception was the direct cause of the following exception:

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/uncertain_01.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x0000015AB81874D0>

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

>       result, raw = ollama_client.triage_email(email_obj)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_ollama_integration_corpus.py:194:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <mailtriage.OllamaClient object at 0x0000015AB81874D0>
email_obj = {'body_excerpt': 'Following up on your request — can you confirm the details?', 'cc': '', 'date': 'Fri, 20 Feb 2026 10:00:00 -0800', 'from': 'Pat <pat@unknown-domain.net>', ...}

    def triage_email(self, email_obj: Dict[str, Any]) -> Tuple[TriageResult, Dict[str, Any]]:
        """
        Returns (parsed_result, raw_ollama_response)
        """
        # system = (
        #     "You are an email triage classifier. "
        #     "Goal: decide whether the user should personally pay attention. "
        #     "Be conservative with auto_move_ok: only true if it is clearly non-urgent and non-personal. "
        #     "Never recommend moving human-to-human emails to marketing folders. "
        #     "If uncertain, set bucket='uncertain', confidence<0.7, action='do_nothing', auto_move_ok=false."
        # )

        system = """
        You are an email triage classifier.

        IMPORTANT:
        - Choose the BEST bucket (what it IS). Do not use 'uncertain' just because it's urgent.
        - 'uncertain' is only for genuinely ambiguous/insufficient content.
        - Use the provided email fields and _features. Do NOT invent signals that contradict _features.
        - List headers (List-ID / List-Unsubscribe) indicate automated mail, but do NOT automatically mean marketing.

        BUCKET DEFINITIONS (pick exactly one):
        1) needs_attention:
        Human-to-human or team email that asks the user to do something (review/confirm/decide/respond) or has a deadline.
        Usually no list headers. May include attachments mentioned.

        2) transactional:
        Receipts, invoices, shipping updates, payment confirmations, bills, confirmations with amounts/order numbers.
        Not primarily promotional.

        3) security_alert:
        Login alerts, password reset requests, 2FA/OTP codes, account security notices.
        Often contains phrases like "If this wasn't you..." and may contain a short code.

        4) calendar_or_travel:
        Calendar invitations/RSVP/accept/decline; travel itinerary changes; hotel/flight booking confirmations.

        5) newsletter_or_marketing:
        Newsletters, promotions, sales, discounts, offers, marketing content (often periodic).
        List headers are common, but content must look like a promo/newsletter.

        6) social_notification:
        Notifications from social/collaboration platforms (LinkedIn, GitHub, X, etc.): new message, comment, follower, mention, digest.
        May have list headers but content is a notification, not a sale/offer.

        7) spam_or_scams:
        Phishing, scams, threats ("account suspended"), suspicious links to verify credentials, impersonation domains.
        Especially if _features.has_link and _features.has_direct_request with threats.

        8) uncertain:
        Too little information to classify confidently.

        PRECEDENCE (if multiple match, choose earlier):
        spam_or_scams > security_alert > calendar_or_travel > transactional > social_notification > newsletter_or_marketing > needs_attention > uncertain

        ACTIONS (be consistent):
        - needs_attention, security_alert, calendar_or_travel -> action=keep_in_inbox, auto_move_ok=false
        - transactional, social_notification, newsletter_or_marketing -> action=move_to_folder, auto_move_ok=true
        - spam_or_scams -> action=quarantine, auto_move_ok=false (conservative)
        - uncertain -> action=do_nothing, auto_move_ok=false

        SIGNALS:
        Return 1-3 short signals that are consistent with _features and the email content.
        Examples: direct_request, has_deadline, has_otp_code, has_discount_language, looks_like_transaction, looks_like_invite,
        looks_like_social_notification, suspicious_link, account_threat.

        Output MUST be ONLY JSON matching the schema.
        """.strip()

        email_for_llm = dict(email_obj)
        email_for_llm["_features"] = compute_features(email_obj)

        user = (
            "Classify this email. Return ONLY JSON that matches the provided schema.\n\n"
            f"Email:\n{json.dumps(email_for_llm, ensure_ascii=False, indent=2)}"
        )

        payload = {
            "model": self.model,
            "stream": False,
            "format": TRIAGE_SCHEMA,  # enforce schema
            "think": False,  # <-- KEY: disable thinking trace for thinking-capable models
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "options": {
                "temperature": 0.0,
                "num_ctx": 2048,      # <- context window; for llama 3.2:3b can go as high as 16K, but for
                                      # llama-3.1:8b and qwen3:8b and deepseek-r1:8b has to remain under 8K or spills into CPU
                "num_predict": 256,   # <- cap output tokens (optional but good practice)
            },
        }

        # Ollama chat API: POST /api/chat :contentReference[oaicite:1]{index=1}
        url = f"{self.base_url}/api/chat"
        resp = requests.post(url, json=payload, timeout=self.timeout_s)
        resp.raise_for_status()
        raw = resp.json()

        msg = raw.get("message", {}) or {}
        content = (msg.get("content") or "").strip()
        if not content:
            raise RuntimeError(
                f"Empty message.content from model={self.model}. "
                f"done_reason={raw.get('done_reason')} eval_count={raw.get('eval_count')}. "
                f"If this is a thinking model, set think=False and increase num_predict. "
                f"thinking_preview={repr((msg.get('thinking') or '')[:200])}"
            )

        try:
            parsed = TriageResult.model_validate_json(content)
        except ValidationError as e:
>           raise RuntimeError(f"LLM returned invalid JSON for schema.\nRaw:\n{raw}\nContent:\n{content}\n\nError:\n{e}") from e
E           RuntimeError: LLM returned invalid JSON for schema.
E           Raw:
E           {'model': 'llama3.2', 'created_at': '2026-02-21T01:15:54.8972186Z', 'message': {'role': 'assistant', 'content': '{"bucket":"needs_attention","confidence":0.9,"action":"keep_in_inbox","reason":"direct_request, has_deadline, has_direct_request, looks_like_invite, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline,'}, 'done': True, 'done_reason': 'length', 'total_duration': 6600414100, 'load_duration': 134231400, 'prompt_eval_count': 915, 'prompt_eval_duration': 37412400, 'eval_count': 256, 'eval_duration': 2002629300}
E           Content:
E           {"bucket":"needs_attention","confidence":0.9,"action":"keep_in_inbox","reason":"direct_request, has_deadline, has_direct_request, looks_like_invite, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline,
E
E           Error:
E           1 validation error for TriageResult
E             Invalid JSON: EOF while parsing a string at line 1 column 1080 [type=json_invalid, input_value='{"bucket":"needs_attenti..._request, has_deadline,', input_type=str]
E               For further information visit https://errors.pydantic.dev/2.12/v/json_invalid

mailtriage.py:308: RuntimeError
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
_____________________________________________________________ test_corpus_case[uncertain_02.json] ______________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/uncertain_02.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x0000015AB81874D0>

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
E           "confidence": 0.5,
E           "action": "move_to_folder",
E           "auto_move_ok": true,
E           "reason": "looks_like_social_notification",
E           "signals": []
E         },
E         "perf": {
E           "prompt_tokens": 903,
E           "gen_tokens": 32,
E           "total_ms": 869.9999
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
  "confidence": 0.5,
  "action": "move_to_folder",
  "reason": "looks_like_social_notification",
  "signals": [],
  "auto_move_ok": true
}
PERF: {
  "prompt_tokens": 903,
  "gen_tokens": 32,
  "prompt_ms": 70.2756,
  "gen_ms": 252.0774,
  "total_ms": 869.9999
}
_____________________________________________________________ test_corpus_case[uncertain_03.json] ______________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/uncertain_03.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x0000015AB81874D0>

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
E           "prompt_tokens": 909,
E           "gen_tokens": 45,
E           "total_ms": 1094.4
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
  "prompt_tokens": 909,
  "gen_tokens": 45,
  "prompt_ms": 54.4377,
  "gen_ms": 351.6206,
  "total_ms": 1094.4
}
______________________________________________________________ test_ollama_smoke_structured_json _______________________________________________________________

self = <mailtriage.OllamaClient object at 0x0000015AB8D74F50>
email_obj = {'body_excerpt': 'Just a quick note: can you reply when you can?', 'date': 'Fri, 20 Feb 2026 10:00:00 -0800', 'from': 'Test <test@example.com>', 'message_id': '<test-1@example.com>', ...}

    def triage_email(self, email_obj: Dict[str, Any]) -> Tuple[TriageResult, Dict[str, Any]]:
        """
        Returns (parsed_result, raw_ollama_response)
        """
        # system = (
        #     "You are an email triage classifier. "
        #     "Goal: decide whether the user should personally pay attention. "
        #     "Be conservative with auto_move_ok: only true if it is clearly non-urgent and non-personal. "
        #     "Never recommend moving human-to-human emails to marketing folders. "
        #     "If uncertain, set bucket='uncertain', confidence<0.7, action='do_nothing', auto_move_ok=false."
        # )

        system = """
        You are an email triage classifier.

        IMPORTANT:
        - Choose the BEST bucket (what it IS). Do not use 'uncertain' just because it's urgent.
        - 'uncertain' is only for genuinely ambiguous/insufficient content.
        - Use the provided email fields and _features. Do NOT invent signals that contradict _features.
        - List headers (List-ID / List-Unsubscribe) indicate automated mail, but do NOT automatically mean marketing.

        BUCKET DEFINITIONS (pick exactly one):
        1) needs_attention:
        Human-to-human or team email that asks the user to do something (review/confirm/decide/respond) or has a deadline.
        Usually no list headers. May include attachments mentioned.

        2) transactional:
        Receipts, invoices, shipping updates, payment confirmations, bills, confirmations with amounts/order numbers.
        Not primarily promotional.

        3) security_alert:
        Login alerts, password reset requests, 2FA/OTP codes, account security notices.
        Often contains phrases like "If this wasn't you..." and may contain a short code.

        4) calendar_or_travel:
        Calendar invitations/RSVP/accept/decline; travel itinerary changes; hotel/flight booking confirmations.

        5) newsletter_or_marketing:
        Newsletters, promotions, sales, discounts, offers, marketing content (often periodic).
        List headers are common, but content must look like a promo/newsletter.

        6) social_notification:
        Notifications from social/collaboration platforms (LinkedIn, GitHub, X, etc.): new message, comment, follower, mention, digest.
        May have list headers but content is a notification, not a sale/offer.

        7) spam_or_scams:
        Phishing, scams, threats ("account suspended"), suspicious links to verify credentials, impersonation domains.
        Especially if _features.has_link and _features.has_direct_request with threats.

        8) uncertain:
        Too little information to classify confidently.

        PRECEDENCE (if multiple match, choose earlier):
        spam_or_scams > security_alert > calendar_or_travel > transactional > social_notification > newsletter_or_marketing > needs_attention > uncertain

        ACTIONS (be consistent):
        - needs_attention, security_alert, calendar_or_travel -> action=keep_in_inbox, auto_move_ok=false
        - transactional, social_notification, newsletter_or_marketing -> action=move_to_folder, auto_move_ok=true
        - spam_or_scams -> action=quarantine, auto_move_ok=false (conservative)
        - uncertain -> action=do_nothing, auto_move_ok=false

        SIGNALS:
        Return 1-3 short signals that are consistent with _features and the email content.
        Examples: direct_request, has_deadline, has_otp_code, has_discount_language, looks_like_transaction, looks_like_invite,
        looks_like_social_notification, suspicious_link, account_threat.

        Output MUST be ONLY JSON matching the schema.
        """.strip()

        email_for_llm = dict(email_obj)
        email_for_llm["_features"] = compute_features(email_obj)

        user = (
            "Classify this email. Return ONLY JSON that matches the provided schema.\n\n"
            f"Email:\n{json.dumps(email_for_llm, ensure_ascii=False, indent=2)}"
        )

        payload = {
            "model": self.model,
            "stream": False,
            "format": TRIAGE_SCHEMA,  # enforce schema
            "think": False,  # <-- KEY: disable thinking trace for thinking-capable models
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "options": {
                "temperature": 0.0,
                "num_ctx": 2048,      # <- context window; for llama 3.2:3b can go as high as 16K, but for
                                      # llama-3.1:8b and qwen3:8b and deepseek-r1:8b has to remain under 8K or spills into CPU
                "num_predict": 256,   # <- cap output tokens (optional but good practice)
            },
        }

        # Ollama chat API: POST /api/chat :contentReference[oaicite:1]{index=1}
        url = f"{self.base_url}/api/chat"
        resp = requests.post(url, json=payload, timeout=self.timeout_s)
        resp.raise_for_status()
        raw = resp.json()

        msg = raw.get("message", {}) or {}
        content = (msg.get("content") or "").strip()
        if not content:
            raise RuntimeError(
                f"Empty message.content from model={self.model}. "
                f"done_reason={raw.get('done_reason')} eval_count={raw.get('eval_count')}. "
                f"If this is a thinking model, set think=False and increase num_predict. "
                f"thinking_preview={repr((msg.get('thinking') or '')[:200])}"
            )

        try:
>           parsed = TriageResult.model_validate_json(content)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E           pydantic_core._pydantic_core.ValidationError: 1 validation error for TriageResult
E             Invalid JSON: EOF while parsing a string at line 1 column 1080 [type=json_invalid, input_value='{"bucket":"needs_attenti..._request, has_deadline,', input_type=str]
E               For further information visit https://errors.pydantic.dev/2.12/v/json_invalid

mailtriage.py:306: ValidationError

The above exception was the direct cause of the following exception:

    @pytest.mark.integration
    def test_ollama_smoke_structured_json():
        if os.getenv("RUN_OLLAMA_INTEGRATION") != "1":
            pytest.skip("Set RUN_OLLAMA_INTEGRATION=1 to run Ollama integration tests.")

        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

        if not _ollama_reachable(base_url):
            pytest.skip(f"Ollama not reachable at {base_url}")

        client = mt.OllamaClient(base_url=base_url, model=model, timeout_s=60)
>       result, _ = client.triage_email({
            "from": "Test <test@example.com>",
            "to": "You <you@example.com>",
            "subject": "hello",
            "date": "Fri, 20 Feb 2026 10:00:00 -0800",
            "message_id": "<test-1@example.com>",
            "body_excerpt": "Just a quick note: can you reply when you can?",
        })

tests\test_ollama_integration_smoke.py:24:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <mailtriage.OllamaClient object at 0x0000015AB8D74F50>
email_obj = {'body_excerpt': 'Just a quick note: can you reply when you can?', 'date': 'Fri, 20 Feb 2026 10:00:00 -0800', 'from': 'Test <test@example.com>', 'message_id': '<test-1@example.com>', ...}

    def triage_email(self, email_obj: Dict[str, Any]) -> Tuple[TriageResult, Dict[str, Any]]:
        """
        Returns (parsed_result, raw_ollama_response)
        """
        # system = (
        #     "You are an email triage classifier. "
        #     "Goal: decide whether the user should personally pay attention. "
        #     "Be conservative with auto_move_ok: only true if it is clearly non-urgent and non-personal. "
        #     "Never recommend moving human-to-human emails to marketing folders. "
        #     "If uncertain, set bucket='uncertain', confidence<0.7, action='do_nothing', auto_move_ok=false."
        # )

        system = """
        You are an email triage classifier.

        IMPORTANT:
        - Choose the BEST bucket (what it IS). Do not use 'uncertain' just because it's urgent.
        - 'uncertain' is only for genuinely ambiguous/insufficient content.
        - Use the provided email fields and _features. Do NOT invent signals that contradict _features.
        - List headers (List-ID / List-Unsubscribe) indicate automated mail, but do NOT automatically mean marketing.

        BUCKET DEFINITIONS (pick exactly one):
        1) needs_attention:
        Human-to-human or team email that asks the user to do something (review/confirm/decide/respond) or has a deadline.
        Usually no list headers. May include attachments mentioned.

        2) transactional:
        Receipts, invoices, shipping updates, payment confirmations, bills, confirmations with amounts/order numbers.
        Not primarily promotional.

        3) security_alert:
        Login alerts, password reset requests, 2FA/OTP codes, account security notices.
        Often contains phrases like "If this wasn't you..." and may contain a short code.

        4) calendar_or_travel:
        Calendar invitations/RSVP/accept/decline; travel itinerary changes; hotel/flight booking confirmations.

        5) newsletter_or_marketing:
        Newsletters, promotions, sales, discounts, offers, marketing content (often periodic).
        List headers are common, but content must look like a promo/newsletter.

        6) social_notification:
        Notifications from social/collaboration platforms (LinkedIn, GitHub, X, etc.): new message, comment, follower, mention, digest.
        May have list headers but content is a notification, not a sale/offer.

        7) spam_or_scams:
        Phishing, scams, threats ("account suspended"), suspicious links to verify credentials, impersonation domains.
        Especially if _features.has_link and _features.has_direct_request with threats.

        8) uncertain:
        Too little information to classify confidently.

        PRECEDENCE (if multiple match, choose earlier):
        spam_or_scams > security_alert > calendar_or_travel > transactional > social_notification > newsletter_or_marketing > needs_attention > uncertain

        ACTIONS (be consistent):
        - needs_attention, security_alert, calendar_or_travel -> action=keep_in_inbox, auto_move_ok=false
        - transactional, social_notification, newsletter_or_marketing -> action=move_to_folder, auto_move_ok=true
        - spam_or_scams -> action=quarantine, auto_move_ok=false (conservative)
        - uncertain -> action=do_nothing, auto_move_ok=false

        SIGNALS:
        Return 1-3 short signals that are consistent with _features and the email content.
        Examples: direct_request, has_deadline, has_otp_code, has_discount_language, looks_like_transaction, looks_like_invite,
        looks_like_social_notification, suspicious_link, account_threat.

        Output MUST be ONLY JSON matching the schema.
        """.strip()

        email_for_llm = dict(email_obj)
        email_for_llm["_features"] = compute_features(email_obj)

        user = (
            "Classify this email. Return ONLY JSON that matches the provided schema.\n\n"
            f"Email:\n{json.dumps(email_for_llm, ensure_ascii=False, indent=2)}"
        )

        payload = {
            "model": self.model,
            "stream": False,
            "format": TRIAGE_SCHEMA,  # enforce schema
            "think": False,  # <-- KEY: disable thinking trace for thinking-capable models
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "options": {
                "temperature": 0.0,
                "num_ctx": 2048,      # <- context window; for llama 3.2:3b can go as high as 16K, but for
                                      # llama-3.1:8b and qwen3:8b and deepseek-r1:8b has to remain under 8K or spills into CPU
                "num_predict": 256,   # <- cap output tokens (optional but good practice)
            },
        }

        # Ollama chat API: POST /api/chat :contentReference[oaicite:1]{index=1}
        url = f"{self.base_url}/api/chat"
        resp = requests.post(url, json=payload, timeout=self.timeout_s)
        resp.raise_for_status()
        raw = resp.json()

        msg = raw.get("message", {}) or {}
        content = (msg.get("content") or "").strip()
        if not content:
            raise RuntimeError(
                f"Empty message.content from model={self.model}. "
                f"done_reason={raw.get('done_reason')} eval_count={raw.get('eval_count')}. "
                f"If this is a thinking model, set think=False and increase num_predict. "
                f"thinking_preview={repr((msg.get('thinking') or '')[:200])}"
            )

        try:
            parsed = TriageResult.model_validate_json(content)
        except ValidationError as e:
>           raise RuntimeError(f"LLM returned invalid JSON for schema.\nRaw:\n{raw}\nContent:\n{content}\n\nError:\n{e}") from e
E           RuntimeError: LLM returned invalid JSON for schema.
E           Raw:
E           {'model': 'llama3.2', 'created_at': '2026-02-21T01:16:03.4341582Z', 'message': {'role': 'assistant', 'content': '{"bucket":"needs_attention","confidence":0.9,"action":"keep_in_inbox","reason":"direct_request, has_deadline, has_direct_request, looks_like_invite, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline,'}, 'done': True, 'done_reason': 'length', 'total_duration': 6516410400, 'load_duration': 124578700, 'prompt_eval_count': 879, 'prompt_eval_duration': 43610800, 'eval_count': 256, 'eval_duration': 1939125300}
E           Content:
E           {"bucket":"needs_attention","confidence":0.9,"action":"keep_in_inbox","reason":"direct_request, has_deadline, has_direct_request, looks_like_invite, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline, has_direct_request, has_deadline,
E
E           Error:
E           1 validation error for TriageResult
E             Invalid JSON: EOF while parsing a string at line 1 column 1080 [type=json_invalid, input_value='{"bucket":"needs_attenti..._request, has_deadline,', input_type=str]
E               For further information visit https://errors.pydantic.dev/2.12/v/json_invalid

mailtriage.py:308: RuntimeError
=================================================================== short test summary info ====================================================================
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[calendar_or_travel_01.json] - AssertionError: [calendar_or_travel_01.json] auto_move_ok failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[calendar_or_travel_02.json] - AssertionError: [calendar_or_travel_02.json] auto_move_ok failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[calendar_or_travel_03.json] - AssertionError: [calendar_or_travel_03.json] action failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[spam_or_scams_02.json] - AssertionError: [spam_or_scams_02.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[spam_or_scams_03.json] - AssertionError: [spam_or_scams_03.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[uncertain_01.json] - RuntimeError: LLM returned invalid JSON for schema.
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[uncertain_02.json] - AssertionError: [uncertain_02.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[uncertain_03.json] - AssertionError: [uncertain_03.json] bucket_in failed
FAILED tests/test_ollama_integration_smoke.py::test_ollama_smoke_structured_json - RuntimeError: LLM returned invalid JSON for schema.
9 failed, 19 passed, 11 deselected in 42.59s