import os
from pathlib import Path
from typing import List

import msal


def _cache_path() -> Path:
    # store locally; add this file to .gitignore
    return Path(os.getenv("M365_TOKEN_CACHE", ".msal_token_cache.bin"))


def _load_cache() -> msal.SerializableTokenCache:
    cache = msal.SerializableTokenCache()
    p = _cache_path()
    if p.exists():
        cache.deserialize(p.read_text(encoding="utf-8"))
    return cache


def _save_cache(cache: msal.SerializableTokenCache) -> None:
    if cache.has_state_changed:
        _cache_path().write_text(cache.serialize(), encoding="utf-8")


def get_m365_access_token(scopes: List[str]) -> str:
    """
    Returns an access token suitable for XOAUTH2 auth to outlook.office365.com IMAP.
    Uses device code flow on first run and refreshes silently afterward.
    """
    client_id = os.getenv("M365_CLIENT_ID")
    if not client_id:
        raise RuntimeError("M365_CLIENT_ID is not set in environment/.env")

    tenant = os.getenv("M365_TENANT", "organizations")
    authority = f"https://login.microsoftonline.com/{tenant}"

    cache = _load_cache()
    app = msal.PublicClientApplication(client_id=client_id, authority=authority, token_cache=cache)

    # Try silent first
    accounts = app.get_accounts()
    result = None
    if accounts:
        result = app.acquire_token_silent(scopes, account=accounts[0])

    # Interactive device code if needed
    if not result:
        flow = app.initiate_device_flow(scopes=scopes)
        if "user_code" not in flow:
            raise RuntimeError(f"Failed to create device flow: {flow}")

        print(flow["message"])  # shows the URL + code
        result = app.acquire_token_by_device_flow(flow)

    _save_cache(cache)

    if "access_token" not in result:
        raise RuntimeError(f"Token acquisition failed: {result}")

    return result["access_token"]