import socket
import threading
import pytmx


# Function to load the map
def load_map(map_file):
    print(f"Loading map: {map_file}")
    try:
        game_map = pytmx.TiledMap(map_file)
        print("Map loaded successfully!")
        return game_map
    except Exception as e:
        print(f"Failed to load map: {e}")
        return None


# Handle the movement commands
def handle_client(client_socket, game_map):
    player_pos = (100, 100)  # Initial position for the player (x, y)
    player_id = threading.get_ident()

    try:
        # Get spawn points from objects in the map
        spawn_points = [obj for obj in game_map.objects if obj.name == "spawn"]
        if spawn_points:
            spawn_point = spawn_points[player_id % len(spawn_points)]
            spawn_pos = (spawn_point.x, spawn_point.y)
        else:
            spawn_pos = (100, 100)

        print(f"Assigned spawn point {spawn_pos} to player {player_id}")
        client_socket.send(f"Player ID: {player_id}, Spawn Point: {spawn_pos}".encode())

        while True:
            try:
                # Receive movement data from the client
                data = client_socket.recv(1024)
                if not data:
                    print(f"Connection lost with player {player_id}")
                    break  # Connection closed by client

                command = data.decode()
                print(f"Received command: {command}")  # Debugging line

                if command == "UP":
                    player_pos = (player_pos[0], player_pos[1] - 10)
                elif command == "DOWN":
                    player_pos = (player_pos[0], player_pos[1] + 10)
                elif command == "LEFT":
                    player_pos = (player_pos[0] - 10, player_pos[1])
                elif command == "RIGHT":
                    player_pos = (player_pos[0] + 10, player_pos[1])

                position_message = f"Player ID: {player_id}, Position: {player_pos}"
                print(f"Sending position update: {position_message}")  # Debugging line
                client_socket.send(position_message.encode())

            except Exception as e:
                print(f"Error while receiving or sending data: {e}")
                break  # Break the loop on error
    except Exception as e:
        print(f"Exception in client handler: {e}")
    finally:
        client_socket.close()


def start_server():
    server_ip = "127.0.0.1"
    server_port = 5555
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((server_ip, server_port))
    server.listen(5)

    print(f"Server listening on {server_ip}:{server_port}")

    map_file = input("Enter the Tiled map filename (e.g., bombex.tmx): ")
    game_map = load_map(map_file)

    if not game_map:
        print("Error: Map could not be loaded.")
        return

    while True:
        try:
            print("Waiting for a new connection...")
            client_socket, addr = server.accept()
            print(f"Connected to {addr}")
            client_thread = threading.Thread(target=handle_client, args=(client_socket, game_map))
            client_thread.start()
        except Exception as e:
            print(f"Error while accepting connection: {e}")


if __name__ == "__main__":
    start_server()
