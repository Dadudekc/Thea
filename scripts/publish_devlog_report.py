import asyncio
import argparse

from scripts.generate_project_report import build_report
from core.discord_manager import DiscordManager


async def _async_main(channel_key="devlog"):
    dm = DiscordManager()
    if not dm.config.get("enabled"):
        print("Discord integration disabled – nothing to publish")
        return

    connected = await dm.connect()
    if not connected:
        print("Cannot connect to Discord – aborting")
        return

    md = build_report()
    await dm.send_markdown(md, channel_key=channel_key)
    await dm.disconnect()


def main():
    parser = argparse.ArgumentParser(description="Publish auto report to Discord devlog")
    parser.add_argument("--channel", default="devlog", help="semantic channel key (default: devlog)")
    args = parser.parse_args()

    asyncio.run(_async_main(channel_key=args.channel))


if __name__ == "__main__":
    main() 