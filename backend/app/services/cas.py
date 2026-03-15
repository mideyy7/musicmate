"""
University of Manchester CAS (Central Authentication Service) integration.

Uses the CS department CAS at https://studentnet.cs.manchester.ac.uk/authenticate/
Flow:
  1. generate_cas_url()  → frontend redirects user to CAS
  2. CAS redirects user back to callback URL with ?username=&fullname=
  3. verify_and_consume() → backend confirms ticket with CAS server-to-server
"""

import secrets
import time
import urllib.parse

import httpx

CAS_BASE = "https://studentnet.cs.manchester.ac.uk/authenticate/"

# In-memory store: csticket -> (callback_url, expiry_timestamp)
# Tickets are single-use and expire after 5 minutes.
_pending_tickets: dict[str, tuple[str, float]] = {}

TICKET_TTL_SECONDS = 300  # 5 minutes


def generate_cas_url(callback_url: str) -> tuple[str, str]:
    """
    Generate a one-time csticket and build the CAS redirect URL.
    Returns (cas_redirect_url, csticket).
    """
    csticket = secrets.token_hex(16)
    _pending_tickets[csticket] = (callback_url, time.time() + TICKET_TTL_SECONDS)

    params = urllib.parse.urlencode({
        "url": callback_url,
        "csticket": csticket,
        "version": 3,
        "command": "validate",
    })
    return f"{CAS_BASE}?{params}", csticket


def verify_and_consume(csticket: str, username: str, fullname: str) -> bool:
    """
    Verify a CAS ticket with the UoM CAS server and consume it (one-time use).
    Returns True if CAS confirms the authentication is valid.
    """
    # Pop ticket from store (consume regardless of outcome to prevent replay)
    entry = _pending_tickets.pop(csticket, None)
    if entry is None:
        return False

    callback_url, expiry = entry
    if time.time() > expiry:
        return False

    # Server-to-server confirmation with UoM CAS
    try:
        response = httpx.get(
            CAS_BASE,
            params={
                "url": callback_url,
                "csticket": csticket,
                "version": 3,
                "command": "confirm",
                "username": username,
                "fullname": fullname,
            },
            timeout=5,
        )
        return response.text.strip() == "true"
    except Exception:
        return False
