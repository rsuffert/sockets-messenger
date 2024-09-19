# messenger

import threading
import json
from datetime import datetime
from typing import Tuple

def _error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            return json.dumps({"status": 1, "mimetype": "text/plain", "body": f"Missing field in the request: {str(e)}"})
        except json.JSONDecodeError as e:
            return json.dumps({"status": 1, "mimetype": "text/plain", "body": "Couldn't convert message to JSON"})
        except Exception as e:
            return json.dumps({"status": 1, "mimetype": "text/plain", "body": str(e)})
    return wrapper

class Messenger:
    """
    Implements the core of the messenger application in a thread-safe manner, exposing commands to operate over the
    cache of messages swapped between the users.
    """
    def __init__(self):
        self._cache = {}
        self._lock  = threading.Lock()
    
    def nuser(self, username: str):
        if username in self._cache: raise ValueError(f"'{username}' user already exists")
        with self._lock:
            self._cache[username] = []

    def smsg(self, origin: str, destination: str, msg: str):
        self._check_user_exists(origin)
        self._check_user_exists(destination)
        with self._lock:
            self._cache[destination].append({
                "from": origin,
                "type": "text message",
                "at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "content": msg
            })
    
    def sfile(self, origin: str, destination: str, file: str):
        self._check_user_exists(origin)
        self._check_user_exists(destination)
        with self._lock:
            self._cache[destination].append({
                "from": origin,
                "type": "file",
                "at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "content": file
            })
    
    def list(self, origin: str) -> str:
        self._check_user_exists(origin)
        with self._lock:
            msgs = []
            counter = 0
            for msg in self._cache[origin]:
                msgs.append(json.dumps(f"{counter}. {msg['type']} from '{msg['from']}' at {msg['at']}"))
                counter += 1
        return '\n'.join(msgs)
    
    def open(self, origin: str, idx: int) -> Tuple[str, str]:
        self._check_user_exists(origin)
        with self._lock:
            if idx < 0 or idx >= len(self._cache[origin]): raise ValueError(f"message {idx} does not exist")
            msg = self._cache[origin][idx]
        return msg['type'], msg['content']
    
    def delete(self, origin: str, idx: int):
        self._check_user_exists(origin)
        with self._lock:
            if idx < 0 or idx >= len(self._cache[origin]): raise ValueError(f"message {idx} does not exist")
            del self._cache[origin][idx]

    def _check_user_exists(self, username: str):
        if not username:
            raise ValueError(f"'{username}' user does not exist (have you logged in?)")
        if username not in self._cache:
            raise ValueError(f"'{username}' user does not exist")

    @_error_handler
    def map_and_handle(self, message: str) -> str:
        json_message = json.loads(message)
        status = 0
        mime   = "text/plain"
        body   = "OK"
        match json_message['cmd'].strip():
            case "nuser": self.nuser(json_message['args']['username'])
            case "smsg" : self.smsg(json_message['user'], json_message['args']['destination'], json_message['body'])
            case "sfile": self.sfile(json_message['user'], json_message['args']['destination'], json_message['body'])
            case "del"  : self.delete(json_message['user'], int(json_message['args']['message-index']))
            case "list" :
                body = self.list(json_message['user'])
            case "open" :
                type, body = self.open(json_message['user'], int(json_message['args']['message-index']))
                mime = "text/file" if type == "file" else "text/plain"
        return json.dumps({
            "status": status,
            "mimetype": mime,
            "body": body
        })