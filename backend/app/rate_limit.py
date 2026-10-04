"""
Rate limiting (slowapi).

Limits are per client IP. Storage defaults to in-memory, which is per process;
when running several workers/servers set RATE_LIMIT_STORAGE_URI=redis://... so they share counts.
"""
import os

from slowapi import Limiter
from slowapi.util import get_remote_address

# Limit strings use the "N/period" format, e.g. "20/minute"
CHAT_LIMIT = os.getenv("RATE_LIMIT_CHAT", "20/minute")             # each message costs OpenAI tokens
LOGIN_LIMIT = os.getenv("RATE_LIMIT_LOGIN", "10/minute")           # slows down password guessing
REGISTER_LIMIT = os.getenv("RATE_LIMIT_REGISTER", "5/minute")      # slows down fake-account creation
SCRAPE_SYNC_LIMIT = os.getenv("RATE_LIMIT_SCRAPE_SYNC", "5/hour")  # scraping + embeddings are expensive

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=os.getenv("RATE_LIMIT_STORAGE_URI", "memory://"),
    enabled=os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true",
)
