import pygame
import pytmx

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
TILE_SIZE = 32
PLAYER_SIZE = 20
VELOCITY = 5
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BOMB_TIMER = 60  # 1-second countdown (60 FPS)
EXPLOSION_RADIUS = 2  # Reduced explosion radius in tiles
COOLDOWN = 60  # 1-second cooldown for placing bombs
PLAYER_LIVES = 3  # Number of player lives
FLASH_DURATION = 30  # Number of frames to flash red

# Initialize the game window and font
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bomberman with Tiled Map")
font = pygame.font.Font(None, 36)  # Font for displaying lives
game_over_font = pygame.font.Font(None, 72)  # Font for game over message

# Load textures
bomb_texture = pygame.image.load("bomb.png").convert_alpha()
player_texture = pygame.image.load("player.png").convert_alpha()


# Player class
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.bombs = []
        self.lives = PLAYER_LIVES
        self.cooldown = 0
        self.hit = False
        self.flash_counter = 0

    def move(self, dx, dy, solid_blocks, breakable_blocks):
        new_rect = self.rect.move(dx * VELOCITY, dy * VELOCITY)
        for block in solid_blocks + breakable_blocks:
            if new_rect.colliderect(block):
                return  # No movement on collision
        self.rect = new_rect
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > SCREEN_WIDTH - PLAYER_SIZE:
            self.rect.x = SCREEN_WIDTH - PLAYER_SIZE
        if self.rect.y < 0:
            self.rect.y = 0
        if self.rect.y > SCREEN_HEIGHT - PLAYER_SIZE:
            self.rect.y = SCREEN_HEIGHT - PLAYER_SIZE

    def place_bomb(self):
        if self.cooldown <= 0:
            bomb_pos = (self.rect.x // TILE_SIZE, self.rect.y // TILE_SIZE)
            bomb = Bomb(bomb_pos[0], bomb_pos[1])
            self.bombs.append(bomb)
            self.cooldown = COOLDOWN

    def update_cooldown(self):
        if self.cooldown > 0:
            self.cooldown -= 1

    def check_damage(self, explosions):
        damage_taken = False
        for explosion in explosions:
            if self.rect.colliderect(explosion):
                if not damage_taken:
                    self.lives -= 1
                    self.hit = True
                    self.flash_counter = FLASH_DURATION
                    damage_taken = True
                    print(f"Player hit! Lives remaining: {self.lives}")
                    if self.lives <= 0:
                        return "Game Over"
        return None


# Bomb class
class Bomb:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.timer = BOMB_TIMER
        self.exploded = False
        self.explosions = []

    def update(self, breakable_blocks, player):
        self.timer -= 1
        if self.timer <= 0 and not self.exploded:
            self.explode(breakable_blocks, player)
            self.exploded = True

    def explode(self, breakable_blocks, player):
        explosion_areas = self.get_explosion_areas()
        self.explosions = explosion_areas

        for block in breakable_blocks[:]:
            for explosion_area in explosion_areas:
                if block.colliderect(explosion_area):
                    breakable_blocks.remove(block)

        damage_result = player.check_damage(explosion_areas)
        if damage_result == "Game Over":
            return

    def get_explosion_areas(self):
        explosion_areas = [self.rect]

        for i in range(1, EXPLOSION_RADIUS + 1):
            up_rect = pygame.Rect(self.rect.x, self.rect.y - i * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            down_rect = pygame.Rect(self.rect.x, self.rect.y + i * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            left_rect = pygame.Rect(self.rect.x - i * TILE_SIZE, self.rect.y, TILE_SIZE, TILE_SIZE)
            right_rect = pygame.Rect(self.rect.x + i * TILE_SIZE, self.rect.y, TILE_SIZE, TILE_SIZE)
            explosion_areas.extend([up_rect, down_rect, left_rect, right_rect])

        return explosion_areas

    def draw(self, screen):
        screen.blit(bomb_texture, self.rect.topleft)


# Load Tiled map
def load_tiled_map(filename):
    tmx_data = pytmx.load_pygame(filename)
    solid_blocks = []
    breakable_blocks = []
    background_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    spawn_points = []

    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile_image = tmx_data.get_tile_image_by_gid(gid)
                if tile_image:
                    background_surface.blit(tile_image, (x * TILE_SIZE, y * TILE_SIZE))
                    tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if layer.name == "Solid":
                        solid_blocks.append(tile_rect)
                    elif layer.name == "Breakable":
                        breakable_blocks.append(tile_rect)
        elif isinstance(layer, pytmx.TiledObjectGroup):
            for obj in layer:
                if obj.name == "spawn":
                    spawn_points.append((obj.x, obj.y))

    return solid_blocks, breakable_blocks, background_surface, spawn_points


# Display lives
def display_lives(player):
    lives_text = font.render(f"Lives: {player.lives}", True, BLACK)
    screen.blit(lives_text, (10, 10))


# Display game over menu
def display_game_over_menu():
    screen.fill(BLACK)
    game_over_text = game_over_font.render("Game Over", True, WHITE)
    restart_text = font.render("Press R to Restart", True, WHITE)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2))
    pygame.display.flip()


# Main game loop
def main():
    clock = pygame.time.Clock()
    solid_blocks, breakable_blocks, background_surface, spawn_points = load_tiled_map("mapa2.tmx")

    if not spawn_points:
        print("Error: No spawn points defined in the map.")
        return

    player_spawn = spawn_points[0]
    player = Player(int(player_spawn[0]), int(player_spawn[1]))

    running = True
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        if not game_over:
            if keys[pygame.K_LEFT]:
                player.move(-1, 0, solid_blocks, breakable_blocks)
            if keys[pygame.K_RIGHT]:
                player.move(1, 0, solid_blocks, breakable_blocks)
            if keys[pygame.K_UP]:
                player.move(0, -1, solid_blocks, breakable_blocks)
            if keys[pygame.K_DOWN]:
                player.move(0, 1, solid_blocks, breakable_blocks)
            if keys[pygame.K_SPACE]:
                player.place_bomb()

            player.update_cooldown()

            for bomb in player.bombs[:]:
                bomb.update(breakable_blocks, player)
                if bomb.exploded:
                    player.bombs.remove(bomb)

            if player.hit:
                player.flash_counter -= 1
                screen.fill(RED)
                if player.flash_counter <= 0:
                    player.hit = False
            else:
                screen.blit(background_surface, (0, 0))

            screen.blit(player_texture, player.rect.topleft)

            for bomb in player.bombs:
                bomb.draw(screen)
                for explosion in bomb.explosions:
                    pygame.draw.rect(screen, (255, 0, 0), explosion)

            display_lives(player)

            if player.lives <= 0:
                game_over = True
                display_game_over_menu()

        if game_over:
            if keys[pygame.K_r]:
                player = Player(int(player_spawn[0]), int(player_spawn[1]))
                player.lives = PLAYER_LIVES
                player.bombs = []
                player.cooldown = 0
                player.hit = False
                player.flash_counter = 0
                solid_blocks, breakable_blocks, background_surface, spawn_points = load_tiled_map("bombex.tmx")
                game_over = False

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
