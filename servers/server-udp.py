import socket
import threading
from box import Box
import yaml
from messenger import Messenger

# Load config
with open("settings.yaml", "r") as file:
    config = Box(yaml.safe_load(file))

HOST: str = config.server.ip_addr
PORT: int = config.server.port
m = Messenger()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind((HOST, PORT))
        while True:
            data, addr = server_socket.recvfrom(1024)
            t = threading.Thread(target=handler, args=(server_socket, data, addr))
            t.start()

def handler(server_socket, data, addr):
    response = m.map_and_handle(data)
    server_socket.sendto(response.encode(), addr)

if __name__ == "__main__":
    start_server()