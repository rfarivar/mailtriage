import mailtriage as mt

def test_norm_addr_extracts_email():
    assert mt.norm_addr('John Doe <John.Doe@Example.com>') == "john.doe@example.com"
    assert mt.norm_addr("SOMEONE@EXAMPLE.COM") == "someone@example.com"

def test_domain_of():
    assert mt.domain_of("A <a@uiuc.edu>") == "uiuc.edu"
    assert mt.domain_of("no-at-symbol") == ""

def test_strip_quoted_history_on_wrote():
    text = "Hi there\n\nOn Tue, Bob wrote:\n> older stuff\n"
    assert mt.strip_quoted_history(text) == "Hi there"

def test_truncate_for_llm_short_text_unchanged():
    #s = "hello world today is a good day to test"
    s = "hello world"
    assert mt.truncate_for_llm(s, head_chars=10, tail_chars=5) == "hello world"

def test_truncate_for_llm_long_text_snips():
    s = "A" * 5000
    out = mt.truncate_for_llm(s, head_chars=1000, tail_chars=200)
    assert "[...snip...]" in out
    assert len(out) < len(s)

def test_should_never_move():
    assert mt.should_never_move(
        sender_email="Boss <boss@company.com>",
        never_domains=["uiuc.edu"],
        never_senders=["boss@company.com"],
    ) is True

    assert mt.should_never_move(
        sender_email="Student <x@uiuc.edu>",
        never_domains=["uiuc.edu"],
        never_senders=[],
    ) is True

    assert mt.should_never_move(
        sender_email="Promo <deals@store.com>",
        never_domains=["uiuc.edu"],
        never_senders=[],
    ) is False

def test_decide_destination():
    folder_map = {"newsletter_or_marketing": "AI/Promotions"}
    assert mt.decide_destination("newsletter_or_marketing", folder_map) == "AI/Promotions"
    assert mt.decide_destination("needs_attention", folder_map) is None