import socket
import pygame
import pytmx

# Define constants for the screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Function to load the map
def load_map(map_file):
    return pytmx.load_pygame(map_file)

# Function to connect to the server
def connect_to_server(ip, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((ip, port))
        return client
    except Exception as e:
        print(f"Error connecting to server: {e}")
        return None

# Function to draw text on the screen
def draw_text(screen, text, size, color, position):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

# Function to create a button
def draw_button(screen, text, x, y, width, height):
    pygame.draw.rect(screen, (0, 0, 255), (x, y, width, height))  # Button rectangle
    draw_text(screen, text, 30, (255, 255, 255), (x + 10, y + 10))  # Button text

# Main function
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Client Window")

    input_box_ip = pygame.Rect(100, 100, 140, 32)  # Input box for IP
    input_box_port = pygame.Rect(100, 150, 140, 32)  # Input box for Port
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color_ip = color_inactive
    color_port = color_inactive
    active_ip = False
    active_port = False
    ip = ''
    port = ''

    join_ip_button = pygame.Rect(250, 100, 100, 32)  # Button for joining with IP
    join_port_button = pygame.Rect(250, 150, 100, 32)  # Button for joining with Port
    connect_button = pygame.Rect(100, 200, 250, 32)  # General connect button

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box_ip.collidepoint(event.pos):
                    active_ip = not active_ip
                else:
                    active_ip = False
                if input_box_port.collidepoint(event.pos):
                    active_port = not active_port
                else:
                    active_port = False

                # Check if the join IP button was clicked
                if join_ip_button.collidepoint(event.pos) and ip:
                    print(f"IP entered: {ip}")

                # Check if the join Port button was clicked
                if join_port_button.collidepoint(event.pos) and port:
                    print(f"Port entered: {port}")

                # Check if the connect button was clicked
                if connect_button.collidepoint(event.pos) and ip and port:
                    client = connect_to_server(ip, int(port))
                    if client:
                        print("Connected to server!")

            if event.type == pygame.KEYDOWN:
                if active_ip:
                    if event.key == pygame.K_RETURN:
                        active_ip = False
                    elif event.key == pygame.K_BACKSPACE:
                        ip = ip[:-1]
                    else:
                        ip += event.unicode
                elif active_port:
                    if event.key == pygame.K_RETURN:
                        active_port = False
                    elif event.key == pygame.K_BACKSPACE:
                        port = port[:-1]
                    else:
                        port += event.unicode

        # Fill the screen with white
        screen.fill((255, 255, 255))

        # Draw input boxes and text
        pygame.draw.rect(screen, color_ip, input_box_ip)
        draw_text(screen, ip, 30, (0, 0, 0), (input_box_ip.x + 5, input_box_ip.y + 5))

        pygame.draw.rect(screen, color_port, input_box_port)
        draw_text(screen, port, 30, (0, 0, 0), (input_box_port.x + 5, input_box_port.y + 5))

        # Draw the join IP and Port buttons
        draw_button(screen, "Join IP", join_ip_button.x, join_ip_button.y, join_ip_button.width, join_ip_button.height)
        draw_button(screen, "Join Port", join_port_button.x, join_port_button.y, join_port_button.width, join_port_button.height)

        # Draw the connect button
        draw_button(screen, "Connect", connect_button.x, connect_button.y, connect_button.width, connect_button.height)

        # Update the display
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
