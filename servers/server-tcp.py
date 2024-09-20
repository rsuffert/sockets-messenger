import socket
from box import Box
import yaml
import threading
from utils.messenger import Messenger
import logging

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(asctime)s - %(message)s')

# load config
with open("settings.yaml", "r") as file:
    config = Box(yaml.safe_load(file))

HOST: str = config.server.ip_addr
PORT: int = config.server.port
BUFFER_SIZE: int = config.server.buffer_size
REQUEST_DELIMITER: str = config.request_delimiter
m = Messenger()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        while True:
            conn, addr = server_socket.accept()
            t = threading.Thread(target=handler, args=(conn, addr))
            t.start()

def handler(connection, address):
    buffer = ""
    with connection:
        while True:
            chunk = connection.recv(BUFFER_SIZE).decode()
            logging.info(f"Request received from {address}: {chunk}")
            if len(chunk) == 0: break
            buffer += chunk
            if buffer.endswith(REQUEST_DELIMITER):
                message = buffer.removesuffix(REQUEST_DELIMITER)
                response = m.map_and_handle(message)
                logging.info(f"Sending response to {address}: {response}")
                connection.sendall(response.encode())
                buffer = ""

if __name__ == "__main__":
    start_server()