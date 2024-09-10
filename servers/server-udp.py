import socket
import threading
from box import Box
import yaml

# Load config
with open("settings.yaml", "r") as file:
    config = Box(yaml.safe_load(file))

HOST: str = config.server.ip_addr
PORT: int = config.server.port

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind((HOST, PORT))
        print(f"Server listening on {HOST}:{PORT}")
        while True:
            data, addr = server_socket.recvfrom(1024)
            print(f"Received data from {addr}")
            t = threading.Thread(target=handler, args=(server_socket, data, addr))
            t.start()

def handler(server_socket, data, addr):
    # handle client requests here
    print(f"Received {data.decode()}")
    response = "Hello"
    server_socket.sendto(response.encode(), addr)

if __name__ == "__main__":
    start_server()