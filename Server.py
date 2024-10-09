import socket
import pytmx
import threading
import pygame


def load_map(map_file):
    return pytmx.load_pygame(map_file)


def handle_client(client_socket, game_map):
    try:
        player_id = threading.get_ident()  # Unique ID for each client
        spawn_point = game_map.objects[player_id % len(game_map.objects)].x, game_map.objects[
            player_id % len(game_map.objects)].y
        client_socket.send(f"Player ID: {player_id}, Spawn Point: {spawn_point}".encode())

        while True:
            # Keep the connection alive
            data = client_socket.recv(1024)
            if not data:
                break
            # Handle received data here if needed
    except Exception as e:
        print(f"Exception in thread {threading.current_thread().name}: {e}")
    finally:
        client_socket.close()


def start_server():
    # Initialize pygame
    pygame.init()

    # Create a display window
    screen = pygame.display.set_mode((800, 600))  # Set the window size to 800x600
    pygame.display.set_caption("Server Window")  # Optional: Set a title for the window

    # Set server IP and port
    server_ip = "127.0.0.1"
    server_port = 5555
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((server_ip, server_port))
    server.listen(5)

    print(f"Server listening on {server_ip}:{server_port}")

    # Load your Tiled map here
    map_file = input("Enter the Tiled map filename (e.g., bombex.tmx): ")
    game_map = load_map(map_file)

    while True:
        client_socket, addr = server.accept()
        print(f"Connection from {addr}")
        client_thread = threading.Thread(target=handle_client, args=(client_socket, game_map))
        client_thread.start()


if __name__ == "__main__":
    start_server()
