# usockets

import socket
from typing import Dict, Any
import json

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