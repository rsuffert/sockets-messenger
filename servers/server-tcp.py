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
    with connection:
        while True:
            data = connection.recv(1024).decode()
            logging.info(f"Request received from {address}: {data}")
            if len(data) == 0: break
            response = m.map_and_handle(data)
            logging.info(f"Sending response to {address}: {response}")
            connection.sendall(response.encode())

if __name__ == "__main__":
    start_server()