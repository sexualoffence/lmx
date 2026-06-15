import os
import json
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

TOKEN = os.getenv("token")
DEFAULT_PREFIX = os.getenv("defprefix")
PREFIX_FILE = "prefixes.json"

def load_prefixes():
    if not os.path.exists(PREFIX_FILE):
        with open(PREFIX_FILE, "w") as f:
            json.dump({}, f)

    with open(PREFIX_FILE, "r") as f:
        return json.load(f)

def save_prefixes(prefixes):
    with open(PREFIX_FILE, "w") as f:
        json.dump(prefixes, f, indent=4)

def get_prefix(bot, message):
    guild_prefix = DEFAULT_PREFIX

    if message.guild:
        prefixes = load_prefixes()
        guild_prefix = prefixes.get(
            str(message.guild.id),
            DEFAULT_PREFIX
        )

    return commands.when_mentioned_or(
        guild_prefix
    )(bot, message)