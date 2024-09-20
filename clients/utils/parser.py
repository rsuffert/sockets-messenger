# parser

import json
from box import Box
import yaml
import os
import re

with open("settings.yaml", "r") as f:
    config = Box(yaml.safe_load(f))

FILE_DELIMITER: str   = config.file_delimiter

username = None

def parse(command: str) -> str:
    """Parses a command typed by the user."""
    def split(command: str) -> list:
        # Regex pattern explanation:
        # - "(\"[^\"]+\")" captures everything inside double quotes as a group
        # - "|(\S+)" matches non-whitespace sequences outside of quotes
        pattern = r'\"([^\"]+)\"|(\S+)'
        matches = re.findall(pattern, command)
        return [m[0] if m[0] else m[1] for m in matches]

    global username
    command_split = split(command)
    if len(command_split) < 1: raise IndexError("Must specify a command")
    match command_split[0]:
        case "nuser":
            if len(command_split) < 2: raise IndexError("Usage: nuser <username>")
            return json.dumps({
                "cmd": "nuser",
                "args": {"username": command_split[1]}
            })
        case "smsg":
            if len(command_split) < 3: raise IndexError("Usage: smsg <destination> {message}")
            return json.dumps({
                "cmd": "smsg",
                "user": username,
                "args": {"destination": command_split[1]},
                "mimetype": "text/plain",
                "body": command_split[2]
            })
        case "sfile":
            if len(command_split) < 3: raise IndexError("Usage: sfile <destination> {file-path}")
            with open(command_split[2], 'r') as f:
                f_content = f.read()
                f_name = os.path.basename(f.name)
            return json.dumps({
                "cmd": "sfile",
                "user": username,
                "args": {"destination": command_split[1]},
                "mimetype": "text/file",
                "body": f"{f_name}{FILE_DELIMITER}{f_content}"
            })
        case "list":
            return json.dumps({
                "cmd": "list",
                "user": username,
                "args": {},
                "mimetype": "text/plain",
                "body": ""
            })
        case "open":
            if len(command_split) < 2: raise IndexError("Usage: open <message-index>")
            if not command_split[1].isdigit(): raise TypeError("argument <message-index> must be a natural number")
            return json.dumps({
                "cmd": "open",
                "user": username,
                "args": {"message-index": int(command_split[1])},
                "mimetype": "text/plain",
                "body": ""
            })
        case "del":
            if len(command_split) < 2: raise IndexError("Usage: del <message-index>")
            if not command_split[1].isdigit(): raise TypeError("argument <message-index> must be a natural number")
            return json.dumps({
                "cmd": "del",
                "user": username,
                "args": {"message-index": int(command_split[1])},
                "mimetype": "text/plain",
                "body": ""
            })
        case "login":
            if len(command_split) < 2: raise IndexError("Usage: login <username>")
            username = command_split[1]
            return None
        case _:
            raise ValueError(f"Unknown command: {command}")