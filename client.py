import socket
from box import Box
import yaml
import json
from typing import Dict, Any
import argparse
import regex

# Load configs
with open("settings.yaml", "r") as f:
    config = Box(yaml.safe_load(f))
SERVER_HOST: str = config.server.ip_addr
SERVER_PORT: int = config.server.port

username = None

class UniformSocket:
    def __init__(self, host: str, port: str, protocol: str = "UDP"):
        self._host = host
        self._port = port
        if protocol.upper() == "TCP":
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._is_tcp = True
        elif protocol.upper() == "UDP":
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._is_tcp = False
        else:
            raise ValueError(f"Invalid transport protocol: {protocol}. Use 'TCP' or 'UDP'.")
    
    
    def send(self, message: str) -> Dict[str, Any]:
        if self._is_tcp:
            self._sock.sendall(message.encode())
            response = self._sock.recv(1024)
        else:
            self._sock.sendto(message.encode(), (self._host, self._port))
            response, _ = self._sock.recvfrom(1024)
        return json.loads(response)
    
    def _connect(self):
        if self._is_tcp:
            self._sock.connect((self._host, self._port))

    def _close(self):
        self._sock.close()

    def __enter__(self):
        self._connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close()

def parse(command: str) -> str:
    global username
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
                "mimetype": "text/plain",
                "body": command_split[2]
            })
        case "sfile":
            with open(command_split[2], 'r') as f:
                body = f.read()
            return json.dumps({
                "cmd": "sfile",
                "user": username,
                "args": command_split[1:],
                "mimetype": "text/file",
                "body": body
            })
        case "list":
            return json.dumps({
                "cmd": "list",
                "user": username,
                "args": [],
                "mimetype": "text/plain",
                "body": ""
            })
        case "open":
            return json.dumps({
                "cmd": "open",
                "user": username,
                "args": [command_split[1]],
                "mimetype": "text/plain",
                "body": ""
            })
        case "del":
            return json.dumps({
                "cmd": "del",
                "user": username,
                "args": [command_split[1]],
                "mimetype": "text/plain",
                "body": ""
            })
        case "login":
            username = command_split[1]
            return None
        case _:
            raise ValueError(f"Unknown command: {command}")
        
def show(server_resp : Dict[str, Any]):
    # TODO: implement printing the server response
    print(server_resp)

def start_client():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--protocol", type=str, choices=["TCP", "UDP"], required=True, help="Specify the transport protocol to use (TCP or UDP)")
    args = parser.parse_args()

    with UniformSocket(SERVER_HOST, SERVER_PORT, args.protocol) as us:
        message = None
        while True:
            command = input("> ")
            if command == "logout": break
            try: message = parse(command)
            except ValueError as e: print(e)
            if message:
                show(us.send(message))

if __name__ == "__main__":
    start_client()