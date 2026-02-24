from email.message import EmailMessage
import mailtriage as mt

def test_extract_body_plain_text():
    msg = EmailMessage()
    msg["From"] = "a@b.com"
    msg["To"] = "c@d.com"
    msg["Subject"] = "Hello"
    msg.set_content("Line1\n\nLine2\n")
    assert mt.extract_body(msg) == "Line1\n\nLine2"

def test_extract_body_html_fallback():
    msg = EmailMessage()
    msg["Subject"] = "HTML"
    msg.add_alternative("<html><body><h1>Hi</h1><p>There</p></body></html>", subtype="html")
    body = mt.extract_body(msg)
    assert "Hi" in body
    assert "There" in body

def test_extract_body_multipart_prefers_plain():
    msg = EmailMessage()
    msg["Subject"] = "Multipart"
    msg.set_content("PLAIN PART\n\nOn Tue, Bob wrote:\n> old\n")
    msg.add_alternative("<p>HTML PART</p>", subtype="html")
    body = mt.extract_body(msg)
    # should prefer plain and strip quoted history
    assert body == "PLAIN PART"