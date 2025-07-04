#!/usr/bin/env python3
"""
Resume Controller – Option A
Sends the "resume autonomy" prompt to every Cursor agent window
using standard input_box coords (is_initial_prompt=False).
"""

import asyncio
from pathlib import Path
from datetime import datetime, timezone

from dreamos.utils.gui.injector import CursorInjector

RESUME_PROMPT = (
    "🟢 RESUME AUTONOMY LOOP v6.1\n"
    "Maintain continuous operation. Log to devlog, no direct user reply."
)

async def resume_agent(agent_id: str):
    injector = CursorInjector(agent_id)
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    prompt = f"{RESUME_PROMPT}\n\n(ts={ts})"
    
    # Use the new hybrid injection method for more reliable text input
    await injector.inject_text_hybrid(prompt, is_initial_prompt=False, retries=2)
    
    # Send Ctrl+Enter to submit the prompt
    await injector.send_submission_keys(['ctrl', 'enter'])

async def main():
    tasks = [resume_agent(f"Agent-{i}") for i in range(1, 9)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main()) 