"""
University of Manchester CAS (Central Authentication Service) integration.

Uses the CS department CAS at https://studentnet.cs.manchester.ac.uk/authenticate/
Flow:
  1. generate_cas_url()  → frontend redirects user to CAS
  2. CAS redirects user back to callback URL with ?username=&fullname=
  3. verify_and_consume() → backend confirms ticket with CAS server-to-server

Tickets are stored in the database so they survive server restarts (Render free tier
spins down after inactivity, which would clear any in-memory store).
"""

import secrets
import urllib.parse
from datetime import datetime, timedelta

import httpx
from sqlalchemy.orm import Session

from app.models.cas_ticket import CASTicket

CAS_BASE = "https://studentnet.cs.manchester.ac.uk/authenticate/"

TICKET_TTL_SECONDS = 300  # 5 minutes


def generate_cas_url(db: Session, callback_url: str) -> tuple[str, str]:
    """
    Generate a one-time csticket, persist it to the DB, and build the CAS redirect URL.
    Returns (cas_redirect_url, csticket).
    """
    csticket = secrets.token_hex(16)
    expires_at = datetime.utcnow() + timedelta(seconds=TICKET_TTL_SECONDS)

    # Clean up expired tickets while we're here
    db.query(CASTicket).filter(CASTicket.expires_at < datetime.utcnow()).delete()

    ticket = CASTicket(csticket=csticket, callback_url=callback_url, expires_at=expires_at)
    db.add(ticket)
    db.commit()

    params = urllib.parse.urlencode({
        "url": callback_url,
        "csticket": csticket,
        "version": 3,
        "command": "validate",
    })
    return f"{CAS_BASE}?{params}", csticket


def verify_and_consume(db: Session, csticket: str, username: str, fullname: str) -> bool:
    """
    Verify a CAS ticket with the UoM CAS server and consume it (one-time use).
    Returns True if CAS confirms the authentication is valid.
    """
    ticket = db.query(CASTicket).filter(CASTicket.csticket == csticket).first()
    if ticket is None:
        return False

    callback_url = ticket.callback_url
    expired = ticket.expires_at < datetime.utcnow()

    # Consume the ticket regardless of outcome (prevent replay attacks)
    db.delete(ticket)
    db.commit()

    if expired:
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
