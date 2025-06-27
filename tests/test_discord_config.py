import json
from core.discord_manager import DiscordManager


def test_default_config_valid(tmp_path, monkeypatch):
    cfg_file = tmp_path / "discord.json"
    cfg_file.write_text(json.dumps({"enabled": False}))
    dm = DiscordManager(config_path=str(cfg_file))
    assert dm._validate_config(dm.config) is True


def test_invalid_config(monkeypatch, tmp_path):
    cfg_file = tmp_path / "discord.json"
    cfg_file.write_text(json.dumps({"enabled": True, "bot_token": ""}))
    dm = DiscordManager(config_path=str(cfg_file))
    assert dm._validate_config(dm.config) is False
