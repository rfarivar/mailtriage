(.venv) C:\Users\rezaf\dev\mailtriage>set OLLAMA_MODEL=deepseek-r1:8b

(.venv) C:\Users\rezaf\dev\mailtriage>python -m pytest -m integration -q
F.FFFFF.....FFFF.FFFF.F.FFFF                                                                                                                              [100%]
=========================================================================== FAILURES ===========================================================================
_________________________________________________________ test_corpus_case[calendar_or_travel_01.json] _________________________________________________________

self = <mailtriage.OllamaClient object at 0x000001C73F2734D0>
email_obj = {'body_excerpt': 'You have been invited to an event.\n\n        Title: Weekly Capstone Sprint Review\n        When: Mo...r decline.', 'cc': '', 'date': 'Fri, 20 Feb 2026 10:00:00 -0800', 'from': 'UIUC Calendar <calendar@illinois.edu>', ...}

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
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

mailtriage.py:306: ValidationError

The above exception was the direct cause of the following exception:

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/calendar_or_travel_01.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000001C73F2734D0>

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

self = <mailtriage.OllamaClient object at 0x000001C73F2734D0>
email_obj = {'body_excerpt': 'You have been invited to an event.\n\n        Title: Weekly Capstone Sprint Review\n        When: Mo...r decline.', 'cc': '', 'date': 'Fri, 20 Feb 2026 10:00:00 -0800', 'from': 'UIUC Calendar <calendar@illinois.edu>', ...}

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
E           {'model': 'deepseek-r1:8b', 'created_at': '2026-02-21T01:01:11.9175479Z', 'message': {'role': 'assistant', 'content': '{\n  "bucket": "calendar_or_travel",\n  "confidence": 100,\n  "action": "keep_in_inbox",\n  "reason": "The email is an invitation to a calendar event with an RSVP request.",\n  "auto_move_ok": false,\n  "signals": [\n    "looks_like_invite",\n    "has_direct_request"\n  ]\n}'}, 'done': True, 'done_reason': 'stop', 'total_duration': 3965105200, 'load_duration': 2713402100, 'prompt_eval_count': 964, 'prompt_eval_duration': 270471500, 'eval_count': 77, 'eval_duration': 768400100}
E           Content:
E           {
E             "bucket": "calendar_or_travel",
E             "confidence": 100,
E             "action": "keep_in_inbox",
E             "reason": "The email is an invitation to a calendar event with an RSVP request.",
E             "auto_move_ok": false,
E             "signals": [
E               "looks_like_invite",
E               "has_direct_request"
E             ]
E           }
E
E           Error:
E           1 validation error for TriageResult
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

mailtriage.py:308: RuntimeError
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
_________________________________________________________ test_corpus_case[calendar_or_travel_03.json] _________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/calendar_or_travel_03.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000001C73F2734D0>

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

rule = 'auto_move_ok', expected = True, actual = False

    def fail(rule: str, expected: Any, actual: Any) -> None:
>       raise AssertionError(
            f"[{case_name}] {rule} failed\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n\n"
            f"DEBUG:\n{json.dumps(debug, indent=2, ensure_ascii=False)}"
        )
E       AssertionError: [calendar_or_travel_03.json] auto_move_ok failed
E         expected: True
E         actual:   False
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
E           "confidence": 0.95,
E           "action": "keep_in_inbox",
E           "auto_move_ok": false,
E           "reason": "Booking confirmation with travel details and modification instructions.",
E           "signals": [
E             "looks_like_travel",
E             "looks_like_transaction"
E           ]
E         },
E         "perf": {
E           "prompt_tokens": 953,
E           "gen_tokens": 73,
E           "total_ms": 1065.2703
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
  "confidence": 0.95,
  "action": "keep_in_inbox",
  "reason": "Booking confirmation with travel details and modification instructions.",
  "signals": [
    "looks_like_travel",
    "looks_like_transaction"
  ],
  "auto_move_ok": false
}
PERF: {
  "prompt_tokens": 953,
  "gen_tokens": 73,
  "prompt_ms": 95.6421,
  "gen_ms": 682.4615,
  "total_ms": 1065.2703
}
_______________________________________________________________ test_corpus_case[human_01.json] ________________________________________________________________

self = <mailtriage.OllamaClient object at 0x000001C73F2734D0>
email_obj = {'body_excerpt': 'Hi Reza, can you review the attached draft and send comments by tomorrow noon?', 'date': 'Fri, 20 Feb 2026 09:10:00 -0800', 'from': 'Eric <eric@illinois.edu>', 'message_id': '<good-5678@illinois.edu>', ...}

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
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

mailtriage.py:306: ValidationError

The above exception was the direct cause of the following exception:

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/human_01.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000001C73F2734D0>

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

self = <mailtriage.OllamaClient object at 0x000001C73F2734D0>
email_obj = {'body_excerpt': 'Hi Reza, can you review the attached draft and send comments by tomorrow noon?', 'date': 'Fri, 20 Feb 2026 09:10:00 -0800', 'from': 'Eric <eric@illinois.edu>', 'message_id': '<good-5678@illinois.edu>', ...}

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
E           {'model': 'deepseek-r1:8b', 'created_at': '2026-02-21T01:01:15.4196312Z', 'message': {'role': 'assistant', 'content': '{\n  "bucket": "needs_attention",\n  "confidence": 100,\n  "action": "keep_in_inbox",\n  "reason": "The email contains a direct request for Reza to review a draft and respond by a specific deadline.",\n  "auto_move_ok": false,\n  "signals": [\n    "has_direct_request",\n    "has_deadline"\n  ]\n}'}, 'done': True, 'done_reason': 'stop', 'total_duration': 1144963300, 'load_duration': 110512900, 'prompt_eval_count': 893, 'prompt_eval_duration': 74115600, 'eval_count': 82, 'eval_duration': 778276100}
E           Content:
E           {
E             "bucket": "needs_attention",
E             "confidence": 100,
E             "action": "keep_in_inbox",
E             "reason": "The email contains a direct request for Reza to review a draft and respond by a specific deadline.",
E             "auto_move_ok": false,
E             "signals": [
E               "has_direct_request",
E               "has_deadline"
E             ]
E           }
E
E           Error:
E           1 validation error for TriageResult
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

mailtriage.py:308: RuntimeError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: human_01.json ---
EMAIL:
{
  "from": "Eric <eric@illinois.edu>",
  "to": "Reza <reza@illinois.edu>",
  "subject": "Quick review on the draft by tomorrow?",
  "date": "Fri, 20 Feb 2026 09:10:00 -0800",
  "message_id": "<good-5678@illinois.edu>",
  "body_excerpt": "Hi Reza, can you review the attached draft and send comments by tomorrow noon?"
}
EXPECT:
{
  "bucket_in": [
    "needs_attention"
  ],
  "action": "keep_in_inbox",
  "min_confidence": 0.7,
  "auto_move_ok": false
}
__________________________________________________________ test_corpus_case[needs_attention_01.json] ___________________________________________________________

self = <mailtriage.OllamaClient object at 0x000001C73F2734D0>
email_obj = {'body_excerpt': "Hi Reza,\n\n        I pushed a small update to the grading rubric and wanted a quick sanity check.\n...,\n        Dana", 'cc': '', 'date': 'Fri, 20 Feb 2026 10:00:00 -0800', 'from': 'Dana Kim <dana.kim@illinois.edu>', ...}

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
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

mailtriage.py:306: ValidationError

The above exception was the direct cause of the following exception:

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/needs_attention_01.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000001C73F2734D0>

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

self = <mailtriage.OllamaClient object at 0x000001C73F2734D0>
email_obj = {'body_excerpt': "Hi Reza,\n\n        I pushed a small update to the grading rubric and wanted a quick sanity check.\n...,\n        Dana", 'cc': '', 'date': 'Fri, 20 Feb 2026 10:00:00 -0800', 'from': 'Dana Kim <dana.kim@illinois.edu>', ...}

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
E           {'model': 'deepseek-r1:8b', 'created_at': '2026-02-21T01:01:16.7159613Z', 'message': {'role': 'assistant', 'content': '{\n  "bucket": "needs_attention",\n  "confidence": 100,\n  "action": "keep_in_inbox",\n  "reason": "The email requests a review with a deadline, indicating human-to-human interaction and a need for response.",\n  "auto_move_ok": false,\n  "signals": [\n    "has_direct_request",\n    "has_deadline"\n  ]\n}'}, 'done': True, 'done_reason': 'stop', 'total_duration': 1267933000, 'load_duration': 111611200, 'prompt_eval_count': 974, 'prompt_eval_duration': 99247300, 'eval_count': 82, 'eval_duration': 796043300}
E           Content:
E           {
E             "bucket": "needs_attention",
E             "confidence": 100,
E             "action": "keep_in_inbox",
E             "reason": "The email requests a review with a deadline, indicating human-to-human interaction and a need for response.",
E             "auto_move_ok": false,
E             "signals": [
E               "has_direct_request",
E               "has_deadline"
E             ]
E           }
E
E           Error:
E           1 validation error for TriageResult
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

mailtriage.py:308: RuntimeError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: needs_attention_01.json ---
EMAIL:
{
  "from": "Dana Kim <dana.kim@illinois.edu>",
  "to": "Reza <reza@illinois.edu>",
  "cc": "",
  "subject": "Can you review the rubric updates today?",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<can-you-revi-3k40vb5t@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "Hi Reza,\n\n        I pushed a small update to the grading rubric and wanted a quick sanity check.\n        Could you skim the changes and reply with approval (or edits) by 4pm today?\n        It's time-sensitive because the TAs start grading this evening.\n\n        Thanks,\n        Dana"
}
EXPECT:
{
  "bucket_in": [
    "needs_attention"
  ],
  "min_confidence": 0.7,
  "auto_move_ok": false,
  "action": "keep_in_inbox"
}
__________________________________________________________ test_corpus_case[needs_attention_02.json] ___________________________________________________________

self = <mailtriage.OllamaClient object at 0x000001C73F2734D0>
email_obj = {'body_excerpt': 'Hey Reza — quick decision needed.\n\n        Between Vendor A and Vendor B, which should we sign for...s fine.\n\n        -Alex', 'cc': '', 'date': 'Fri, 20 Feb 2026 10:00:00 -0800', 'from': 'Alex <alex@company.com>', ...}

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
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

mailtriage.py:306: ValidationError

The above exception was the direct cause of the following exception:

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/needs_attention_02.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000001C73F2734D0>

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

self = <mailtriage.OllamaClient object at 0x000001C73F2734D0>
email_obj = {'body_excerpt': 'Hey Reza — quick decision needed.\n\n        Between Vendor A and Vendor B, which should we sign for...s fine.\n\n        -Alex', 'cc': '', 'date': 'Fri, 20 Feb 2026 10:00:00 -0800', 'from': 'Alex <alex@company.com>', ...}

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
E           {'model': 'deepseek-r1:8b', 'created_at': '2026-02-21T01:01:17.807319Z', 'message': {'role': 'assistant', 'content': '{\n  "bucket": "needs_attention",\n  "confidence": 100,\n  "action": "keep_in_inbox",\n  "reason": "The email explicitly requests a decision from the recipient (Reza) with a deadline (by end of day).",\n  "auto_move_ok": false\n}'}, 'done': True, 'done_reason': 'stop', 'total_duration': 1074983900, 'load_duration': 124444300, 'prompt_eval_count': 951, 'prompt_eval_duration': 97981100, 'eval_count': 66, 'eval_duration': 631740800}
E           Content:
E           {
E             "bucket": "needs_attention",
E             "confidence": 100,
E             "action": "keep_in_inbox",
E             "reason": "The email explicitly requests a decision from the recipient (Reza) with a deadline (by end of day).",
E             "auto_move_ok": false
E           }
E
E           Error:
E           1 validation error for TriageResult
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

mailtriage.py:308: RuntimeError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: needs_attention_02.json ---
EMAIL:
{
  "from": "Alex <alex@company.com>",
  "to": "Reza <reza@company.com>",
  "cc": "",
  "subject": "Decision needed: vendor choice for next week",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<decision-nee-qmh6uc8t@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "Hey Reza — quick decision needed.\n\n        Between Vendor A and Vendor B, which should we sign for next week’s pilot?\n        I need your call by end of day so procurement can start the paperwork.\n        Two bullet points is fine.\n\n        -Alex"
}
EXPECT:
{
  "bucket_in": [
    "needs_attention"
  ],
  "min_confidence": 0.7,
  "auto_move_ok": false,
  "action": "keep_in_inbox"
}
__________________________________________________________ test_corpus_case[needs_attention_03.json] ___________________________________________________________

self = <mailtriage.OllamaClient object at 0x000001C73F2734D0>
email_obj = {'body_excerpt': 'Hi Professor Farivar,\n\n        We want to confirm whether our Milestone 3 can focus on the prototy...c': '', 'date': 'Fri, 20 Feb 2026 10:00:00 -0800', 'from': 'Student Team Delta <teamdelta@students.illinois.edu>', ...}

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
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

mailtriage.py:306: ValidationError

The above exception was the direct cause of the following exception:

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/needs_attention_03.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000001C73F2734D0>

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

self = <mailtriage.OllamaClient object at 0x000001C73F2734D0>
email_obj = {'body_excerpt': 'Hi Professor Farivar,\n\n        We want to confirm whether our Milestone 3 can focus on the prototy...c': '', 'date': 'Fri, 20 Feb 2026 10:00:00 -0800', 'from': 'Student Team Delta <teamdelta@students.illinois.edu>', ...}

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
E           {'model': 'deepseek-r1:8b', 'created_at': '2026-02-21T01:01:18.9821958Z', 'message': {'role': 'assistant', 'content': '{\n  "bucket": "needs_attention",\n  "confidence": 100,\n  "action": "keep_in_inbox",\n  "reason": "The email is a direct request for confirmation regarding a project milestone, which requires human intervention to respond.",\n  "auto_move_ok": false,\n  "signals": [\n    "has_direct_request"\n  ]\n}'}, 'done': True, 'done_reason': 'stop', 'total_duration': 1153768900, 'load_duration': 113450600, 'prompt_eval_count': 975, 'prompt_eval_duration': 99225100, 'eval_count': 76, 'eval_duration': 737007100}
E           Content:
E           {
E             "bucket": "needs_attention",
E             "confidence": 100,
E             "action": "keep_in_inbox",
E             "reason": "The email is a direct request for confirmation regarding a project milestone, which requires human intervention to respond.",
E             "auto_move_ok": false,
E             "signals": [
E               "has_direct_request"
E             ]
E           }
E
E           Error:
E           1 validation error for TriageResult
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

mailtriage.py:308: RuntimeError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: needs_attention_03.json ---
EMAIL:
{
  "from": "Student Team Delta <teamdelta@students.illinois.edu>",
  "to": "Reza <reza@illinois.edu>",
  "cc": "",
  "subject": "Question about milestone scope (need confirmation)",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<question-abo-tv0tx1r2@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "Hi Professor Farivar,\n\n        We want to confirm whether our Milestone 3 can focus on the prototype plus one measurement set,\n        or if you expect the full 4–5 measurement sets by then.\n        Could you confirm the expectation so we plan the sprint correctly?\n\n        Best,\n        Team Delta"
}
EXPECT:
{
  "bucket_in": [
    "needs_attention"
  ],
  "min_confidence": 0.7,
  "auto_move_ok": false,
  "action": "keep_in_inbox"
}
___________________________________________________________ test_corpus_case[security_alert_01.json] ___________________________________________________________

self = <mailtriage.OllamaClient object at 0x000001C73F2734D0>
email_obj = {'body_excerpt': 'We noticed a new sign-in to your Google Account.\n\n        Device: Windows (Chrome)\n        Locati....', 'cc': '', 'date': 'Fri, 20 Feb 2026 10:00:00 -0800', 'from': 'Google Security <no-reply@accounts.google.com>', ...}

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
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

mailtriage.py:306: ValidationError

The above exception was the direct cause of the following exception:

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/security_alert_01.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000001C73F2734D0>

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

self = <mailtriage.OllamaClient object at 0x000001C73F2734D0>
email_obj = {'body_excerpt': 'We noticed a new sign-in to your Google Account.\n\n        Device: Windows (Chrome)\n        Locati....', 'cc': '', 'date': 'Fri, 20 Feb 2026 10:00:00 -0800', 'from': 'Google Security <no-reply@accounts.google.com>', ...}

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
E           {'model': 'deepseek-r1:8b', 'created_at': '2026-02-21T01:01:25.7447792Z', 'message': {'role': 'assistant', 'content': '{\n  "bucket": "security_alert",\n  "confidence": 100,\n  "action": "keep_in_inbox",\n  "reason": "This email is a security alert from Google Security, indicating a new sign-in attempt. It matches the bucket definition with phrases like \'If this wasn\'t you...\' and contains a direct request to review account settings.",\n  "auto_move_ok": false,\n  "signals": [\n    "looks_like_security_alert",\n    "has_direct_request"\n  ]\n}'}, 'done': True, 'done_reason': 'stop', 'total_duration': 1392289300, 'load_duration': 100445500, 'prompt_eval_count': 968, 'prompt_eval_duration': 96532500, 'eval_count': 105, 'eval_duration': 981088700}
E           Content:
E           {
E             "bucket": "security_alert",
E             "confidence": 100,
E             "action": "keep_in_inbox",
E             "reason": "This email is a security alert from Google Security, indicating a new sign-in attempt. It matches the bucket definition with phrases like 'If this wasn't you...' and contains a direct request to review account settings.",
E             "auto_move_ok": false,
E             "signals": [
E               "looks_like_security_alert",
E               "has_direct_request"
E             ]
E           }
E
E           Error:
E           1 validation error for TriageResult
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

mailtriage.py:308: RuntimeError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: security_alert_01.json ---
EMAIL:
{
  "from": "Google Security <no-reply@accounts.google.com>",
  "to": "Reza <reza@gmail.com>",
  "cc": "",
  "subject": "Security alert: new sign-in on your Google Account",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<security-ale-flukomgh@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "We noticed a new sign-in to your Google Account.\n\n        Device: Windows (Chrome)\n        Location: San Jose, CA\n        Time: Feb 20, 9:12 AM\n\n        If this was you, you can ignore this email.\n        If not, review your security activity in your account settings."
}
EXPECT:
{
  "bucket_in": [
    "security_alert"
  ],
  "min_confidence": 0.8,
  "auto_move_ok": false,
  "action": "keep_in_inbox"
}
___________________________________________________________ test_corpus_case[security_alert_02.json] ___________________________________________________________

self = <mailtriage.OllamaClient object at 0x000001C73F2734D0>
email_obj = {'body_excerpt': 'A password reset was requested for your Microsoft account.\n\n        If you requested this, follow ...i, 20 Feb 2026 10:00:00 -0800', 'from': 'Microsoft Account Team <account-security-noreply@account.microsoft.com>', ...}

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
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

mailtriage.py:306: ValidationError

The above exception was the direct cause of the following exception:

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/security_alert_02.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000001C73F2734D0>

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

self = <mailtriage.OllamaClient object at 0x000001C73F2734D0>
email_obj = {'body_excerpt': 'A password reset was requested for your Microsoft account.\n\n        If you requested this, follow ...i, 20 Feb 2026 10:00:00 -0800', 'from': 'Microsoft Account Team <account-security-noreply@account.microsoft.com>', ...}

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
E           {'model': 'deepseek-r1:8b', 'created_at': '2026-02-21T01:01:27.108814Z', 'message': {'role': 'assistant', 'content': '{\n  "bucket": "security_alert",\n  "confidence": 100,\n  "action": "keep_in_inbox",\n  "reason": "This email is a security alert from Microsoft regarding a password reset request. It matches the bucket definition for security_alert as it contains account security instructions and a prompt to secure the account if not requested by the user.",\n  "auto_move_ok": false,\n  "signals": [\n    "looks_like_security_alert"\n  ]\n}'}, 'done': True, 'done_reason': 'stop', 'total_duration': 1332561900, 'load_duration': 105539900, 'prompt_eval_count': 946, 'prompt_eval_duration': 93988200, 'eval_count': 99, 'eval_duration': 929190000}
E           Content:
E           {
E             "bucket": "security_alert",
E             "confidence": 100,
E             "action": "keep_in_inbox",
E             "reason": "This email is a security alert from Microsoft regarding a password reset request. It matches the bucket definition for security_alert as it contains account security instructions and a prompt to secure the account if not requested by the user.",
E             "auto_move_ok": false,
E             "signals": [
E               "looks_like_security_alert"
E             ]
E           }
E
E           Error:
E           1 validation error for TriageResult
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

mailtriage.py:308: RuntimeError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: security_alert_02.json ---
EMAIL:
{
  "from": "Microsoft Account Team <account-security-noreply@account.microsoft.com>",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "Password reset requested",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<password-res-boane99d@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "A password reset was requested for your Microsoft account.\n\n        If you requested this, follow the instructions in your account security page.\n        If you did not request this, secure your account immediately by changing your password and enabling MFA."
}
EXPECT:
{
  "bucket_in": [
    "security_alert"
  ],
  "min_confidence": 0.8,
  "auto_move_ok": false,
  "action": "keep_in_inbox"
}
___________________________________________________________ test_corpus_case[security_alert_03.json] ___________________________________________________________

self = <mailtriage.OllamaClient object at 0x000001C73F2734D0>
email_obj = {'body_excerpt': 'Your one-time code is: 493201\n\n        This code expires in 10 minutes.\n        If you did not re...your card.', 'cc': '', 'date': 'Fri, 20 Feb 2026 10:00:00 -0800', 'from': 'Bank Alerts <alerts@bank-example.com>', ...}

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
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

mailtriage.py:306: ValidationError

The above exception was the direct cause of the following exception:

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/security_alert_03.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000001C73F2734D0>

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

self = <mailtriage.OllamaClient object at 0x000001C73F2734D0>
email_obj = {'body_excerpt': 'Your one-time code is: 493201\n\n        This code expires in 10 minutes.\n        If you did not re...your card.', 'cc': '', 'date': 'Fri, 20 Feb 2026 10:00:00 -0800', 'from': 'Bank Alerts <alerts@bank-example.com>', ...}

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
E           {'model': 'deepseek-r1:8b', 'created_at': '2026-02-21T01:01:28.4527521Z', 'message': {'role': 'assistant', 'content': '{\n  "bucket": "security_alert",\n  "confidence": 100,\n  "action": "keep_in_inbox",\n  "reason": "This email is a two-factor authentication code request, which is a common security alert. It contains an OTP code and mentions expiration, aligning with the security_alert bucket.",\n  "auto_move_ok": false,\n  "signals": [\n    "has_otp_code",\n    "looks_like_security_alert"\n  ]\n}'}, 'done': True, 'done_reason': 'stop', 'total_duration': 1327885400, 'load_duration': 111490900, 'prompt_eval_count': 938, 'prompt_eval_duration': 91969700, 'eval_count': 98, 'eval_duration': 910351700}
E           Content:
E           {
E             "bucket": "security_alert",
E             "confidence": 100,
E             "action": "keep_in_inbox",
E             "reason": "This email is a two-factor authentication code request, which is a common security alert. It contains an OTP code and mentions expiration, aligning with the security_alert bucket.",
E             "auto_move_ok": false,
E             "signals": [
E               "has_otp_code",
E               "looks_like_security_alert"
E             ]
E           }
E
E           Error:
E           1 validation error for TriageResult
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

mailtriage.py:308: RuntimeError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: security_alert_03.json ---
EMAIL:
{
  "from": "Bank Alerts <alerts@bank-example.com>",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "Two-factor authentication code",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<two-factor-a-c7kjparb@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "Your one-time code is: 493201\n\n        This code expires in 10 minutes.\n        If you did not request this code, contact support via the official website or phone number on your card."
}
EXPECT:
{
  "bucket_in": [
    "security_alert"
  ],
  "min_confidence": 0.8,
  "auto_move_ok": false,
  "action": "keep_in_inbox"
}
________________________________________________________ test_corpus_case[social_notification_01.json] _________________________________________________________

self = <mailtriage.OllamaClient object at 0x000001C73F2734D0>
email_obj = {'body_excerpt': 'You have new messages waiting in your LinkedIn inbox.\n\n        Open LinkedIn to read them.\n      ...y time.', 'cc': '', 'date': 'Fri, 20 Feb 2026 10:00:00 -0800', 'from': 'LinkedIn <messages-noreply@linkedin.com>', ...}

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
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

mailtriage.py:306: ValidationError

The above exception was the direct cause of the following exception:

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/social_notification_01.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000001C73F2734D0>

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

self = <mailtriage.OllamaClient object at 0x000001C73F2734D0>
email_obj = {'body_excerpt': 'You have new messages waiting in your LinkedIn inbox.\n\n        Open LinkedIn to read them.\n      ...y time.', 'cc': '', 'date': 'Fri, 20 Feb 2026 10:00:00 -0800', 'from': 'LinkedIn <messages-noreply@linkedin.com>', ...}

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
E           {'model': 'deepseek-r1:8b', 'created_at': '2026-02-21T01:01:29.322311Z', 'message': {'role': 'assistant', 'content': '{\n  "bucket": "social_notification",\n  "confidence": 100,\n  "action": "move_to_folder",\n  "reason": "Social notification from LinkedIn about new messages.",\n  "auto_move_ok": true\n}'}, 'done': True, 'done_reason': 'stop', 'total_duration': 835237400, 'load_duration': 92996600, 'prompt_eval_count': 947, 'prompt_eval_duration': 92591700, 'eval_count': 50, 'eval_duration': 454576500}
E           Content:
E           {
E             "bucket": "social_notification",
E             "confidence": 100,
E             "action": "move_to_folder",
E             "reason": "Social notification from LinkedIn about new messages.",
E             "auto_move_ok": true
E           }
E
E           Error:
E           1 validation error for TriageResult
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

mailtriage.py:308: RuntimeError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: social_notification_01.json ---
EMAIL:
{
  "from": "LinkedIn <messages-noreply@linkedin.com>",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "You have 3 new messages",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<you-have-3-n-89ehj7i1@example.test>",
  "list_id": "<linkedin.notifications.linkedin.com>",
  "list_unsubscribe": "<https://www.linkedin.com/comm/setting/email>",
  "body_excerpt": "You have new messages waiting in your LinkedIn inbox.\n\n        Open LinkedIn to read them.\n        You can change your email notification settings at any time."
}
EXPECT:
{
  "bucket_in": [
    "social_notification"
  ],
  "min_confidence": 0.75,
  "auto_move_ok": true,
  "action": "move_to_folder"
}
________________________________________________________ test_corpus_case[social_notification_03.json] _________________________________________________________

self = <mailtriage.OllamaClient object at 0x000001C73F2734D0>
email_obj = {'body_excerpt': 'You have a new follower.\n\n        @someone is now following you.\n        Adjust notification preferences in your account settings.', 'cc': '', 'date': 'Fri, 20 Feb 2026 10:00:00 -0800', 'from': 'X <notify@x.com>', ...}

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
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

mailtriage.py:306: ValidationError

The above exception was the direct cause of the following exception:

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/social_notification_03.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000001C73F2734D0>

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

self = <mailtriage.OllamaClient object at 0x000001C73F2734D0>
email_obj = {'body_excerpt': 'You have a new follower.\n\n        @someone is now following you.\n        Adjust notification preferences in your account settings.', 'cc': '', 'date': 'Fri, 20 Feb 2026 10:00:00 -0800', 'from': 'X <notify@x.com>', ...}

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
E           {'model': 'deepseek-r1:8b', 'created_at': '2026-02-21T01:01:31.3918952Z', 'message': {'role': 'assistant', 'content': '{\n  "bucket": "social_notification",\n  "confidence": 100,\n  "action": "move_to_folder",\n  "reason": "Social notification from a platform (X) about a new follower, with list unsubscribe header but content is a standard social notification.",\n  "auto_move_ok": true,\n  "signals": [\n    "looks_like_social_notification"\n  ]\n}'}, 'done': True, 'done_reason': 'stop', 'total_duration': 1142425600, 'load_duration': 102223600, 'prompt_eval_count': 929, 'prompt_eval_duration': 85186500, 'eval_count': 81, 'eval_duration': 746758500}
E           Content:
E           {
E             "bucket": "social_notification",
E             "confidence": 100,
E             "action": "move_to_folder",
E             "reason": "Social notification from a platform (X) about a new follower, with list unsubscribe header but content is a standard social notification.",
E             "auto_move_ok": true,
E             "signals": [
E               "looks_like_social_notification"
E             ]
E           }
E
E           Error:
E           1 validation error for TriageResult
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

mailtriage.py:308: RuntimeError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: social_notification_03.json ---
EMAIL:
{
  "from": "X <notify@x.com>",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "New follower: @someone",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<new-follower-ml105n0c@example.test>",
  "list_id": "<x.notifications.x.com>",
  "list_unsubscribe": "<https://x.com/settings/notifications>",
  "body_excerpt": "You have a new follower.\n\n        @someone is now following you.\n        Adjust notification preferences in your account settings."
}
EXPECT:
{
  "bucket_in": [
    "social_notification"
  ],
  "min_confidence": 0.75,
  "auto_move_ok": true,
  "action": "move_to_folder"
}
___________________________________________________________ test_corpus_case[spam_or_scams_01.json] ____________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/spam_or_scams_01.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000001C73F2734D0>

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
E           "reason": "The email claims to be from PayPal Support and warns of account limitation with a direct link to verify identity, matching the security_alert bucket criteria.",
E           "signals": []
E         },
E         "perf": {
E           "prompt_tokens": 944,
E           "gen_tokens": 72,
E           "total_ms": 1060.69
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
  "reason": "The email claims to be from PayPal Support and warns of account limitation with a direct link to verify identity, matching the security_alert bucket criteria.",
  "signals": [],
  "auto_move_ok": false
}
PERF: {
  "prompt_tokens": 944,
  "gen_tokens": 72,
  "prompt_ms": 94.5363,
  "gen_ms": 671.5102,
  "total_ms": 1060.69
}
___________________________________________________________ test_corpus_case[spam_or_scams_02.json] ____________________________________________________________

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/spam_or_scams_02.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000001C73F2734D0>

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
E           "reason": "The email claims the mailbox has exceeded storage and requires immediate re-validation to avoid deactivation, which is a common tactic in account takeover scams.",
E           "signals": [
E             "has_direct_request",
E             "account_threat",
E             "suspicious_link"
E           ]
E         },
E         "perf": {
E           "prompt_tokens": 944,
E           "gen_tokens": 98,
E           "total_ms": 1316.6117
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
  "reason": "The email claims the mailbox has exceeded storage and requires immediate re-validation to avoid deactivation, which is a common tactic in account takeover scams.",
  "signals": [
    "has_direct_request",
    "account_threat",
    "suspicious_link"
  ],
  "auto_move_ok": false
}
PERF: {
  "prompt_tokens": 944,
  "gen_tokens": 98,
  "prompt_ms": 94.5688,
  "gen_ms": 913.2859,
  "total_ms": 1316.6117
}
___________________________________________________________ test_corpus_case[spam_or_scams_03.json] ____________________________________________________________

self = <mailtriage.OllamaClient object at 0x000001C73F2734D0>
email_obj = {'body_excerpt': 'We attempted delivery but require a small redelivery fee.\n\n        Pay the fee here to schedule re...d.', 'cc': '', 'date': 'Fri, 20 Feb 2026 10:00:00 -0800', 'from': 'Delivery Notice <noreply@shipments-track.net>', ...}

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
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

mailtriage.py:306: ValidationError

The above exception was the direct cause of the following exception:

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/spam_or_scams_03.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000001C73F2734D0>

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

self = <mailtriage.OllamaClient object at 0x000001C73F2734D0>
email_obj = {'body_excerpt': 'We attempted delivery but require a small redelivery fee.\n\n        Pay the fee here to schedule re...d.', 'cc': '', 'date': 'Fri, 20 Feb 2026 10:00:00 -0800', 'from': 'Delivery Notice <noreply@shipments-track.net>', ...}

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
E           {'model': 'deepseek-r1:8b', 'created_at': '2026-02-21T01:01:34.8340138Z', 'message': {'role': 'assistant', 'content': '{\n  "bucket": "needs_attention",\n  "confidence": 100,\n  "action": "keep_in_inbox",\n  "reason": "The email requests payment for a package delivery fee and threatens return if unpaid, indicating a direct request to take action.",\n  "auto_move_ok": false\n}'}, 'done': True, 'done_reason': 'stop', 'total_duration': 990979500, 'load_duration': 105551000, 'prompt_eval_count': 947, 'prompt_eval_duration': 96157700, 'eval_count': 66, 'eval_duration': 607190400}
E           Content:
E           {
E             "bucket": "needs_attention",
E             "confidence": 100,
E             "action": "keep_in_inbox",
E             "reason": "The email requests payment for a package delivery fee and threatens return if unpaid, indicating a direct request to take action.",
E             "auto_move_ok": false
E           }
E
E           Error:
E           1 validation error for TriageResult
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

mailtriage.py:308: RuntimeError
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
___________________________________________________________ test_corpus_case[transactional_02.json] ____________________________________________________________

self = <mailtriage.OllamaClient object at 0x000001C73F2734D0>
email_obj = {'body_excerpt': 'Payment received.\n\n        Amount: $86.42\n        Confirmation: CWU-2398841\n        Service peri...ment.', 'cc': '', 'date': 'Fri, 20 Feb 2026 10:00:00 -0800', 'from': 'City Water Utility <billing@citywater.gov>', ...}

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
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

mailtriage.py:306: ValidationError

The above exception was the direct cause of the following exception:

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/transactional_02.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000001C73F2734D0>

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

self = <mailtriage.OllamaClient object at 0x000001C73F2734D0>
email_obj = {'body_excerpt': 'Payment received.\n\n        Amount: $86.42\n        Confirmation: CWU-2398841\n        Service peri...ment.', 'cc': '', 'date': 'Fri, 20 Feb 2026 10:00:00 -0800', 'from': 'City Water Utility <billing@citywater.gov>', ...}

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
E           {'model': 'deepseek-r1:8b', 'created_at': '2026-02-21T01:01:36.9489294Z', 'message': {'role': 'assistant', 'content': '{\n  "bucket": "transactional",\n  "confidence": 100,\n  "action": "move_to_folder",\n  "reason": "This email is a payment confirmation with a transactional amount and details, matching the transactional bucket criteria.",\n  "auto_move_ok": true\n}'}, 'done': True, 'done_reason': 'stop', 'total_duration': 970475400, 'load_duration': 93949500, 'prompt_eval_count': 945, 'prompt_eval_duration': 96940700, 'eval_count': 63, 'eval_duration': 581546300}
E           Content:
E           {
E             "bucket": "transactional",
E             "confidence": 100,
E             "action": "move_to_folder",
E             "reason": "This email is a payment confirmation with a transactional amount and details, matching the transactional bucket criteria.",
E             "auto_move_ok": true
E           }
E
E           Error:
E           1 validation error for TriageResult
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

mailtriage.py:308: RuntimeError
--------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------

--- CASE: transactional_02.json ---
EMAIL:
{
  "from": "City Water Utility <billing@citywater.gov>",
  "to": "Reza <reza@example.com>",
  "cc": "",
  "subject": "Receipt: Payment received for water bill",
  "date": "Fri, 20 Feb 2026 10:00:00 -0800",
  "message_id": "<receipt:-pay-pvyfljhk@example.test>",
  "list_id": "",
  "list_unsubscribe": "",
  "body_excerpt": "Payment received.\n\n        Amount: $86.42\n        Confirmation: CWU-2398841\n        Service period: Jan 15 – Feb 14\n\n        Thank you for your payment."
}
EXPECT:
{
  "bucket_in": [
    "transactional"
  ],
  "min_confidence": 0.75,
  "auto_move_ok": true,
  "action": "move_to_folder"
}
_____________________________________________________________ test_corpus_case[uncertain_01.json] ______________________________________________________________

self = <mailtriage.OllamaClient object at 0x000001C73F2734D0>
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
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

mailtriage.py:306: ValidationError

The above exception was the direct cause of the following exception:

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/uncertain_01.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000001C73F2734D0>

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

self = <mailtriage.OllamaClient object at 0x000001C73F2734D0>
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
E           {'model': 'deepseek-r1:8b', 'created_at': '2026-02-21T01:01:39.0088863Z', 'message': {'role': 'assistant', 'content': '{\n  "bucket": "needs_attention",\n  "confidence": 100,\n  "action": "keep_in_inbox",\n  "reason": "The email contains a direct request for confirmation of details.",\n  "auto_move_ok": false\n}'}, 'done': True, 'done_reason': 'stop', 'total_duration': 864560300, 'load_duration': 110557400, 'prompt_eval_count': 904, 'prompt_eval_duration': 80137400, 'eval_count': 54, 'eval_duration': 498011500}
E           Content:
E           {
E             "bucket": "needs_attention",
E             "confidence": 100,
E             "action": "keep_in_inbox",
E             "reason": "The email contains a direct request for confirmation of details.",
E             "auto_move_ok": false
E           }
E
E           Error:
E           1 validation error for TriageResult
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

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
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000001C73F2734D0>

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
E           "reason": "The email is from a service and indicates automated notification, with _features showing 'looks_like_social_notification' is true. No list headers or other signals indicate it's promotional or security-related.",
E           "signals": []
E         },
E         "perf": {
E           "prompt_tokens": 892,
E           "gen_tokens": 81,
E           "total_ms": 1129.9305
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
  "reason": "The email is from a service and indicates automated notification, with _features showing 'looks_like_social_notification' is true. No list headers or other signals indicate it's promotional or security-related.",
  "signals": [],
  "auto_move_ok": true
}
PERF: {
  "prompt_tokens": 892,
  "gen_tokens": 81,
  "prompt_ms": 74.37,
  "gen_ms": 751.735,
  "total_ms": 1129.9305
}
_____________________________________________________________ test_corpus_case[uncertain_03.json] ______________________________________________________________

self = <mailtriage.OllamaClient object at 0x000001C73F2734D0>
email_obj = {'body_excerpt': 'Your ticket has been updated. Please see the portal for details.', 'cc': '', 'date': 'Fri, 20 Feb 2026 10:00:00 -0800', 'from': 'Support <support@vendor.example>', ...}

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
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

mailtriage.py:306: ValidationError

The above exception was the direct cause of the following exception:

case_path = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example/uncertain_03.json')
corpus_dir = WindowsPath('C:/Users/rezaf/dev/mailtriage/tests/corpus_example'), ollama_client = <mailtriage.OllamaClient object at 0x000001C73F2734D0>

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

self = <mailtriage.OllamaClient object at 0x000001C73F2734D0>
email_obj = {'body_excerpt': 'Your ticket has been updated. Please see the portal for details.', 'cc': '', 'date': 'Fri, 20 Feb 2026 10:00:00 -0800', 'from': 'Support <support@vendor.example>', ...}

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
E           {'model': 'deepseek-r1:8b', 'created_at': '2026-02-21T01:01:41.2557969Z', 'message': {'role': 'assistant', 'content': '{\n  "bucket": "needs_attention",\n  "confidence": 100,\n  "action": "keep_in_inbox",\n  "reason": "The email contains a direct request to take action (see the portal for details) and lacks list headers, fitting the \'needs_attention\' bucket.",\n  "auto_move_ok": false\n}'}, 'done': True, 'done_reason': 'stop', 'total_duration': 1046993300, 'load_duration': 108412800, 'prompt_eval_count': 899, 'prompt_eval_duration': 74169500, 'eval_count': 72, 'eval_duration': 664862900}
E           Content:
E           {
E             "bucket": "needs_attention",
E             "confidence": 100,
E             "action": "keep_in_inbox",
E             "reason": "The email contains a direct request to take action (see the portal for details) and lacks list headers, fitting the 'needs_attention' bucket.",
E             "auto_move_ok": false
E           }
E
E           Error:
E           1 validation error for TriageResult
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

mailtriage.py:308: RuntimeError
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
______________________________________________________________ test_ollama_smoke_structured_json _______________________________________________________________

self = <mailtriage.OllamaClient object at 0x000001C73FD2BC50>
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
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

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

self = <mailtriage.OllamaClient object at 0x000001C73FD2BC50>
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
E           {'model': 'deepseek-r1:8b', 'created_at': '2026-02-21T01:01:42.3841139Z', 'message': {'role': 'assistant', 'content': '{\n  "bucket": "needs_attention",\n  "confidence": 100,\n  "action": "keep_in_inbox",\n  "reason": "The email contains a direct request for a response (\\"can you reply when you can?\\")",\n  "auto_move_ok": false,\n  "signals": [\n    "has_direct_request"\n  ]\n}'}, 'done': True, 'done_reason': 'stop', 'total_duration': 1074503900, 'load_duration': 94519600, 'prompt_eval_count': 868, 'prompt_eval_duration': 67612400, 'eval_count': 76, 'eval_duration': 700205800}
E           Content:
E           {
E             "bucket": "needs_attention",
E             "confidence": 100,
E             "action": "keep_in_inbox",
E             "reason": "The email contains a direct request for a response (\"can you reply when you can?\")",
E             "auto_move_ok": false,
E             "signals": [
E               "has_direct_request"
E             ]
E           }
E
E           Error:
E           1 validation error for TriageResult
E           confidence
E             Input should be less than or equal to 1 [type=less_than_equal, input_value=100, input_type=int]
E               For further information visit https://errors.pydantic.dev/2.12/v/less_than_equal

mailtriage.py:308: RuntimeError
=================================================================== short test summary info ====================================================================
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[calendar_or_travel_01.json] - RuntimeError: LLM returned invalid JSON for schema.
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[calendar_or_travel_03.json] - AssertionError: [calendar_or_travel_03.json] auto_move_ok failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[human_01.json] - RuntimeError: LLM returned invalid JSON for schema.
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[needs_attention_01.json] - RuntimeError: LLM returned invalid JSON for schema.
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[needs_attention_02.json] - RuntimeError: LLM returned invalid JSON for schema.
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[needs_attention_03.json] - RuntimeError: LLM returned invalid JSON for schema.
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[security_alert_01.json] - RuntimeError: LLM returned invalid JSON for schema.
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[security_alert_02.json] - RuntimeError: LLM returned invalid JSON for schema.
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[security_alert_03.json] - RuntimeError: LLM returned invalid JSON for schema.
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[social_notification_01.json] - RuntimeError: LLM returned invalid JSON for schema.
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[social_notification_03.json] - RuntimeError: LLM returned invalid JSON for schema.
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[spam_or_scams_01.json] - AssertionError: [spam_or_scams_01.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[spam_or_scams_02.json] - AssertionError: [spam_or_scams_02.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[spam_or_scams_03.json] - RuntimeError: LLM returned invalid JSON for schema.
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[transactional_02.json] - RuntimeError: LLM returned invalid JSON for schema.
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[uncertain_01.json] - RuntimeError: LLM returned invalid JSON for schema.
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[uncertain_02.json] - AssertionError: [uncertain_02.json] bucket_in failed
FAILED tests/test_ollama_integration_corpus.py::test_corpus_case[uncertain_03.json] - RuntimeError: LLM returned invalid JSON for schema.
FAILED tests/test_ollama_integration_smoke.py::test_ollama_smoke_structured_json - RuntimeError: LLM returned invalid JSON for schema.
19 failed, 9 passed, 11 deselected in 35.04s
