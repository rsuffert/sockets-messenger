import socket
import threading
from box import Box
import yaml
from utils.messenger import Messenger
import logging
from typing import List

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(asctime)s - %(message)s')

# Load config
with open("settings.yaml", "r") as file:
    config = Box(yaml.safe_load(file))

HOST: str = config.server.ip_addr
PORT: int = config.server.port
BUFFER_SIZE: int = config.server.buffer_size
REQUEST_DELIMITER: str = config.request_delimiter
m = Messenger()
buffer = {}
lock = threading.Lock()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind((HOST, PORT))
        while True:
            data, addr = server_socket.recvfrom(BUFFER_SIZE)
            t = threading.Thread(target=handler, args=(server_socket, data, addr))
            t.start()

def handler(server_socket, data, addr):
    logging.info(f"Request received from {addr}: {data}")
    with lock:
        if addr not in buffer: buffer[addr] = ""
        buffer[addr] += data.decode()
        if not buffer[addr].endswith(REQUEST_DELIMITER): return
        message = buffer[addr].removesuffix(REQUEST_DELIMITER)
        del buffer[addr]
    response = m.map_and_handle(message)
    logging.info(f"Sending response to {addr}: {response}")
    chunks = chunk_message(response)
    for c in chunks:
        server_socket.sendto(c.encode(), addr)

def chunk_message(message: str) -> List[str]:
    max_chunk_size = BUFFER_SIZE
    return [message[i:i + max_chunk_size] for i in range(0, len(message), max_chunk_size)]

if __name__ == "__main__":
    start_server()