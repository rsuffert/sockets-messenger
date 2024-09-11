import socket
from box import Box
import yaml
import threading

# load config
with open("settings.yaml", "r") as file:
    config = Box(yaml.safe_load(file))

HOST: str = config.server.ip_addr
PORT: int = config.server.port

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Server listening on {HOST}:{PORT}")
        while True:
            conn, addr = server_socket.accept()
            print(f"Connected by {addr}")
            t = threading.Thread(target=handler, args=(conn,))
            t.start()


def handler(connection):
    with connection:
        while True:
            data = connection.recv(1024).decode()
            print(f"Received {data}")
            if len(data) == 0: break
            response = "{\"message\": \"Hello\"}"
            connection.sendall(response.encode())
        print("Client closed connection. Terminating...")

if __name__ == "__main__":
    start_server()