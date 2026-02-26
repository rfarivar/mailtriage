import argparse
import base64
import datetime as dt
import email
import json
import re
import ssl
import sys
from dataclasses import dataclass
from email.parser import BytesParser
from email.policy import default
from typing import Any, Dict, List, Optional, Tuple

import imaplib
import requests
import yaml
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, ValidationError

from pathlib import Path
import os
import time
from urllib.parse import urlparse
from tqdm import tqdm

from dotenv import load_dotenv

from m365_oauth import get_m365_access_token


# -----------------------------
# Models / schema for the LLM
# -----------------------------

BUCKETS = [
    "needs_attention",
    "transactional",
    "security_alert",
    "calendar_or_travel",
    "newsletter_or_marketing",
    "social_notification",
    "spam_or_scams",
    "uncertain",
]

ACTIONS = [
    "keep_in_inbox",
    "move_to_folder",
    "label_only",
    "quarantine",
    "do_nothing",
]


class LLMClassification(BaseModel):
    """
    What we expect from the LLM. Keep this minimal and stable across models.
    """
    bucket: str = Field(..., description="Classification bucket", pattern="^(" + "|".join(BUCKETS) + ")$")
    # allow 0..100 to tolerate models that output percentage confidence (e.g., 85 or 100)
    confidence: float = Field(..., ge=0.0, le=100.0)
    reason: str
    signals: List[str] = Field(default_factory=list)

    model_config = {"extra": "ignore"}  # ignore any extra fields some models emit


# TRIAGE_SCHEMA = TriageResult.model_json_schema()
# We use LLMClassification as the schema for the LLM output, and then convert to TriageResult in code.
# This allows the LLM to be flexible in what it outputs (e.g., confidence as 0..100 or 0..1, and ignore auto_move_ok which is a policy decision we make in code), while still enforcing the core required fields and types.
# Why: we now enforce a simpler JSON schema at the API boundary, which is where DeepSeek/Qwen are most likely to break

# JSON schema (what we send to Ollama as `format`)
TRIAGE_SCHEMA = LLMClassification.model_json_schema()

class TriageResult(BaseModel):
    bucket: str = Field(..., description="Classification bucket", pattern="^(" + "|".join(BUCKETS) + ")$")
    confidence: float = Field(..., ge=0.0, le=1.0)
    action: str = Field(..., description="Suggested action", pattern="^(" + "|".join(ACTIONS) + ")$")
    reason: str
    signals: List[str] = Field(default_factory=list)
    auto_move_ok: bool = Field(..., description="Whether it's safe to auto-move without user review")


# -----------------------------
# Email parsing helpers
# -----------------------------

RE_QUOTED_SPLITS = [
    r"\nOn .* wrote:\n",
    r"\nFrom: .*",
    r"\n-----Original Message-----\n",
    r"\n______________________________\n",
]


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # remove scripts/styles
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text("\n")
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def strip_quoted_history(text: str) -> str:
    # Heuristic: cut at common reply separators
    for pat in RE_QUOTED_SPLITS:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            return text[: m.start()].strip()
    return text.strip()


def truncate_for_llm(text: str, head_chars: int = 4000, tail_chars: int = 1000) -> str:
    text = text.strip()
    if len(text) <= head_chars + tail_chars + 50:
        return text
    head = text[:head_chars].rstrip()
    tail = text[-tail_chars:].lstrip()
    return f"{head}\n\n[...snip...]\n\n{tail}"


def extract_body(msg: email.message.EmailMessage) -> str:
    # Prefer text/plain; fallback to text/html
    plain_parts = []
    html_parts = []

    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            disp = part.get_content_disposition()
            if disp == "attachment":
                continue
            if ctype == "text/plain":
                try:
                    plain_parts.append(part.get_content().strip())
                except Exception:
                    pass
            elif ctype == "text/html":
                try:
                    html_parts.append(part.get_content())
                except Exception:
                    pass
    else:
        ctype = msg.get_content_type()
        try:
            if ctype == "text/plain":
                plain_parts.append(msg.get_content().strip())
            elif ctype == "text/html":
                html_parts.append(msg.get_content())
        except Exception:
            pass

    if plain_parts:
        body = "\n\n".join([p for p in plain_parts if p])
        return strip_quoted_history(body)

    if html_parts:
        body = "\n\n".join([html_to_text(h) for h in html_parts if h])
        return strip_quoted_history(body)

    return ""


def norm_addr(addr: str) -> str:
    # Pull email out of "Name <email@x>"
    m = re.search(r"<([^>]+)>", addr or "")
    if m:
        return m.group(1).strip().lower()
    return (addr or "").strip().lower()


def domain_of(addr: str) -> str:
    addr = norm_addr(addr)
    if "@" in addr:
        return addr.split("@", 1)[1]
    return ""

OTP_RE = re.compile(r"\b\d{6}\b")  # simple 6-digit code
MONEY_RE = re.compile(r"(\$|usd|amount:)", re.IGNORECASE)
DISCOUNT_RE = re.compile(r"(%\s*off|\b\d{1,2}%\b|\bsale\b|\bdeal\b|\bflash sale\b|\blimited time\b)", re.IGNORECASE)

URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)

def sanitize_urls(
    text: str,
    max_url_len: int = 200,
    max_domain_len: int = 80,
    max_path_len: int = 80,
    path_segments: int = 3,
) -> str:
    """
    Replace long URLs with a compact placeholder that preserves domain + a richer path signal.
    Output format uses commas for readability and easier parsing.

    Example:
      [URL, domain=click.example.com, path=/f/abc/def, query_len=842, total_len=1024]
    """

    def summarize_path(path: str) -> str:
        if not path:
            return "/"

        # Split into segments, ignoring empty
        segs = [s for s in path.split("/") if s]
        if not segs:
            return "/"

        # Keep first N segments
        kept = segs[:path_segments]

        # If the last segment is different and short, keep it too (helps with /verify, /reset, /confirm, etc.)
        last = segs[-1]
        if last not in kept and len(last) <= 24 and len(segs) > path_segments:
            kept.append("…")
            kept.append(last)

        out = "/" + "/".join(kept)

        # Trim if still too long
        if len(out) > max_path_len:
            out = out[: max_path_len - 1] + "…"
        return out

    def repl(m: re.Match) -> str:
        url = m.group(0)
        if len(url) <= max_url_len:
            return url

        try:
            p = urlparse(url)
            domain = (p.netloc or "")[:max_domain_len]
            path = summarize_path(p.path or "/")
            qlen = len(p.query or "")
            return f"[URL, domain={domain}, path={path}, query_len={qlen}, total_len={len(url)}]"
        except Exception:
            return f"[URL, total_len={len(url)}]"

    return URL_RE.sub(repl, text)

def url_stats(text: str) -> Dict[str, Any]:
    urls = URL_RE.findall(text or "")
    if not urls:
        return {"url_count": 0, "max_url_len": 0, "max_url_query_len": 0}

    max_len = 0
    max_qlen = 0
    for u in urls:
        max_len = max(max_len, len(u))
        try:
            p = urlparse(u)
            max_qlen = max(max_qlen, len(p.query or ""))
        except Exception:
            pass
    return {"url_count": len(urls), "max_url_len": max_len, "max_url_query_len": max_qlen}

def compute_features(email_obj: Dict[str, Any]) -> Dict[str, Any]:
    subject = (email_obj.get("subject") or "")
    body = (email_obj.get("body_excerpt") or "")
    list_id = (email_obj.get("list_id") or "")
    list_unsub = (email_obj.get("list_unsubscribe") or "")
    frm = (email_obj.get("from") or "")

    text = f"{subject}\n{body}"

    features = {
        "from_email": norm_addr(frm),
        "from_domain": domain_of(frm),
        "has_list_id": bool(list_id.strip()),
        "has_list_unsubscribe": bool(list_unsub.strip()),
        "has_link": bool(URL_RE.search(text)),
        "url_count": int(email_obj.get("url_count", 0)),
        "max_url_len": int(email_obj.get("max_url_len", 0)),
        "max_url_query_len": int(email_obj.get("max_url_query_len", 0)),
        "has_very_long_url": int(email_obj.get("max_url_len", 0)) >= 500,
        "has_otp_code": bool(OTP_RE.search(text)),
        "has_money_amount": bool(MONEY_RE.search(text)),
        "has_discount_language": bool(DISCOUNT_RE.search(text)),
        "looks_like_invite": bool(re.search(r"\binvitation\b|\baccept\b|\bdecline\b|\brsvp\b|\bcalendar\b", text, re.IGNORECASE)),
        "looks_like_travel": bool(re.search(r"\bflight\b|\bitinerary\b|\bcheck-?in\b|\bcheck-?out\b|\bbooking\b|\breservation\b", text, re.IGNORECASE)),
        "looks_like_transaction": bool(re.search(r"\breceipt\b|\border\b|\bshipped\b|\bpayment received\b|\binvoice\b|\bconfirmation\b", text, re.IGNORECASE)),
        "looks_like_security_alert": bool(re.search(r"\bsecurity alert\b|\bnew sign-?in\b|\bpassword reset\b|\btwo-?factor\b|\bone-time code\b|\bverification code\b", text, re.IGNORECASE)),
        "looks_like_social_notification": bool(re.search(r"\bnew follower\b|\bnew message\b|\bcomment\b|\bmentioned\b|\binvite you to\b|\bGitHub\b|\bLinkedIn\b", text, re.IGNORECASE)),
        "has_direct_request": bool(re.search(r"\bcan you\b|\bcould you\b|\bneed your\b|\bconfirm\b|\breview\b|\breply\b", text, re.IGNORECASE)),
        "has_deadline": bool(re.search(r"\bby\b.*\b(today|tomorrow|noon|pm|am|\d{1,2}:\d{2})\b|\bend of day\b|\bEOD\b", text, re.IGNORECASE)),
    }
    return features

def normalize_confidence(c: float) -> float:
    """
    Normalize confidence into [0, 1]. Tolerate models that output 0..100.
    """
    if c > 1.0 and c <= 100.0:
        return c / 100.0
    return max(0.0, min(1.0, c))


def policy_action_and_automove(bucket: str, features: Dict[str, Any]) -> Tuple[str, bool]:
    """
    Deterministic policy. This is the single source of truth for action + auto_move_ok.
    """
    if bucket in ("needs_attention", "security_alert"):
        return "keep_in_inbox", False

    if bucket == "calendar_or_travel":
        # Calendar invites: keep in inbox. Travel confirmations/itineraries: safe to move.
        if features.get("looks_like_travel") and not features.get("looks_like_invite"):
            return "move_to_folder", True
        return "keep_in_inbox", False

    if bucket in ("transactional", "social_notification", "newsletter_or_marketing"):
        return "move_to_folder", True

    if bucket == "spam_or_scams":
        return "quarantine", True

    # uncertain
    return "do_nothing", False


# -----------------------------
# Ollama client
# -----------------------------

class OllamaClient:
    def __init__(self, base_url: str, model: str, timeout_s: int = 120):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_s = timeout_s

    def triage_email(self, email_obj: Dict[str, Any], system_prompt: str, context_length_tokens: int = 4096) -> Tuple[TriageResult, Dict[str, Any]]:
        """
        Returns (parsed_result, raw_ollama_response)
        """

        email_for_llm = dict(email_obj)
        email_for_llm["_features"] = compute_features(email_obj)

        user_prompt = (
            "Classify this email. Return ONLY JSON that matches the provided schema.\n\n"
            f"Email:\n{json.dumps(email_for_llm, ensure_ascii=False, indent=2)}"
        )

        payload = {
            "model": self.model,
            "stream": False,
            "format": TRIAGE_SCHEMA,  # enforce schema
            "think": False,  # <-- KEY: disable thinking trace for thinking-capable models
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "options": {
                "temperature": 0.0,
                "num_ctx": context_length_tokens,      # <- context window; for llama 3.2:3b can go as high as 16K, but for 
                                      # llama-3.1:8b and qwen3:8b and deepseek-r1:8b has to remain under 8K or spills into CPU
                "num_predict": 512,   # <- cap output tokens (optional but good practice)
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
            llm_out = LLMClassification.model_validate_json(content)
        except ValidationError as e:
            raise RuntimeError(
                f"LLM returned invalid JSON for schema.\nRaw:\n{raw}\nContent:\n{content}\n\nError:\n{e}"
            ) from e

        conf = normalize_confidence(llm_out.confidence)

        features = email_for_llm["_features"]
        action, auto_move_ok = policy_action_and_automove(llm_out.bucket, features)

        final = TriageResult(
            bucket=llm_out.bucket,
            confidence=conf,
            action=action,
            reason=llm_out.reason,
            signals=llm_out.signals,
            auto_move_ok=auto_move_ok,
        )

        return final, raw


# -----------------------------
# IMAP connector + mover
# -----------------------------

def xoauth2_b64(username: str, access_token: str) -> str:
    """
    XOAUTH2 string is:
      base64("user=<user>^Aauth=Bearer <token>^A^A")
    where ^A is Ctrl+A (\x01).
    """
    s = f"user={username}\x01auth=Bearer {access_token}\x01\x01"
    return base64.b64encode(s.encode("utf-8")).decode("ascii")

def xoauth2_sasl_bytes(username: str, access_token: str) -> bytes:
    # NOTE: this is NOT base64. imaplib.authenticate will base64-encode it.
    s = f"user={username}\x01auth=Bearer {access_token}\x01\x01"
    return s.encode("utf-8")

@dataclass
class ImapAccount:
    host: str
    port: int
    auth_method: str = "password"  # "password" or "xoauth2"
    username: Optinal[str] = None
    username_env: Optional[str] = None
    password_env: Optional[str] = None
    access_token_env: Optional[str] = None
    mailbox: str = "INBOX"

    def get_username(self) -> str:
        # Prefer explicit username (non-secret) from config.yaml
        if self.username:
            return self.username
        # Fallback to username_env if provided
        if not self.username_env:
            raise RuntimeError("No username configured (set accounts.<name>.username or auth.username_env)")
        username = os.getenv(self.username_env)
        if not username:
            raise RuntimeError(f"Missing env var for IMAP username: {self.username_env}")
        return username

    def get_password(self) -> str:
        if not self.password_env:
            raise RuntimeError("password_env not configured for app password auth")
        pw = os.getenv(self.password_env)
        if not pw:
            raise RuntimeError(f"Missing env var for IMAP password: {self.password_env}")
        return pw

    def get_access_token(self) -> str:
        """Get OAuth2 access token from env or via M365 device flow."""
        if not self.access_token_env:
            raise RuntimeError("access_token_env not configured for xoauth2 auth")
        
        # Check if token is already in environment (user set it manually)
        token = os.getenv(self.access_token_env)
        if token:
            return token
        
        # Otherwise, use M365 device flow to get a fresh token
        from m365_oauth import get_m365_access_token
        scopes = ["https://outlook.office.com/IMAP.AccessAsUser.All"]
        token = get_m365_access_token(scopes)
        
        # Cache it in the environment for this session
        os.environ[self.access_token_env] = token
        return token


class ImapClient:
    def __init__(self, acct: ImapAccount):
        self.acct = acct
        self.conn: Optional[imaplib.IMAP4_SSL] = None

    def __enter__(self):
        ctx = ssl.create_default_context()
        self.conn = imaplib.IMAP4_SSL(self.acct.host, self.acct.port, ssl_context=ctx)
        
        # Authenticate based on method
        if self.acct.auth_method == "password":
            self.conn.login(self.acct.get_username(), self.acct.get_password())
        elif self.acct.auth_method == "xoauth2":
            token = self.acct.get_access_token()          
            sasl = xoauth2_sasl_bytes(self.acct.get_username(), token)
            typ, data = self.conn.authenticate("XOAUTH2", lambda _: sasl)
            if typ != "OK":
                raise RuntimeError(f"XOAUTH2 auth failed: {typ} {data}")            
        else:
            raise RuntimeError(f"Unknown auth method: {self.acct.auth_method}")
        
        typ, _ = self.conn.select(self.acct.mailbox)
        if typ != "OK":
            raise RuntimeError(f"Failed to select mailbox: {self.acct.mailbox}")
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.conn is not None:
            try:
                self.conn.close()
            except Exception:
                pass
            try:
                self.conn.logout()
            except Exception:
                pass

    def search_unseen(self, limit: int = 30) -> List[bytes]:
        # Returns message sequence numbers (not UIDs). Simpler MVP.
        assert self.conn
        typ, data = self.conn.search(None, "UNSEEN")
        if typ != "OK":
            return []
        ids = data[0].split()
        return ids[-limit:]  # newest N
    
    def search(self, criterion: str, limit: int) -> List[bytes]:
        assert self.conn
        typ, data = self.conn.search(None, criterion)
        if typ != "OK":
            return []
        ids = data[0].split()
        return ids[-limit:]  # newest N

    def uid_search(self, criterion: str, limit: int) -> List[bytes]:
        assert self.conn
        typ, data = self.conn.uid("SEARCH", None, criterion)
        if typ != "OK":
            return []
        uids = data[0].split()
        return uids[-limit:]

    def fetch_rfc822(self, msg_id: bytes) -> bytes:
        assert self.conn
        typ, data = self.conn.fetch(msg_id, "(RFC822)")
        if typ != "OK":
            raise RuntimeError(f"Failed to fetch message {msg_id!r}")
        return data[0][1]
    
    def uid_fetch_rfc822(self, uid: bytes) -> bytes:
        assert self.conn
        typ, data = self.conn.uid("FETCH", uid, "(RFC822)")
        if typ != "OK" or not data or not data[0]:
            raise RuntimeError(f"Failed to UID FETCH {uid!r}")
        return data[0][1]

    def ensure_mailbox(self, mailbox: str) -> None:
        """
        Ensure mailbox exists on the server.
        - CREATE may return NO if it already exists (that's fine).
        - SUBSCRIBE helps some servers/clients display the folder.
        """
        assert self.conn

        # Try CREATE; ignore "already exists" style failures.
        typ, data = self.conn.create(mailbox)
        if typ != "OK":
            # Many servers return "NO [ALREADYEXISTS]" or similar.
            msg = ""
            if data and isinstance(data, list) and data[0]:
                try:
                    msg = data[0].decode(errors="ignore") if isinstance(data[0], (bytes, bytearray)) else str(data[0])
                except Exception:
                    msg = str(data[0])

            # If it looks like "already exists", ignore; otherwise raise.
            if "exists" not in msg.lower() and "already" not in msg.lower():
                raise RuntimeError(f"CREATE mailbox failed for {mailbox}: {typ} {data}")

        # Best-effort subscribe (OK if server doesn't support it)
        try:
            self.conn.subscribe(mailbox)
        except Exception:
            pass

    def move_message(self, msg_id: bytes, dest_mailbox: str) -> None:
        """
        Generic IMAP move:
          COPY to dest
          mark Deleted in source
          EXPUNGE
        """
        assert self.conn
        self.ensure_mailbox(dest_mailbox)
        typ, _ = self.conn.copy(msg_id, dest_mailbox)
        if typ != "OK":
            raise RuntimeError(f"COPY failed to {dest_mailbox} for msg {msg_id!r}")
        self.conn.store(msg_id, "+FLAGS", r"(\Deleted)")
        self.conn.expunge()

    def uid_move_message(self, uid: bytes, dest_mailbox: str) -> None:
        assert self.conn
        self.ensure_mailbox(dest_mailbox)
        typ, _ = self.conn.uid("COPY", uid, dest_mailbox)
        if typ != "OK":
            raise RuntimeError(f"UID COPY failed to {dest_mailbox} for uid {uid!r}")
        typ, _ = self.conn.uid("STORE", uid, "+FLAGS", r"(\Deleted)")
        if typ != "OK":
            raise RuntimeError(f"UID STORE failed for uid {uid!r}")
        self.conn.expunge()


# -----------------------------
# Policy + main loop
# -----------------------------

def should_never_move(sender_email: str, never_domains: List[str], never_senders: List[str]) -> bool:
    sender_email = norm_addr(sender_email)
    if sender_email in [s.lower() for s in never_senders]:
        return True
    dom = domain_of(sender_email)
    if dom and dom.lower() in [d.lower() for d in never_domains]:
        return True
    return False


def decide_destination(bucket: str, folder_map: Dict[str, str]) -> Optional[str]:
    return folder_map.get(bucket)


def build_email_object(msg: email.message.EmailMessage, body_excerpt: str, body_length: int, url_stats_obj: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "from": msg.get("From", ""),
        "to": msg.get("To", ""),
        "cc": msg.get("Cc", ""),
        "subject": msg.get("Subject", ""),
        "date": msg.get("Date", ""),
        "message_id": msg.get("Message-ID", ""),
        "list_id": msg.get("List-ID", ""),
        "list_unsubscribe": msg.get("List-Unsubscribe", ""),
        "body_excerpt": body_excerpt,
        "body_length": body_length,
        "sanitized_body_length": len(body_excerpt),
        "body_truncated": body_length > len(body_excerpt),
        "body_truncated_ratio": len(body_excerpt) / body_length if body_length > 0 else 0,
        "url_count": url_stats_obj.get("url_count", 0),
        "max_url_len": url_stats_obj.get("max_url_len", 0),
        "max_url_query_len": url_stats_obj.get("max_url_query_len", 0),
    }

# Helpers for report-mode JSNOL logging and summary stats. 
# Not essential for triage functionality, but useful for monitoring and improving the system.
# ======================================================================
def ensure_dir(path: str) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p

def write_jsonl_line(fp, obj: Dict[str, Any]) -> None:
    fp.write(json.dumps(obj, ensure_ascii=False) + "\n")

# ======================================================================

def bucket_dest_group(bucket: str, folder_map: Dict[str, str]) -> str:
    """
    Group key for agreement when --agree group is used.

    We use the destination folder (AI/Promotions, AI/Social, etc.) as the group key,
    since that's what the user actually cares about.
    Buckets that don't move fall back to a stable label.
    """
    dest = folder_map.get(bucket)
    if dest:
        return dest

    # Non-movable buckets: keep them distinct by bucket name to avoid over-agreement.
    return f"INBOX::{bucket}"

def agree(
    primary: TriageResult,
    secondary: Optional[TriageResult],
    mode: str,
    folder_map: Dict[str, str],
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Returns (is_verified, forced_bucket, forced_dest).

    forced_bucket/forced_dest are used for special overrides like spam quarantine consensus.
    """
    if secondary is None:
        return False, None, None

    # --- special spam override ---
    # If either model says spam_or_scams and the other says a low-risk movable bucket,
    # treat it as verified and route to spam_or_scams destination (AI/Quarantine).
    movable_ok = {"newsletter_or_marketing", "social_notification", "transactional"}
    if (
        (primary.bucket == "spam_or_scams" and secondary.bucket in movable_ok)
        or (secondary.bucket == "spam_or_scams" and primary.bucket in movable_ok)
    ):
      
        forced_bucket = "spam_or_scams"
        forced_dest = folder_map.get("spam_or_scams")
        # If spam folder isn't configured, we can't safely act on this override.
        if forced_dest:
            return True, forced_bucket, forced_dest
        return False, None, None

    # --- normal agreement ---
    if mode == "bucket":
        return (primary.bucket == secondary.bucket), None, None

    # mode == "group": compare destination intent
    g1 = bucket_dest_group(primary.bucket, folder_map)
    g2 = bucket_dest_group(secondary.bucket, folder_map)
    return (g1 == g2), None, None

def verify_reason(it, args, auto_thr, spam_thr, folder_map):
    # only meaningful in two-pass mode
    p = it["primary"]
    s = it["secondary"]

    movable_ok = {"newsletter_or_marketing", "social_notification", "transactional"}
    if (
        (p.bucket == "spam_or_scams" and s and s.bucket in movable_ok)
        or (s and s.bucket == "spam_or_scams" and p.bucket in movable_ok)
    ):
        if folder_map.get("spam_or_scams"):
            return "spam_override->quarantine"
        
    # Not shortlisted => we never attempted secondary
    if s is None:
        # distinguish between "not shortlisted" vs "secondary error"
        if it.get("secondary_raw") is None and args.two_pass:
            # We can detect "attempted but failed" by a flag; easiest: set it when catching exception
            if it.get("secondary_error"):
                return "secondary_error"
        return "not_shortlisted"

    # Agreement checks
    if args.agree == "bucket":
        if p.bucket != s.bucket:
            return f"bucket_mismatch({p.bucket}->{s.bucket})"
    else:
        g1 = bucket_dest_group(p.bucket, folder_map)
        g2 = bucket_dest_group(s.bucket, folder_map)
        if g1 != g2:
            return f"group_mismatch({g1}->{g2})"
        
    # Confidence checks (final move thresholds)
    # (report mode uses move thresholds to define "verified", so show which one failed)
    if p.bucket == "spam_or_scams":
        if p.confidence < spam_thr:
            return f"p_conf<{spam_thr:.2f}"
        if s.confidence < spam_thr:
            return f"s_conf<{spam_thr:.2f}"
    else:
        if p.confidence < auto_thr:
            return f"p_conf<{auto_thr:.2f}"
        if s.confidence < auto_thr:
            return f"s_conf<{auto_thr:.2f}"

    return "verified"




def main():
    load_dotenv()

    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")

    sub = ap.add_subparsers(dest="cmd", required=True)

    primary_triage = sub.add_parser("triage", help="Fetch emails, run LLM triage, and optionally move or report.")
    primary_triage.add_argument("--account", required=True, help="Account key from config.yaml")
    primary_triage.add_argument("--limit", type=int, default=200)
    primary_triage.add_argument("--unseen", action="store_true", help="Only process UNSEEN messages")
    primary_triage.add_argument("--mode", choices=["report", "move"], default="report")
    primary_triage.add_argument("--outdir", default="runs", help="Directory to write JSONL reports/logs")
    primary_triage.add_argument("--dry-run", action="store_true", help="Do not move anything (only relevant for --mode move)")
    primary_triage.add_argument("--two-pass", action="store_true", help="Use primary model on all emails, then verify candidates with a secondary model.")
    primary_triage.add_argument("--primary-model", default=None, help="Primary model name override for triage (single-pass and two-pass). If omitted, uses OLLAMA_MODEL env var or config.yaml.")
    primary_triage.add_argument("--secondary-model", default="qwen3:8b", help="Secondary model name for two-pass verification.")
    primary_triage.add_argument("--shortlist-threshold", type=float, default=0.85, help="Primary confidence threshold to send to secondary model.")
    primary_triage.add_argument("--agree", choices=["bucket", "group"], default="bucket", help="Require agreement on exact bucket or on move-group.")

    fold = sub.add_parser("folders", help="Ensure destination folders exist on the IMAP server.")
    fold.add_argument("--account", required=True, help="Account key from config.yaml")



    args = ap.parse_args()


    cfg = yaml.safe_load(open(args.config, "r", encoding="utf-8"))

    oll = cfg["ollama"]
    policy = cfg["policy"]
    accounts = cfg["accounts"]
    context_length_tokens = int(oll.get("context_length_tokens", 4096))

    if args.cmd == "triage":
        dry_run = bool(getattr(args, "dry_run", False)) or bool(policy.get("dry_run", True))
    else:
        dry_run = True  # irrelevant; folders doesn't move anything

    # dry_run = bool(args.dry_run) or bool(policy.get("dry_run", True))
    auto_thr = float(policy.get("auto_move_threshold", 0.92))
    spam_thr = float(policy.get("spam_quarantine_threshold", 0.97))
    never_domains = policy.get("never_move_from_domains", [])
    never_senders = policy.get("never_move_from_senders", [])
    folder_map = policy.get("folder_map", {})

    # read system from system.md
    system_prompt = ""
    if args.cmd == "triage":
        system_prompt = (Path(__file__).parent / "system.md").read_text(encoding="utf-8").strip()

    acct_cfg = accounts[args.account]
    if acct_cfg.get("type") != "imap":
        raise RuntimeError("This MVP only supports IMAP accounts for now.")

    auth_cfg = acct_cfg.get("auth", {})
    auth_method = auth_cfg.get("method", "password")
    
   
    acct = ImapAccount(
        host=acct_cfg["host"],
        port=int(acct_cfg.get("port", 993)),
        auth_method=auth_method,
        username=acct_cfg.get("username"),                 # <-- take from config
        username_env=auth_cfg.get("username_env"),         # <-- optional, from auth
        password_env=auth_cfg.get("password_env"),
        access_token_env=auth_cfg.get("access_token_env"),
        mailbox=acct_cfg.get("mailbox", "INBOX"),
    )

    primary_model = (
        getattr(args, "primary_model", None)
        or os.getenv("OLLAMA_MODEL")
        or oll["model"]
    )

    ollama = OllamaClient(
        # base_url should be either be read from the os environment variable, or if not present, read from the config file.
        # This allows for flexibility in deployment (e.g., can set env var in production without changing config file, 
        #   and also keeps sensitive info like API keys out of config files).
        base_url=os.getenv("OLLAMA_BASE_URL", oll["base_url"]),
        model=primary_model,
        timeout_s=int(oll.get("timeout_s", 120)),
    )

    secondary_ollama = None
    if args.cmd == "triage" and args.two_pass:
        secondary_ollama = OllamaClient(
            base_url=ollama.base_url,
            model=args.secondary_model,
            timeout_s=ollama.timeout_s,
        )

    print(f"Account={args.account} mailbox={acct.mailbox} dry_run={dry_run}")
    print(f"Primary triage LLM: Ollama={ollama.base_url}, model={ollama.model}, context_length_tokens={context_length_tokens}")
    if secondary_ollama:
        print(f"Secondary triage LLM: Ollama={secondary_ollama.base_url}, model={secondary_ollama.model}, context_length_tokens={context_length_tokens}")
    print()

    run_start = time.perf_counter()

    with ImapClient(acct) as imap:

        if args.cmd == "folders":
            # Create all unique destination folders from folder_map
            dests = sorted({v for v in folder_map.values() if v})
            print(f"Ensuring {len(dests)} folders exist:")
            for d in dests:
                print(f"  - {d}")
                imap.ensure_mailbox(d)
            print("Done.")
            return

        criterion = "UNSEEN" if args.unseen else "ALL"
        uids = imap.uid_search(criterion, limit=args.limit)
        print(f"Found {len(uids)} messages ({criterion}).")
        print()


        n = len(uids)
        idxw = 2 * len(str(n)) + 3   # width of "[N/N]"

        def fmt_idx(i: int, n: int, w: int) -> str:
            return f"[{i}/{n}]".rjust(w)

        if args.mode == "report" and args.two_pass:
            header = (
            f"{'idx':{idxw}}  "
            f"{'p_bucket':24} {'p_cf':>6}  "
            f"{'s_bucket':24} {'s_cf':>6}  "
            f"{'Consensus':24}  "
            f"{'subject'}"
        )
            print(header)
            print("-"*idxw + "  " + "-"*24 +  "   " + "-"*4 + "   " + "-"*24 +  "  " + "-"*4 + "  "  + "-"*24 + "  " + "-"*60 )
        elif args.mode == "report":
            header = (
            f"{'idx':{idxw}}  "
            f"{'bucket':24} {'conf':>6}  "
            f"{'subject'}"
        )
            print(header)
            print("-"*idxw + "  " + "-"*24 +  "   " + "-"*4 + "  "+ "-"*60 )

        run_dir = ensure_dir(args.outdir)
        ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        jsonl_path = run_dir / f"{args.account}_{ts}.jsonl"

        bucket_counts: Dict[str, int] = {b: 0 for b in BUCKETS}
        processed = 0
        errors = 0

        chars_to_llm = context_length_tokens * 4  # rough chars per token estimate; adjust as needed based on the model and typical email content
        chars_to_llm -= len(system_prompt)  # reserve chars for the LLM system prompt
        chars_to_llm -= 512  # reserve chars for the JSON formatting and other prompt content
        head_chars = int(chars_to_llm * 0.8)
        tail_chars = chars_to_llm - head_chars

        with open(jsonl_path, "w", encoding="utf-8") as fp:
            # ----------------------------
            # Phase 0: Fetch emails from the inbox, snapshot into items
            # ----------------------------
            items: List[Dict[str, Any]] = []
            for i, uid in enumerate(tqdm(uids, desc="Phase 0/3: Fetching emails", unit="email"), 1):
                raw_bytes = imap.uid_fetch_rfc822(uid)
                msg = BytesParser(policy=default).parsebytes(raw_bytes)

                body = extract_body(msg)
                body_sanitized = sanitize_urls(body)
                body_excerpt = truncate_for_llm(body_sanitized, head_chars, tail_chars)

                stats = url_stats(body)
                email_obj = build_email_object(msg, body_excerpt, len(body), stats)

                sender = msg.get("From", "")
                subj = (msg.get("Subject", "") or "").strip()
                never_move = should_never_move(sender, never_domains, never_senders)

                items.append({
                    "idx": i,
                    "uid": uid,
                    "sender": sender,
                    "subj": subj,
                    "body_raw_preview": body[:2000],
                    "email_obj": email_obj,
                    "never_move": never_move,
                    "primary": None,
                    "primary_raw": None,
                    "secondary": None,
                    "secondary_raw": None,
                    "secondary_error": None,
                })

            # ----------------------------
            # Phase 1: primary model on all items
            # ----------------------------
            for it in tqdm(items, desc=f"Phase 1/3: Primary triage using {ollama.model}", unit="email"):
                try:
                    tri, raw = ollama.triage_email(
                        it["email_obj"],
                        system_prompt=system_prompt,
                        context_length_tokens=context_length_tokens,
                    )
                    it["primary"] = tri
                    it["primary_raw"] = raw
                except Exception as e:
                    errors += 1
                    write_jsonl_line(fp, {
                        "account": args.account,
                        "imap_uid": it["uid"].decode(errors="ignore"),
                        "date": it["email_obj"].get("date", ""),
                        "from": it["sender"],
                        "to": it["email_obj"].get("to", ""),
                        "subject": it["subj"],
                        "message_id": it["email_obj"].get("message_id", ""),
                        "error": f"primary_llm_error: {e}",
                    })
                    print(f"[{it['idx']}/{len(uids)}] {'LLM error':22} 0.00  {it['subj'][:30]:30}  <== {str(e)[:90]}")
                    continue

            # ----------------------------
            # Phase 2: shortlist + secondary verification (batched)
            # ----------------------------
            shortlist: List[Dict[str, Any]] = []
            if args.two_pass:
                for it in items:
                    p = it["primary"]
                    if p is None:
                        continue
                    dest = decide_destination(p.bucket, folder_map)
                    if it["never_move"]:
                        continue
                    if not p.auto_move_ok:
                        continue
                    if dest is None:
                        continue
                    # broader than final move gate
                    if p.bucket == "spam_or_scams":
                        if p.confidence >= max(spam_thr, args.shortlist_threshold):
                            shortlist.append(it)
                    else:
                        if p.confidence >= args.shortlist_threshold:
                            shortlist.append(it)

                if secondary_ollama is not None and shortlist:
                    for it in tqdm(shortlist, desc=f"Phase 2/3: Secondary triage using {secondary_ollama.model}", unit="email"):
                        try:
                            tri2, raw2 = secondary_ollama.triage_email(
                                it["email_obj"],
                                system_prompt=system_prompt,
                                context_length_tokens=context_length_tokens,
                            )
                            it["secondary"] = tri2
                            it["secondary_raw"] = raw2
                        except Exception as e:
                            # keep secondary None; log if useful
                            write_jsonl_line(fp, {
                                "account": args.account,
                                "imap_uid": it["uid"].decode(errors="ignore"),
                                "subject": it["subj"],
                                "message_id": it["email_obj"].get("message_id", ""),
                                "error": f"secondary_llm_error: {e}",
                                "secondary_error": str(e),
                            })
                            it["secondary"] = None
                            it["secondary_raw"] = None
                            it["secondary_error"] = str(e)

            # ----------------------------
            # Phase 3: decide + log + (optional) move
            # ----------------------------
            for it in items:
                p = it["primary"]
                if p is None:
                    continue

                processed += 1
                bucket_counts[p.bucket] = bucket_counts.get(p.bucket, 0) + 1

                # perf (primary)
                raw_p = it["primary_raw"] or {}
                perf_p = {
                    "prompt_tokens": raw_p.get("prompt_eval_count"),
                    "gen_tokens": raw_p.get("eval_count"),
                    "prompt_ms": (raw_p.get("prompt_eval_duration", 0) or 0) / 1e6,
                    "gen_ms": (raw_p.get("eval_duration", 0) or 0) / 1e6,
                    "total_ms": (raw_p.get("total_duration", 0) or 0) / 1e6,
                    "model": ollama.model,
                }

                # perf (secondary, if present)
                s = it["secondary"]
                raw_s = it["secondary_raw"] or {}
                perf_s = None
                if s is not None:
                    perf_s = {
                        "prompt_tokens": raw_s.get("prompt_eval_count"),
                        "gen_tokens": raw_s.get("eval_count"),
                        "prompt_ms": (raw_s.get("prompt_eval_duration", 0) or 0) / 1e6,
                        "gen_ms": (raw_s.get("eval_duration", 0) or 0) / 1e6,
                        "total_ms": (raw_s.get("total_duration", 0) or 0) / 1e6,
                        "model": secondary_ollama.model if secondary_ollama else "secondary",
                    }

                dest = decide_destination(p.bucket, folder_map)

                forced_bucket = None
                forced_dest = None

                verified = True
                if args.two_pass:
                    verified, forced_bucket, forced_dest = agree(p, s, args.agree, folder_map)

                # If spam override triggered, use the forced destination (AI/Quarantine) and treat bucket as spam_or_scams
                effective_bucket = forced_bucket or p.bucket
                effective_dest = forced_dest or decide_destination(effective_bucket, folder_map)

                # Final move gate: must be verified in two-pass mode
                move_ok = (
                    (args.mode == "move")
                    and (not dry_run)
                    and (not it["never_move"])
                    and (effective_dest is not None)
                    and (p.auto_move_ok or forced_bucket is not None)
                    and verified
                    and (
                        (effective_bucket == "spam_or_scams" and p.confidence >= spam_thr)
                        or (effective_bucket != "spam_or_scams" and p.confidence >= auto_thr)
                    )
                )


                # Write one record per email including both model outputs
                record = {
                    "account": args.account,
                    "imap_uid": it["uid"].decode(errors="ignore"),
                    "date": it["email_obj"].get("date", ""),
                    "from": it["sender"],
                    "to": it["email_obj"].get("to", ""),
                    "subject": it["subj"],
                    "body_length": it["email_obj"].get("body_length", 0),
                    "body_excerpt": it["email_obj"].get("body_excerpt", ""),
                    "raw_body_preview": it["body_raw_preview"],
                    "body_truncated": it["email_obj"].get("body_truncated"),
                    "message_id": it["email_obj"].get("message_id", ""),
                    "primary": {
                        "bucket": p.bucket,
                        "confidence": p.confidence,
                        "action": p.action,
                        "auto_move_ok": p.auto_move_ok,
                        "reason": p.reason,
                        "signals": p.signals,
                        "perf": perf_p,
                        "model": ollama.model,
                        "context_length_tokens": context_length_tokens,
                    },
                    "secondary": None if s is None else {
                        "bucket": s.bucket,
                        "confidence": s.confidence,
                        "action": s.action,
                        "auto_move_ok": s.auto_move_ok,
                        "reason": s.reason,
                        "signals": s.signals,
                        "perf": perf_s,
                        "model": secondary_ollama.model,
                        "context_length_tokens": context_length_tokens,
                    },
                    "bucket_effective": effective_bucket,
                    "dest": effective_dest,
                    "forced_bucket": forced_bucket,
                    "forced_dest": forced_dest,
                    "verified": verified,
                    "dest_primary": dest,
                    "move_ok": move_ok,
                }
                write_jsonl_line(fp, record)

                # Console output
                if args.mode == "report" and args.two_pass:

                    p = it["primary"]
                    s = it["secondary"]
                    pconf = f"{p.confidence:.2f}"
                    sconf = f"{s.confidence:.2f}" if s else "—"
                    sbucket = s.bucket if s else "—"
                    why = verify_reason(it, args, auto_thr, spam_thr, folder_map)

                    # print(f"[{it['idx']:>2}/{len(uids)}] {p.bucket:25} p={pconf:>4}  s={sbucket:25} s={sconf:>4}  <== {why:24}  {it['subj'][:40]}")
                    idx_str = fmt_idx(it["idx"], n, idxw)
                    print(
                        f"{idx_str}  "
                        f"{p.bucket:24} {pconf:>6}  "
                        f"{sbucket:24} {sconf:>6}  "
                        f"{why:24}  "
                        f"{it['subj'][:60]}"
                    )
                elif args.mode == "report":
                    # tag = "verified" if (args.two_pass and verified) else ("unverified" if args.two_pass else "single")
                    # print(f"[{it['idx']}/{len(uids)}] {p.bucket:22} {p.confidence:.2f}  {it['subj'][:30]:30}  <== {tag}")
                    idx_str = fmt_idx(it["idx"], n, idxw)
                    print(f"{idx_str}  {p.bucket:24} {p.confidence:>6.2f}  {it['subj'][:60]}")
                else:
                    print(f"\n[{it['idx']}/{len(uids)}] {it['subj'][:120]}")
                    print(f"  date: {it['email_obj'].get('date', '')}")
                    print(f"  from: {it['sender']}")
                    if args.two_pass:
                        print(f"  primary={p.bucket} -|- primary reason= {p.reason} -|- conf= {p.confidence:.2f}    ")
                        print(f"  secondary={(s.bucket if s else None)} -|- secondary reason= {(s.reason if s else None)} -|- conf= {(s.confidence if s else 0):.2f} ")
                        print(f"  agree={verified} ==> effective bucket: {effective_bucket}")
                    else: 
                        print(f"  bucket={p.bucket} conf={p.confidence:.2f} action={p.action} auto_move_ok={p.auto_move_ok}")
                        print(f"  primary reason: {p.reason}")

                    print(f"  dest: {effective_dest}")

                    if move_ok:
                        print(f"  MOVING -> {effective_dest}")
                        try:
                            imap.uid_move_message(it["uid"], effective_dest)
                        except Exception as e:
                            print(f"  MOVE FAILED: {e}")
                    else:
                        if dry_run:
                            print("  (not moved) dry_run")
                        elif it["never_move"]:
                            print("  (not moved) blocked by never-move allowlist")
                        elif args.two_pass and not verified:
                            print("  (not moved) two-pass did not verify")
                        else:
                            print("  (not moved) did not meet thresholds / no destination")

    elapsed_s = time.perf_counter() - run_start
    print(f"\nTotal time: {elapsed_s:.1f}s ({elapsed_s/60:.2f} min)")
    if processed > 0:
        print(f"Avg time per processed email: {elapsed_s/processed:.2f}s")
        print(f"Log written to: {jsonl_path}")
    print("\nDone.")


if __name__ == "__main__":
    main()
