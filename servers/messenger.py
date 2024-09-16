# messenger

import threading
import json
from datetime import datetime
from typing import Tuple

class Messenger:
    def __init__(self):
        self._cache = {}
        self._lock  = threading.Lock()
    
    def nuser(self, username: str):
        if username in self._cache: raise ValueError(f"'{username}' user already exists")
        with self._lock:
            self._cache[username] = []

    def smsg(self, origin: str, destination: str, msg: str):
        self._check_user_exists(destination)
        self._check_user_exists(origin)
        with self._lock:
            self._cache[destination].append({
                "from": origin,
                "type": "text message",
                "at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "content": msg
            })
    
    def sfile(self, origin: str, destination: str, file: str):
        self._check_user_exists(destination)
        self._check_user_exists(origin)
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
        if username not in self._cache:
            raise ValueError(f"'{username}' user does not exist")

    def map_and_handle(self, message: str) -> str:
        try: json_message = json.loads(message)
        except json.decoder.JSONDecodeError:
            return json.dumps({
                "status": 1,
                "mimetype": "text/plain",
                "body": "couldn't convert message to JSON"
            })
        
        status = 0
        mime   = "text/plain"
        body   = "OK"

        match json_message['cmd'].strip():
            case "nuser":
                try: self.nuser(json_message['args'][0])
                except Exception as e:
                    status = 1
                    body = str(e)
            case "smsg":
                try: self.smsg(json_message['user'], json_message['args'][0], json_message['body'])
                except Exception as e:
                    status = 1
                    body = str(e)
            case "sfile":
                try: self.sfile(json_message['user'], json_message['args'][0], json_message['body'])
                except Exception as e:
                    status = 1
                    body = str(e)
            case "list":
                try: body = self.list(json_message['user'])
                except Exception as e:
                    status = 1
                    body = str(e)
            case "open":
                try:
                    type, body = self.open(json_message['user'], int(json_message['args'][0]))
                    mime = "text/file" if type == "file" else "text/plain"
                except Exception as e:
                    status = 1
                    body = str(e)
            case "del":
                try: self.delete(json_message['user'], int(json_message['args'][0]))
                except Exception as e:
                    status = 1
                    body = str(e)

        return json.dumps({
            "status": status,
            "mimetype": mime,
            "body": body
        })