from box import Box
import yaml
from typing import Dict, Any
import argparse
import os
import time
from utils.usockets import UniformClientSocket
from utils.parser import parse
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(asctime)s - %(message)s')

# Load configs
with open("settings.yaml", "r") as f:
    config = Box(yaml.safe_load(f))
SERVER_HOST: str = config.server.ip_addr
SERVER_PORT: int = config.server.port
FILE_DELIMITER: str = config.file_delimiter

def start_client():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--protocol", type=str, choices=["TCP", "UDP"], required=True, help="Specify the transport protocol to use (TCP or UDP)")
    args = parser.parse_args()

    with UniformClientSocket(SERVER_HOST, SERVER_PORT, args.protocol) as us:
        message = None
        while True:
            command = input("> ")
            if command.strip() == "logout": break
            try: 
                message = parse(command)
                if message:
                    before = time.time()
                    resp = us.send(message)
                    logging.info(f"Received response after: {(time.time()-before)*(10**3)} ms")
                    show(resp)
            except Exception as e: print(e)
        
def show(server_resp : Dict[str, Any]):
    """Prints a response from the server, depending on its mimetype."""
    def generate_new_filename(filename: str) -> str:
        base, extension = os.path.splitext(filename)
        timestamp = int(time.time())
        new_filename = f"{base}_{timestamp}{extension}"
        return new_filename
    
    if server_resp['mimetype'] == "text/plain":
        print(server_resp['body'])
    elif server_resp['mimetype'] == "text/file":
        body_fields = server_resp['body'].split(FILE_DELIMITER, 1)
        if len(body_fields) != 2:
            print("The server response body has an unexpected format. Please retry sending the request.")
            return
        file_name = body_fields[0]
        print(f"Writing file '{file_name}'...")
        if os.path.exists(file_name):
            print(f"File '{file_name}' already exists.")
            while os.path.exists(file_name):
                file_name = generate_new_filename(file_name)
            print(f"Writing file content to '{file_name}' instead.")
        file_content = body_fields[1]
        with open(file_name, 'w') as f:
            f.write(file_content)

if __name__ == "__main__":
    start_client()