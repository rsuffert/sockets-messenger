# usockets

import socket
from typing import Dict, Any, List
import json
from box import Box
import yaml

# Load configs
with open("settings.yaml", "r") as f:
    config = Box(yaml.safe_load(f))
REQUEST_DELIMITER:  str = config.request_delimiter
SERVER_BUFFER_SIZE: int = config.server.buffer_size

class UniformClientSocket:
    """Implements a uniform interface for client sockets, doesn't matter if it is a TCP or UDP socket."""
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
            buffer = ""
            while True:
                chunk = self._sock.recv(1024).decode()
                buffer += chunk
                if len(chunk) == 0 or buffer.endswith(REQUEST_DELIMITER): break
        else:
            chunks = self._chunk_message(message)
            for c in chunks:
                self._sock.sendto(c.encode(), (self._host, self._port))
            buffer = ""
            while True:
                chunk, _ = self._sock.recvfrom(1024)
                buffer += chunk.decode()
                if buffer.endswith(REQUEST_DELIMITER): break
        return json.loads(buffer.removesuffix(REQUEST_DELIMITER))
    
    def _connect(self):
        if self._is_tcp:
            self._sock.connect((self._host, self._port))

    def _close(self):
        self._sock.close()

    def _chunk_message(self, message: str) -> List[str]:
        max_chunk_size = SERVER_BUFFER_SIZE
        return [message[i:i + max_chunk_size] for i in range(0, len(message), max_chunk_size)]

    def __enter__(self):
        self._connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close()