import socket
import subprocess
import sys
import os


def connect_to_server(server_ip, server_port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((server_ip, server_port))
        print("Connected to server.")
        initial_data = client.recv(1024).decode()
        print(f"Received initial data: {initial_data}")
        client.close()
        return initial_data
    except Exception as e:
        print(f"Connection error: {e}")
        return None


def main():
    server_ip = input("Enter server IP: ")
    server_port = int(input("Enter server Port: "))

    initial_data = connect_to_server(server_ip, server_port)
    if initial_data:
        try:
            print("Attempting to launch game.py...")
            result = subprocess.Popen(
                [sys.executable, "Game.py", server_ip, str(server_port), initial_data],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Read and display the output from game.py
            for line in result.stdout:
                print("game.py output:", line.decode(), end='')

            # Check for errors
            for line in result.stderr:
                print("game.py error:", line.decode(), end='')

            print(f"Game launched with PID: {result.pid}")
        except Exception as e:
            print(f"Error launching game.py: {e}")
    else:
        print("Failed to connect to server or receive data.")


if __name__ == "__main__":
    main()
