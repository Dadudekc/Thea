import json
import time
import logging
import hashlib
from dataclasses import dataclass
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

@dataclass
class FetchFailure:
    url: str
    attempts: int
    last_error: str
    timestamp: float

class ConversationFetcher:
    """Fetch conversation content with retries and failure logging."""

    def __init__(self, extractor, max_attempts: int = 3, delay: float = 2.0,
                 failure_log: str = "outputs/failed_convos.json"):
        self.extractor = extractor
        self.max_attempts = max_attempts
        self.delay = delay
        self.failure_log = failure_log
        self.failures: List[FetchFailure] = []
        self._hashes: set[str] = set()

    def fetch(self, driver, url: str) -> Optional[Dict[str, str]]:
        """Fetch a conversation with retries."""
        error = ""
        for attempt in range(1, self.max_attempts + 1):
            try:
                if not self.extractor.enter_conversation(driver, url):
                    raise RuntimeError("navigation failed")

                data = self.extractor.get_conversation_content(driver)
                if not data.get("content"):
                    raise RuntimeError("empty content")

                # Duplicate detection via content hash
                content_hash = hashlib.sha1(data["content"].encode("utf-8")).hexdigest()
                if content_hash in self._hashes:
                    logger.info("Duplicate conversation detected: %s", url)
                    return None
                self._hashes.add(content_hash)
                return data
            except Exception as e:  # broad catch for robustness
                error = str(e)
                logger.warning("Fetch attempt %s for %s failed: %s", attempt, url, error)
                time.sleep(self.delay)
        self.failures.append(FetchFailure(url, self.max_attempts, error, time.time()))
        return None

    def save_failures(self):
        if not self.failures:
            return
        try:
            entries = [f.__dict__ for f in self.failures]
            with open(self.failure_log, "w", encoding="utf-8") as f:
                json.dump(entries, f, indent=2)
            logger.info("Saved failure log to %s", self.failure_log)
        except Exception as e:
            logger.error("Failed to save failure log: %s", e)
