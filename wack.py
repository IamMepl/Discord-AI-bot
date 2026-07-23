import json
import asyncio

CONFIG_PATH = 'config.json'

# Random chance (0-1) that the bot jumps into a conversation in a channel
# that hasn't been explicitly /register-ed.
RANDOM_CHAT_CHANCE = 0.2

# Guards read-modify-write access to `config` so concurrent slash commands
# (e.g. from two different servers at once) can't clobber each other's changes.
config_lock = asyncio.Lock()


def _load_from_disk():
    try:
        with open(CONFIG_PATH, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        return {}

    # Normalize older config.json formats to the current {"channels": [...], "language": ...} shape.
    for guild_id, guild_data in list(data.items()):
        if isinstance(guild_data, list):
            data[guild_id] = {"channels": guild_data}
        elif isinstance(guild_data, dict) and "channels" not in guild_data:
            data[guild_id] = {"channels": guild_data.get("channels", []), "language": guild_data.get("language")}
    return data


config = _load_from_disk()


def _save_to_disk():
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f)


def reload_config():
    """Re-read config.json from disk, discarding in-memory changes. Used by /wack."""
    global config
    config = _load_from_disk()


def is_registered_channel(guild_id, channel_id):
    guild_data = config.get(guild_id)
    return isinstance(guild_data, dict) and channel_id in guild_data.get("channels", [])


def get_guild_language(guild_id):
    guild_data = config.get(guild_id)
    return guild_data.get("language") if isinstance(guild_data, dict) else None


def _ensure_guild(guild_id):
    if guild_id not in config or not isinstance(config[guild_id], dict):
        config[guild_id] = {"channels": []}
    return config[guild_id]


def register_channel(guild_id, channel_id):
    """Register a channel. Returns True if newly added, False if it was already registered."""
    guild_data = _ensure_guild(guild_id)
    if channel_id in guild_data["channels"]:
        return False
    guild_data["channels"].append(channel_id)
    _save_to_disk()
    return True


def unregister_channel(guild_id, channel_id):
    """Unregister a channel. Returns True if it was registered and got removed."""
    guild_data = config.get(guild_id)
    if isinstance(guild_data, dict) and channel_id in guild_data.get("channels", []):
        guild_data["channels"].remove(channel_id)
        _save_to_disk()
        return True
    return False


def set_language(guild_id, language):
    guild_data = _ensure_guild(guild_id)
    guild_data["language"] = language
    _save_to_disk()
