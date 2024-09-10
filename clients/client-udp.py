import socket
from box import Box
import yaml

# load config
with open("settings.yaml", "r") as file:
    config = Box(yaml.safe_load(file))

SERVER_HOST: str = config.server.ip_addr
SERVER_PORT: int = config.server.port

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        while True:
            message = input("Enter message: ")
            if message.upper() == "FIM":
                client_socket.close()
                break
            client_socket.sendto(message.encode(), (SERVER_HOST, SERVER_PORT))
            response, _ = client_socket.recvfrom(1024)
            print(f"Response from server: {response.decode()}")

if __name__ == "__main__":
    main()