# messenger

import threading
import json
from datetime import datetime
from typing import Tuple, Dict, Any

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
        
        match json_message['cmd'].strip():
            case "nuser":
                try: self.nuser(json_message['args'][0])
                except Exception as e:
                    return json.dumps({
                        "status": 1,
                        "mimetype": "text/plain",
                        "body": str(e)
                    })
                return json.dumps({
                    "status": 0,
                    "mimetype": "text/plain",
                    "body": "OK"
                })
            case "smsg":
                try: self.smsg(json_message['user'], json_message['args'][0], json_message['body'])
                except Exception as e:
                    return json.dumps({
                        "status": 1,
                        "mimetype": "text/plain",
                        "body": str(e)
                    })
                return json.dumps({
                    "status": 0,
                    "mimetype": "text/plain",
                    "body": "OK"
                })
            case "sfile":
                try: self.sfile(json_message['user'], json_message['args'][0], json_message['body'])
                except Exception as e:
                    return json.dumps({
                        "status": 1,
                        "mimetype": "text/plain",
                        "body": str(e)
                    })
                return json.dumps({
                  "status": 0,
                  "mimetype": "text/plain",
                  "body": "OK"  
                })
            case "list":
                try: res = self.list(json_message['user'])
                except Exception as e:
                    return json.dumps({
                        "status": 1,
                        "mimetype": "text/plain",
                        "body": str(e)
                    })
                return json.dumps({
                    "status": 0,
                    "mimetype": "text/plain",
                    "body": res
                })
            case "open":
                try: 
                    type, content = self.open(json_message['user'], int(json_message['args'][0]))
                    print(content)
                except Exception as e:
                    return json.dumps({
                        "status": 1,
                        "mimetype": "text/plain",
                        "body": str(e)
                    })
                return json.dumps({
                   "status": 0,
                   "mimetype": "text/file" if type == "file" else "text/plain",
                   "body": content
                })
            case "del":
                try: self.delete(json_message['user'], int(json_message['args'][0]))
                except Exception as e:
                    return json.dumps({
                        "status": 1,
                        "mimetype": "text/plain",
                        "body": str(e)
                    })
                return json.dumps({
                    "status": 1,
                    "mimetype": "text/plain",
                    "body": "OK"
                })