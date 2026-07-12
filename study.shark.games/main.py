import pygame
import random
import sys
import asyncio

# Initialize Pygame
pygame.init()

# Game Constants
BASE_WIDTH = 800
BASE_HEIGHT = 600
SCREEN_WIDTH = BASE_WIDTH
SCREEN_HEIGHT = BASE_HEIGHT
GRID_SIZE = 20

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
BLUE = (50, 150, 255)
GREEN = (50, 255, 150)
GRAY = (50, 50, 50)
LIGHT_GRAY = (80, 80, 80)

# Setup Screen and Clock
screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Web Arcade: 3 Games in 1")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 30)
virtual_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))

# ==========================================
# UI COMPONENTS
# ==========================================
class Button:
    def __init__(self, x, y, width, height, text, color, target_state=None, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.base_color = color
        self.target_state = target_state
        self.action = action

    def draw(self, surface, mouse_pos):
        # Highlight button on hover
        is_hovered = self.rect.collidepoint(mouse_pos)
        color = tuple(min(c + 40, 255) for c in self.base_color) if is_hovered else self.base_color
        
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, WHITE, self.rect, width=2, border_radius=8)
        
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
        return is_hovered


def get_scale_data():
    screen_width, screen_height = screen.get_size()
    scale = min(screen_width / BASE_WIDTH, screen_height / BASE_HEIGHT)
    scaled_width = max(int(BASE_WIDTH * scale), 1)
    scaled_height = max(int(BASE_HEIGHT * scale), 1)
    x_offset = (screen_width - scaled_width) // 2
    y_offset = (screen_height - scaled_height) // 2
    return scale, x_offset, y_offset, scaled_width, scaled_height


def to_virtual_position(mouse_pos, x_offset, y_offset, scale):
    return ((mouse_pos[0] - x_offset) / scale, (mouse_pos[1] - y_offset) / scale)


def get_touch_direction(mouse_pressed, virtual_mouse):
    if not mouse_pressed:
        return None
    x, y = virtual_mouse
    if x < 0 or x > BASE_WIDTH or y < 0 or y > BASE_HEIGHT:
        return None
    dx = x - BASE_WIDTH / 2
    dy = y - BASE_HEIGHT / 2
    if abs(dx) > abs(dy):
        return (-1, 0) if dx < 0 else (1, 0)
    return (0, -1) if dy < 0 else (0, 1)


def get_touch_action(buttons, virtual_mouse, pressed):
    if not pressed:
        return None
    for btn in buttons:
        if btn.rect.collidepoint(virtual_mouse):
            return btn.action
    return None

# ==========================================
# GAME 1: OBSTACLE DODGER SYSTEM
# ==========================================
class Player:
    def __init__(self):
        self.width, self.height = 40, 40
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 80
        self.speed = 6

    def move(self, keys, touch_direction=None):
        if touch_direction:
            dx, dy = touch_direction
            if dx < 0 and self.x > 0: self.x -= self.speed
            if dx > 0 and self.x < SCREEN_WIDTH - self.width: self.x += self.speed
            if dy < 0 and self.y > 0: self.y -= self.speed
            if dy > 0 and self.y < SCREEN_HEIGHT - self.height: self.y += self.speed
            return
        if keys[pygame.K_LEFT] and self.x > 0: self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width: self.x += self.speed
        if keys[pygame.K_UP] and self.y > 0: self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < SCREEN_HEIGHT - self.height: self.y += self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, (self.x, self.y, self.width, self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Obstacle:
    def __init__(self):
        self.width, self.height = random.randint(40, 100), 30
        self.x = random.randint(0, SCREEN_WIDTH - self.width)
        self.y = -self.height
        self.speed = random.randint(4, 8)

    def update(self): self.y += self.speed
    def draw(self, surface): pygame.draw.rect(surface, RED, (self.x, self.y, self.width, self.height))
    def get_rect(self): return pygame.Rect(self.x, self.y, self.width, self.height)

# ==========================================
# GAME 2: SNAKE SYSTEM
# ==========================================
class SnakeGame:
    def __init__(self): self.reset()
    def reset(self):
        self.body = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = (GRID_SIZE, 0)
        self.spawn_food()
        self.score, self.move_delay = 0, 0

    def spawn_food(self):
        self.food = (
            random.randint(0, (SCREEN_WIDTH - GRID_SIZE) // GRID_SIZE) * GRID_SIZE,
            random.randint(0, (SCREEN_HEIGHT - GRID_SIZE) // GRID_SIZE) * GRID_SIZE
        )

    def set_direction(self, new_direction):
        if new_direction[0] == -self.direction[0] and new_direction[1] == -self.direction[1]:
            return
        self.direction = new_direction

    def handle_input(self, keys):
        if keys[pygame.K_LEFT]:
            self.set_direction((-GRID_SIZE, 0))
        if keys[pygame.K_RIGHT]:
            self.set_direction((GRID_SIZE, 0))
        if keys[pygame.K_UP]:
            self.set_direction((0, -GRID_SIZE))
        if keys[pygame.K_DOWN]:
            self.set_direction((0, GRID_SIZE))

    def handle_touch(self, direction):
        if direction is not None:
            self.set_direction((direction[0] * GRID_SIZE, direction[1] * GRID_SIZE))

    def update(self):
        self.move_delay += 1
        if self.move_delay < 5: return True
        self.move_delay = 0
        new_head = (self.body[0][0] + self.direction[0], self.body[0][1] + self.direction[1])
        if (new_head[0] < 0 or new_head[0] >= SCREEN_WIDTH or new_head[1] < 0 or new_head[1] >= SCREEN_HEIGHT or new_head in self.body):
            return False
        self.body.insert(0, new_head)
        if new_head == self.food:
            self.score += 1
            self.spawn_food()
        else: self.body.pop()
        return True

    def draw(self, surface):
        for seg in self.body: pygame.draw.rect(surface, GREEN, (seg[0], seg[1], GRID_SIZE - 2, GRID_SIZE - 2))
        pygame.draw.rect(surface, RED, (self.food[0], self.food[1], GRID_SIZE - 2, GRID_SIZE - 2))

# ==========================================
# GAME 3: PONG SYSTEM (VS AI)
# ==========================================
class PongGame:
    def __init__(self): self.reset()
    def reset(self):
        self.p_width, self.p_height = 15, 90
        self.player_y = SCREEN_HEIGHT // 2 - self.p_height // 2
        self.ai_y = SCREEN_HEIGHT // 2 - self.p_height // 2
        self.ball_x, self.ball_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        self.ball_dx, self.ball_dy = random.choice([-5, 5]), random.choice([-3, 3])
        self.score, self.speed = 0, 5

    def update(self, keys, touch_direction=None):
        # Player control
        if touch_direction:
            if touch_direction == (0, -1) and self.player_y > 0:
                self.player_y -= self.speed
            elif touch_direction == (0, 1) and self.player_y < SCREEN_HEIGHT - self.p_height:
                self.player_y += self.speed
        else:
            if keys[pygame.K_UP] and self.player_y > 0: self.player_y -= self.speed
            if keys[pygame.K_DOWN] and self.player_y < SCREEN_HEIGHT - self.p_height: self.player_y += self.speed
        
        # Simple AI Tracking
        if self.ball_y > self.ai_y + self.p_height // 2 and self.ai_y < SCREEN_HEIGHT - self.p_height: self.ai_y += 4
        elif self.ball_y < self.ai_y + self.p_height // 2 and self.ai_y > 0: self.ai_y -= 4

        # Ball Logic
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        # Wall bounces
        if self.ball_y <= 0 or self.ball_y >= SCREEN_HEIGHT - 15: self.ball_dy *= -1

        # Build boundaries
        p_rect = pygame.Rect(30, self.player_y, self.p_width, self.p_height)
        ai_rect = pygame.Rect(SCREEN_WIDTH - 30 - self.p_width, self.ai_y, self.p_width, self.p_height)
        ball_rect = pygame.Rect(self.ball_x, self.ball_y, 15, 15)

        # Paddle Collisions
        if ball_rect.colliderect(p_rect) and self.ball_dx < 0:
            self.ball_dx *= -1.1  # Speed up slightly
            self.score += 1
        if ball_rect.colliderect(ai_rect) and self.ball_dx > 0:
            self.ball_dx *= -1.1

        # Win / Loss conditions
        if self.ball_x < 0: return False  # Missed the ball -> Game over
        if self.ball_x > SCREEN_WIDTH:    # AI missed -> Reset ball position
            self.ball_x, self.ball_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
            self.ball_dx = -5
        return True

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, (30, self.player_y, self.p_width, self.p_height))
        pygame.draw.rect(surface, WHITE, (SCREEN_WIDTH - 30 - self.p_width, self.ai_y, self.p_width, self.p_height))
        pygame.draw.ellipse(surface, WHITE, (self.ball_x, self.ball_y, 15, 15))
        pygame.draw.aaline(surface, LIGHT_GRAY, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT))

# ==========================================
# MAIN ARCADE LOOP
# ==========================================
async def main():
    global screen
    state = "MENU"
    
    # Initialize game objects
    player = Player()
    obstacles = []
    dodger_score, spawn_timer = 0, 0
    snake = SnakeGame()
    pong = PongGame()

    # Create UI Buttons
    btn_w, btn_h = 350, 50
    btn_x = SCREEN_WIDTH // 2 - btn_w // 2
    buttons = [
        Button(btn_x, 240, btn_w, btn_h, "1. Obstacle Dodger", GRAY, "DODGER"),
        Button(btn_x, 310, btn_w, btn_h, "2. Snake Game", GRAY, "SNAKE"),
        Button(btn_x, 380, btn_w, btn_h, "3. Classic Pong", GRAY, "PONG")
    ]

    touch_controls = {
        "DODGER": [
            Button(40, 420, 70, 70, "⬅", GRAY, None, action=(-1, 0)),
            Button(130, 420, 70, 70, "➡", GRAY, None, action=(1, 0)),
            Button(85, 350, 70, 70, "⬆", GRAY, None, action=(0, -1)),
            Button(85, 500, 70, 70, "⬇", GRAY, None, action=(0, 1))
        ],
        "SNAKE": [
            Button(40, 420, 70, 70, "⬅", GRAY, None, action=(-1, 0)),
            Button(130, 420, 70, 70, "➡", GRAY, None, action=(1, 0)),
            Button(85, 350, 70, 70, "⬆", GRAY, None, action=(0, -1)),
            Button(85, 500, 70, 70, "⬇", GRAY, None, action=(0, 1))
        ],
        "PONG": [
            Button(BASE_WIDTH - 110, 420, 70, 70, "⬆", GRAY, None, action=(0, -1)),
            Button(BASE_WIDTH - 110, 500, 70, 70, "⬇", GRAY, None, action=(0, 1))
        ]
    }
    menu_button = Button(BASE_WIDTH - 160, 20, 140, 50, "Menu", BLUE, None, action="MENU")

    while True:
        actual_mouse_pos = pygame.mouse.get_pos()
        clicked = False
        touch_pressed = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked = True
            if event.type == pygame.FINGERDOWN:
                actual_mouse_pos = (event.x * screen.get_width(), event.y * screen.get_height())
                clicked = True
                touch_pressed = True
            if event.type == pygame.FINGERUP:
                touch_pressed = False
            if event.type == pygame.FINGERMOTION:
                actual_mouse_pos = (event.x * screen.get_width(), event.y * screen.get_height())

        keys = pygame.key.get_pressed()
        screen.fill(BLACK)

        scale, x_offset, y_offset, scaled_width, scaled_height = get_scale_data()
        virtual_mouse = to_virtual_position(actual_mouse_pos, x_offset, y_offset, scale)
        virtual_mouse_pressed = pygame.mouse.get_pressed()[0] or touch_pressed
        virtual_clicked = clicked and 0 <= virtual_mouse[0] <= SCREEN_WIDTH and 0 <= virtual_mouse[1] <= SCREEN_HEIGHT
        touch_direction = get_touch_action(touch_controls.get(state, []), virtual_mouse, virtual_mouse_pressed)

        virtual_surface.fill(BLACK)

        # ------------------------------------------
        # MENU LAYER
        # ------------------------------------------
        if state == "MENU":
            title = font.render("Python Web Arcade", True, WHITE)
            virtual_surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 130))

            for btn in buttons:
                hovered = btn.draw(virtual_surface, virtual_mouse)
                
                # Check for keyboard triggers OR mouse clicks
                if (virtual_clicked and hovered) or (btn.target_state == "DODGER" and keys[pygame.K_1]) or \
                   (btn.target_state == "SNAKE" and keys[pygame.K_2]) or (btn.target_state == "PONG" and keys[pygame.K_3]):
                    state = btn.target_state
                    if state == "DODGER":
                        player = Player()
                        obstacles.clear()
                        dodger_score = 0
                    elif state == "SNAKE": snake.reset()
                    elif state == "PONG": pong.reset()

        # ------------------------------------------
        # GAME LAYER: DODGER
        # ------------------------------------------
        elif state == "DODGER":
            player.move(keys, touch_direction)
            spawn_timer += 1
            if spawn_timer >= 30:
                obstacles.append(Obstacle())
                spawn_timer = 0

            for obstacle in obstacles[:]:
                obstacle.update()
                if obstacle.y > SCREEN_HEIGHT:
                    obstacles.remove(obstacle)
                    dodger_score += 1
                if player.get_rect().colliderect(obstacle.get_rect()):
                    state = "MENU"

            player.draw(virtual_surface)
            for obstacle in obstacles:
                obstacle.draw(virtual_surface)

            score_text = font.render(f"Score: {dodger_score}   |   Press [ESC] for Menu", True, WHITE)
            virtual_surface.blit(score_text, (10, 10))
            if keys[pygame.K_ESCAPE]:
                state = "MENU"

        # ------------------------------------------
        # GAME LAYER: SNAKE
        # ------------------------------------------
        elif state == "SNAKE":
            if touch_direction:
                snake.handle_touch(touch_direction)
            else:
                snake.handle_input(keys)
            if not snake.update():
                state = "MENU"
            snake.draw(virtual_surface)
            score_text = font.render(f"Score: {snake.score}   |   Press [ESC] for Menu", True, WHITE)
            virtual_surface.blit(score_text, (10, 10))
            if keys[pygame.K_ESCAPE]:
                state = "MENU"

        # ------------------------------------------
        # GAME LAYER: PONG
        # ------------------------------------------
        elif state == "PONG":
            if not pong.update(keys, touch_direction):
                state = "MENU"
            pong.draw(virtual_surface)
            score_text = font.render(f"Score: {pong.score}   |   Press [ESC] for Menu", True, WHITE)
            virtual_surface.blit(score_text, (10, 10))
            if keys[pygame.K_ESCAPE]:
                state = "MENU"

        if state in touch_controls:
            for btn in touch_controls[state]:
                btn.draw(virtual_surface, virtual_mouse)

        if menu_button.draw(virtual_surface, virtual_mouse) and virtual_mouse_pressed:
            state = "MENU"

        # Scale the virtual canvas and center it in the actual window
        scaled_surface = pygame.transform.smoothscale(virtual_surface, (scaled_width, scaled_height))
        screen.blit(scaled_surface, (x_offset, y_offset))

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

asyncio.run(main())