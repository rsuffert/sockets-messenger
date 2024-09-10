import socket
from box import Box
import yaml
import regex
import parser

# load config
with open("settings.yaml", "r") as file:
    config = Box(yaml.safe_load(file))

SERVER_HOST: str = config.server.ip_addr
SERVER_PORT: int = config.server.port

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        username = None
        message = None
        while True:
            command = input("> ")
            command_split = regex.split("\s+", command)
            if command_split[0] == "login":
                username = command_split[1]
            elif command_split[0] == "logout":
                client_socket.close()
                break
            else:
                message = parser.parse(command, username)
                if not message:
                    print(f"Unknown command: {command_split[0]}")
                    continue
                client_socket.sendto(message.encode(), (SERVER_HOST, SERVER_PORT))
                response, _ = client_socket.recvfrom(1024)
                print(response.decode())

if __name__ == "__main__":
    main()