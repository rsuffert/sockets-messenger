# parser

import regex
import json

def parse(command: str, username: str) -> str:
    command_split = regex.split("\s+", command)
    match command_split[0]:
        case "nuser":
            return json.dumps({
                "cmd": "nuser",
                "args": [command_split[1]]
            })
        case "smsg":
            return json.dumps({
                "cmd": "smsg",
                "user": username,
                "args": [command_split[1]],
                "mimetype": "application/json",
                "body": command_split[2]
            })
        case "sfile":
            with open(command_split[2], 'r') as f:
                body = f.read()
            return json.dumps({
                "cmd": "sfile",
                "user": username,
                "args": command_split[1:],
                "mimetype": "application/json",
                "body": body
            })
        case "list":
            return json.dumps({
                "cmd": "list",
                "user": username,
                "args": [],
                "mimetype": "application/json",
                "body": ""
            })
        case "open":
            return json.dumps({
                "cmd": "open",
                "user": username,
                "args": [command_split[1]],
                "body": ""
            })
        case "del":
            return json.dumps({
                "cmd": "del",
                "user": username,
                "args": [command_split[1]],
                "mimetype": "application/json",
                "body": ""
            })
    return None