import argparse
import base64
import email
import ssl
from email.parser import BytesParser
from email.policy import default
from pathlib import Path

import imaplib
import yaml
from dotenv import load_dotenv

load_dotenv()


def xoauth2_b64(username: str, access_token: str) -> str:
    """
    XOAUTH2 string is:
      base64("user=<user>^Aauth=Bearer <token>^A^A")
    where ^A is Ctrl+A (\x01).  (Gmail + Microsoft docs)
    """
    s = f"user={username}\x01auth=Bearer {access_token}\x01\x01"
    return base64.b64encode(s.encode("utf-8")).decode("ascii")


def connect_imap(host: str, port: int, use_ssl: bool):
    if use_ssl:
        ctx = ssl.create_default_context()
        return imaplib.IMAP4_SSL(host, port, ssl_context=ctx)
    # STARTTLS mode if you ever need it:
    imap = imaplib.IMAP4(host, port)
    imap.starttls(ssl.create_default_context())
    return imap


def fetch_headers(imap, msg_id: bytes) -> dict:
    typ, data = imap.fetch(msg_id, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE MESSAGE-ID)])")
    if typ != "OK" or not data or not data[0]:
        return {"from": "", "subject": "", "date": "", "message_id": ""}
    raw = data[0][1]
    msg = BytesParser(policy=default).parsebytes(raw)
    return {
        "from": msg.get("From", ""),
        "subject": msg.get("Subject", ""),
        "date": msg.get("Date", ""),
        "message_id": msg.get("Message-ID", ""),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--account", required=True)
    ap.add_argument("--limit", type=int, default=10, help="how many messages to show")
    ap.add_argument("--unseen", action="store_true", help="only show UNSEEN messages")
    args = ap.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    acct = cfg["accounts"][args.account]

    host = acct["host"]
    port = int(acct.get("port", 993))
    use_ssl = bool(acct.get("ssl", True))
    mailbox = acct.get("mailbox", "INBOX")
    username = acct["username"]

    auth = acct.get("auth", {}) or {}
    method = auth.get("method", "password")

    imap = connect_imap(host, port, use_ssl)

    try:
        if method == "password":
            import os
            env_name = auth.get("password_env")
            if not env_name:
                raise SystemExit("config missing auth.password_env")
            password = os.environ.get(env_name)
            if not password:
                raise SystemExit(f"env var {env_name} is not set")
            imap.login(username, password)

        elif method == "xoauth2":
            import os
            env_name = auth.get("access_token_env")
            if not env_name:
                raise SystemExit("config missing auth.access_token_env")
            token = os.environ.get(env_name)
            if not token:
                raise SystemExit(f"env var {env_name} is not set")

            # Send AUTHENTICATE XOAUTH2 <base64(...)>
            b64 = xoauth2_b64(username, token)
            typ, data = imap.authenticate("XOAUTH2", lambda _: b64)
            if typ != "OK":
                raise RuntimeError(f"XOAUTH2 auth failed: {typ} {data}")

        else:
            raise SystemExit(f"Unknown auth method: {method}")

        typ, _ = imap.select(mailbox)
        if typ != "OK":
            raise RuntimeError(f"Failed to select mailbox {mailbox}")

        criteria = "UNSEEN" if args.unseen else "ALL"
        typ, data = imap.search(None, criteria)
        if typ != "OK":
            raise RuntimeError(f"SEARCH failed: {typ} {data}")

        ids = data[0].split()
        ids = ids[-args.limit:]  # newest N

        print(f"Connected OK: {args.account} ({username}) {host}:{port} mailbox={mailbox}")
        print(f"Showing {len(ids)} messages ({criteria})\n")

        for msg_id in reversed(ids):
            h = fetch_headers(imap, msg_id)
            print(f"- {h['date']}")
            print(f"  From: {h['from']}")
            print(f"  Subj: {h['subject']}")
            print(f"  ID:   {h['message_id']}\n")

    finally:
        try:
            imap.logout()
        except Exception:
            pass


if __name__ == "__main__":
    main()