from __future__ import annotations

"""Discord Bridge – subscribes to DSUpdate events and routes them via DiscordManager.
Reuse-first: relies solely on the helper methods recently added to DiscordManager.
"""

import asyncio
import logging
from typing import Union

from core.discord_manager import DiscordManager
from core.models import DSUpdate

logger = logging.getLogger(__name__)

class DiscordBridge:
    """Thin adapter that delivers DSUpdate objects to Discord channels."""

    def __init__(self, dm: DiscordManager | None = None):
        self.dm = dm or DiscordManager()

    async def handle(self, update: DSUpdate):
        """Forward a DSUpdate to the appropriate Discord channel."""
        if not update:
            return
        if not self.dm.is_connected:
            logger.debug("DiscordBridge: manager not connected – skipping update")
            return
        await self.dm.send_update(update.kind, update.msg, update.embed)

    # Convenience for sync producers ---------------------------------------------------
    def handle_sync(self, update: DSUpdate):
        """Blocking wrapper for non-async producers."""
        try:
            asyncio.run(self.handle(update))
        except RuntimeError:
            # We are already inside an event loop (e.g., PyQt); schedule task.
            loop = asyncio.get_event_loop()
            loop.create_task(self.handle(update)) 