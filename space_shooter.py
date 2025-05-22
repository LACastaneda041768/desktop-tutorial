import pygame
import random
import sys
import math
from pygame import mixer
import os

# Initialize Pygame
pygame.init()
mixer.init()

# Create assets directory if it doesn't exist
if not os.path.exists('assets'):
    os.makedirs('assets')

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 7
BULLET_SPEED = 10
ASTEROID_SPEED = 3
SPAWN_RATE = 60
STAR_COUNT = 50

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Shooter")

# Clock for controlling game speed
clock = pygame.time.Clock()

class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.randint(1, 3)
        self.size = random.randint(1, 3)

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (self.x, self.y), self.size)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 4)
        self.life = 30
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(0, self.size - 0.1)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, power_type):
        super().__init__()
        self.type = power_type
        self.size = 20
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(BLACK)
        color = BLUE if power_type == 'speed' else RED if power_type == 'triple_shot' else YELLOW
        pygame.draw.circle(self.image, color, (self.size//2, self.size//2), self.size//2)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.size)
        self.rect.y = -self.size
        self.speed_y = 2

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 40))
        self.image.fill(BLACK)
        # Create a more detailed triangle shape for the player
        pygame.draw.polygon(self.image, BLUE, [(0, 40), (25, 0), (50, 40)])
        pygame.draw.polygon(self.image, WHITE, [(10, 35), (25, 5), (40, 35)])
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed_x = 0
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.triple_shot = False
        self.triple_shot_timer = 0
        self.speed_boost = False
        self.speed_boost_timer = 0

    def update(self):
        now = pygame.time.get_ticks()
        
        # Update power-up timers
        if self.triple_shot and now - self.triple_shot_timer > 5000:
            self.triple_shot = False
        if self.speed_boost and now - self.speed_boost_timer > 5000:
            self.speed_boost = False

        self.speed_x = 0
        keys = pygame.key.get_pressed()
        base_speed = PLAYER_SPEED * (1.5 if self.speed_boost else 1)
        
        if keys[pygame.K_LEFT]:
            self.speed_x = -base_speed
        if keys[pygame.K_RIGHT]:
            self.speed_x = base_speed
        
        self.rect.x += self.speed_x
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle=0):
        super().__init__()
        self.image = pygame.Surface((4, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -BULLET_SPEED
        self.speed_x = BULLET_SPEED * math.sin(math.radians(angle))

    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        if self.rect.bottom < 0 or self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.kill()

class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = random.randint(20, 50)
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(BLACK)
        # Create a more detailed asteroid
        points = []
        for i in range(8):
            angle = i * (360 / 8)
            radius = self.size // 2 * random.uniform(0.8, 1.2)
            x = self.size//2 + radius * math.cos(math.radians(angle))
            y = self.size//2 + radius * math.sin(math.radians(angle))
            points.append((x, y))
        pygame.draw.polygon(self.image, WHITE, points)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.size)
        self.rect.y = -self.size
        self.speed_y = random.randint(2, ASTEROID_SPEED)
        self.speed_x = random.randint(-2, 2)
        self.rotation = 0
        self.rotation_speed = random.randint(-3, 3)

    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        if self.rect.top > SCREEN_HEIGHT or self.rect.left < -self.size or self.rect.right > SCREEN_WIDTH + self.size:
            self.kill()

def create_explosion(x, y, color):
    return [Particle(x, y, color) for _ in range(10)]

def main():
    # Initialize high score
    try:
        with open('highscore.txt', 'r') as f:
            high_score = int(f.read())
    except:
        high_score = 0

    # Create stars
    stars = [Star() for _ in range(STAR_COUNT)]
    
    # Sprite groups
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    
    # Create player
    player = Player()
    all_sprites.add(player)
    
    # Game variables
    score = 0
    game_over = False
    spawn_counter = 0
    particles = []
    
    # Game loop
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE and not game_over:
                    now = pygame.time.get_ticks()
                    if now - player.last_shot > player.shoot_delay:
                        if player.triple_shot:
                            angles = [-15, 0, 15]
                            for angle in angles:
                                bullet = Bullet(player.rect.centerx, player.rect.top, angle)
                                all_sprites.add(bullet)
                                bullets.add(bullet)
                        else:
                            bullet = Bullet(player.rect.centerx, player.rect.top)
                            all_sprites.add(bullet)
                            bullets.add(bullet)
                        player.last_shot = now
        
        if not game_over:
            # Update
            all_sprites.update()
            
            # Update particles
            particles = [p for p in particles if p.life > 0]
            for particle in particles:
                particle.update()
            
            # Update stars
            for star in stars:
                star.update()
            
            # Spawn asteroids
            spawn_counter += 1
            if spawn_counter >= SPAWN_RATE:
                asteroid = Asteroid()
                all_sprites.add(asteroid)
                asteroids.add(asteroid)
                spawn_counter = 0
            
            # Spawn power-ups (5% chance when spawn counter is full)
            if spawn_counter >= SPAWN_RATE and random.random() < 0.05:
                power_type = random.choice(['speed', 'triple_shot'])
                powerup = PowerUp(power_type)
                all_sprites.add(powerup)
                powerups.add(powerup)
            
            # Check for collisions
            # Bullet hits asteroid
            hits = pygame.sprite.groupcollide(asteroids, bullets, True, True)
            for hit in hits:
                score += 10
                particles.extend(create_explosion(hit.rect.centerx, hit.rect.centery, WHITE))
            
            # Player gets power-up
            hits = pygame.sprite.spritecollide(player, powerups, True)
            for hit in hits:
                if hit.type == 'speed':
                    player.speed_boost = True
                    player.speed_boost_timer = pygame.time.get_ticks()
                elif hit.type == 'triple_shot':
                    player.triple_shot = True
                    player.triple_shot_timer = pygame.time.get_ticks()
                particles.extend(create_explosion(hit.rect.centerx, hit.rect.centery, hit.image.get_at((hit.size//2, hit.size//2))))
            
            # Asteroid hits player
            hits = pygame.sprite.spritecollide(player, asteroids, False)
            if hits:
                particles.extend(create_explosion(player.rect.centerx, player.rect.centery, BLUE))
                game_over = True
                if score > high_score:
                    high_score = score
                    with open('highscore.txt', 'w') as f:
                        f.write(str(high_score))
        
        # Draw
        screen.fill(BLACK)
        
        # Draw stars
        for star in stars:
            star.draw(screen)
        
        # Draw particles
        for particle in particles:
            particle.draw(screen)
        
        all_sprites.draw(screen)
        
        # Draw score and high score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {score}', True, WHITE)
        high_score_text = font.render(f'High Score: {high_score}', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (10, 50))
        
        # Draw power-up status
        if player.triple_shot:
            triple_text = font.render('Triple Shot!', True, RED)
            screen.blit(triple_text, (SCREEN_WIDTH - 150, 10))
        if player.speed_boost:
            speed_text = font.render('Speed Boost!', True, BLUE)
            screen.blit(speed_text, (SCREEN_WIDTH - 150, 50))
        
        if game_over:
            game_over_text = font.render('GAME OVER - Press ESC to quit', True, WHITE)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(game_over_text, text_rect)
        
        # Refresh display
        pygame.display.flip()
        
        # Control game speed
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 