from __future__ import annotations

"""XP Dispatcher
================

Centralized helper to award XP (and optional skill points) to the
`core.mmorpg_engine.MMORPGEngine` instance.  Having a dedicated component
keeps GUI panels / CLI tools decoupled from the internal engine state shape.
"""

import logging
from datetime import datetime
from typing import Dict, Optional

from core.mmorpg_engine import MMORPGEngine

logger = logging.getLogger(__name__)

class XPDispatcher:
    """Dispatch XP / skill rewards and handle tier progression."""

    def __init__(self, engine: MMORPGEngine):
        self.engine = engine

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
    def dispatch(
        self,
        xp: int,
        *,
        skill_rewards: Dict[str, int] | None = None,
        source: str = "system",
    ) -> bool:
        """Award XP (and optional skill points) then persist state.

        Returns ``True`` when XP was applied, ``False`` if skipped (e.g. non-positive).
        """
        try:
            if xp <= 0:
                logger.warning("XPDispatcher: non-positive XP ignored (%s)", xp)
                return False

            gs = self.engine.game_state
            gs.total_xp += xp
            logger.info("+%s XP awarded via %s (total=%s)", xp, source, gs.total_xp)

            # Apply skill rewards
            skill_rewards = skill_rewards or {}
            for skill_name, pts in skill_rewards.items():
                if skill_name not in gs.skills:
                    logger.debug("XPDispatcher: unknown skill '%s' – skipping", skill_name)
                    continue
                skill = gs.skills[skill_name]
                skill.experience_points += pts
                skill.current_level = min(skill.max_level, skill.experience_points // 10)
                skill.last_updated = datetime.now()
                logger.info("+%s %s skill points (lvl %s)", pts, skill_name, skill.current_level)

            # Check tier advancement
            self._check_tier_advancement()

            # Persist
            try:
                self.engine.memory_manager.save_game_state(gs)
            except Exception as exc:
                logger.debug("Failed to persist game state: %s", exc)

            return True

        except Exception as e:
            logger.error("XPDispatcher failed (%s XP from %s): %s", xp, source, e)
            return False

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    def _check_tier_advancement(self):
        new_tier = 1
        gs = self.engine.game_state
        for tl in sorted(gs.architect_tiers.keys(), reverse=True):
            if gs.total_xp >= gs.architect_tiers[tl].experience_required:
                new_tier = tl
                break
        if new_tier > gs.current_tier:
            old = gs.current_tier
            gs.current_tier = new_tier
            gs.architect_tiers[new_tier].achieved_at = datetime.now()
            logger.info("🎉 Tier up! %s → %s", old, new_tier)

# Convenience functional wrapper ------------------------------------------------

def dispatch_xp(engine: MMORPGEngine, xp: int, *, skill_rewards: Optional[Dict[str, int]] = None, source: str = "system") -> bool:
    """Functional form – thin proxy over :meth:`XPDispatcher.dispatch`."""
    return XPDispatcher(engine).dispatch(xp, skill_rewards=skill_rewards, source=source)

__all__ = ["XPDispatcher", "dispatch_xp"] 