
"""
Group Name: CAS/DAN GROUP-15
Group Members:
- S388343 Princy Patel
- S390060 Lamia Sarwar 
- S389242 Mahesh Chandra Regmi
- S390909 Gallage Achintha Methsara Fernando
"""

import pygame
import sys
import random
from abc import ABC, abstractmethod


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

class GameObject(pygame.sprite.Sprite, ABC):
    def __init__(self, image_path, size):
        super().__init__()
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, size)
        self.rect = self.image.get_rect()
        self.max_hp = 100
        self.hp = self.max_hp

    @abstractmethod
    def update(self):
        pass

    def draw_hp_bar(self, surface, bar_width=50, bar_height=5):
        bar_x = self.rect.x + (self.rect.width - bar_width) // 2
        bar_y = self.rect.bottom + 5
        
        # Background
        pygame.draw.rect(surface, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
        
        # Health bar
        health_percentage = self.hp / self.max_hp
        current_width = int(bar_width * health_percentage)
        
        # Color gradient based on health
        if health_percentage > 0.5:
            color = (0, 255, 0)
        elif health_percentage > 0.25:
            color = (255, 255, 0)
        else:
            color = (255, 0, 0)
            
        pygame.draw.rect(surface, color, (bar_x, bar_y, current_width, bar_height))
        pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

class Projectile(GameObject):
    def __init__(self, x, y, target_x, target_y):
        super().__init__('assets/charge.png', (30, 30))
        self.rect.center = (x, y)
        self.target_x = target_x
        self.target_y = target_y
        self.speed = 5
        self.creation_time = pygame.time.get_ticks()
        self.lifetime = 2000

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.creation_time > self.lifetime:
            self.kill()
            return

        dx = self.target_x - self.rect.centerx
        dy = self.target_y - self.rect.centery
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        if distance > 0:
            dx = dx / distance
            dy = dy / distance
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed
            
            self._update_rotation(dx, dy)
            self.image = pygame.transform.scale(self.image, (30, 30))

    def _update_rotation(self, dx, dy):
        if abs(dy) > abs(dx):
            self.image = pygame.transform.rotate(self.original_image, 90 if dy < 0 else -90)
        else:
            self.image = pygame.transform.rotate(self.original_image, 180 if dx < 0 else 0)

class Player(GameObject):
    def __init__(self):
        super().__init__('assets/idle.png', (50, 50))  # Reduced initial size
        self._load_animations()
        self.speed = 5
        self.facing_x = 0
        self.facing_y = -1
        self.is_moving = False

    def _load_animations(self):
        # Load and scale idle animation
        self.idle_sheet = pygame.image.load('assets/idle.png').convert_alpha()
        self.idle_image = pygame.Surface((self.idle_sheet.get_width(), self.idle_sheet.get_height()), pygame.SRCALPHA)
        self.idle_image.blit(self.idle_sheet, (0, 0))
        self.idle_image = pygame.transform.scale(self.idle_image, (50, 50))  # Scale idle image
        
        # Load and scale move animation
        self.move_sheet = pygame.image.load('assets/move.png').convert_alpha()
        self.frame_width = self.move_sheet.get_width() // 6
        self.move_image = pygame.Surface((self.frame_width, self.move_sheet.get_height()), pygame.SRCALPHA)
        self.move_image.blit(self.move_sheet, (0, 0), (0, 0, self.frame_width, self.move_sheet.get_height()))
        self.move_image = pygame.transform.scale(self.move_image, (50, 50))  # Scale move image

    def update(self):
        self._handle_movement()
        self._keep_in_bounds()
        return self._get_projectile()

    def _handle_movement(self):
        keys = pygame.key.get_pressed()
        self.is_moving = False
        
        if keys[pygame.K_w]:
            self._move(0, -1, 90)
        if keys[pygame.K_s]:
            self._move(0, 1, -90)
        if keys[pygame.K_a]:
            self._move(-1, 0, 180)
        if keys[pygame.K_d]:
            self._move(1, 0, 0)
        
        if not self.is_moving:
            self._update_idle_animation()

    def _move(self, dx, dy, rotation):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        self.facing_x = dx
        self.facing_y = dy
        self.is_moving = True
        self.original_image = self.move_image
        self.image = pygame.transform.rotate(self.original_image, rotation)

    def _update_idle_animation(self):
        self.original_image = self.idle_image
        if self.facing_x == 1:
            self.image = pygame.transform.rotate(self.original_image, 0)
        elif self.facing_x == -1:
            self.image = pygame.transform.rotate(self.original_image, 180)
        elif self.facing_y == 1:
            self.image = pygame.transform.rotate(self.original_image, -90)
        else:
            self.image = pygame.transform.rotate(self.original_image, 90)
        self.image = pygame.transform.scale(self.image, (50, 50))

    def _get_projectile(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            target_x = self.rect.centerx + (self.facing_x * 1000)
            target_y = self.rect.centery + (self.facing_y * 1000)
            return Projectile(self.rect.centerx, self.rect.centery, target_x, target_y)
        return None

    def _keep_in_bounds(self):
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)

class Enemy(GameObject):
    def __init__(self):
        super().__init__('assets/idleEnemy.png', (100, 100))
        self.speed = 2
        self.last_shot = 0
        self.shoot_delay = 2000

    def update(self, player):
        self._move_towards_player(player)
        return self._handle_shooting(player)

    def _move_towards_player(self, player):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        if distance > 0:
            dx = dx / distance
            dy = dy / distance
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed
            self._update_rotation(dx, dy)

    def _update_rotation(self, dx, dy):
        if abs(dy) > abs(dx):
            self.image = pygame.transform.rotate(self.original_image, 90 if dy < 0 else -90)
        else:
            self.image = pygame.transform.rotate(self.original_image, 180 if dx < 0 else 0)
        self.image = pygame.transform.scale(self.image, (100, 100))

    def _handle_shooting(self, player):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_delay:
            self.last_shot = current_time
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance > 0:
                dx = dx / distance
                dy = dy / distance
                target_x = self.rect.centerx + (dx * 2000)
                target_y = self.rect.centery + (dy * 2000)
                return Projectile(self.rect.centerx, self.rect.centery, target_x, target_y)
        return None

class Boss(Enemy):
    def __init__(self):
        super().__init__()
        self.max_hp = 200
        self.hp = self.max_hp
        self.image = pygame.transform.scale(self.original_image, (150, 150))
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed = 1.5

    def draw_hp_bar(self, surface):
        super().draw_hp_bar(surface, bar_width=100, bar_height=8)

class Collectible(GameObject):
    def __init__(self):
        super().__init__('assets/idle.png', (30, 30))  # Using a placeholder image
        self._create_plus_sign()
        self.rect.x = random.randint(0, SCREEN_WIDTH - 30)
        self.rect.y = random.randint(0, SCREEN_HEIGHT - 30)
        self.heal_amount = 20

    def _create_plus_sign(self):
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (0, 255, 0), (13, 5, 4, 20))
        pygame.draw.rect(self.image, (0, 255, 0), (5, 13, 20, 4))

    def update(self):
        pass

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self._load_background()
        self.game_started = False
        self.reset_game()

    def _load_background(self):
        self.background = pygame.image.load('assets/space.png').convert()
        self.background = pygame.transform.scale(self.background, 
            (int(SCREEN_WIDTH * 1.5), int(SCREEN_HEIGHT * 1.5)))
        self.camera_x = 0
        self.camera_y = 0

    def reset_game(self):
        self.player = Player()
        self.player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.all_sprites = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.enemy_projectiles = pygame.sprite.Group()
        self.collectibles = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        
        self.score = 0
        self.level = 1
        self.max_level = 5
        self.font = pygame.font.Font(None, 36)
        self.game_over = False
        self.last_collectible_spawn = 0
        self.collectible_spawn_delay = 5000
        self.boss_spawned = False

    def get_max_enemies(self):
        return {
            1: 3, 2: 10, 3: 15, 4: 20, 5: 25
        }.get(self.level, 3)

    def get_spawn_rate(self):
        return {
            1: 5, 2: 10, 3: 15, 4: 20, 5: 25
        }.get(self.level, 5)

    def check_level_up(self):
        new_level = min(self.max_level, (self.score // 100) + 1)
        if new_level != self.level:
            self.level = new_level
            self.boss_spawned = False
            return True
        return False

    def draw_health_bar(self):
        bar_width = 200
        bar_height = 20
        bar_x = (SCREEN_WIDTH - bar_width) // 2
        bar_y = SCREEN_HEIGHT - 40
        
        pygame.draw.rect(self.screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
        
        health_percentage = self.player.hp / self.player.max_hp
        current_width = int(bar_width * health_percentage)
        
        color = (0, 255, 0) if health_percentage > 0.5 else (255, 255, 0) if health_percentage > 0.25 else (255, 0, 0)
        pygame.draw.rect(self.screen, color, (bar_x, bar_y, current_width, bar_height))
        pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        game_over_font = pygame.font.Font(None, 74)
        game_over_text = game_over_font.render('GAME OVER', True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, game_over_rect)

        score_text = self.font.render(f'Final Score: {self.score}', True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        self.screen.blit(score_text, score_rect)

        button_font = pygame.font.Font(None, 48)
        button_text = button_font.render('Restart', True, (255, 255, 255))
        button_rect = button_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        
        button_bg = pygame.Rect(button_rect.x - 20, button_rect.y - 10, 
                              button_rect.width + 40, button_rect.height + 20)
        pygame.draw.rect(self.screen, (50, 50, 50), button_bg)
        pygame.draw.rect(self.screen, (255, 255, 255), button_bg, 2)
        
        self.screen.blit(button_text, button_rect)
        return button_rect

    def draw_start_screen(self):
        # Clear the screen
        self.screen.fill((0, 0, 0))
        
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw title
        title_font = pygame.font.Font(None, 74)
        title_text = title_font.render('SPACE SURVIVOR', True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        self.screen.blit(title_text, title_rect)

        # Draw instructions
        instruction_font = pygame.font.Font(None, 36)
        instructions = [
            "Use WASD to move",
            "Press SPACE to shoot",
            "Collect green plus signs to heal",
            "Survive as long as possible!"
        ]
        
        for i, instruction in enumerate(instructions):
            text = instruction_font.render(instruction, True, (200, 200, 200))
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + i * 40))
            self.screen.blit(text, rect)

        # Draw start button at the bottom
        button_font = pygame.font.Font(None, 48)
        button_text = button_font.render('START GAME', True, (255, 255, 255))
        button_rect = button_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        
        # Draw button background
        button_bg = pygame.Rect(button_rect.x - 20, button_rect.y - 10, 
                              button_rect.width + 40, button_rect.height + 20)
        pygame.draw.rect(self.screen, (50, 50, 50), button_bg)
        pygame.draw.rect(self.screen, (255, 255, 255), button_bg, 2)
        
        self.screen.blit(button_text, button_rect)
        return button_rect

    def run(self):
        while True:
            if not self.game_started:
                self._handle_start_screen()
                self.draw_start_screen()  # Draw start screen every frame
            else:
                self._handle_events()
                self._update_camera()
                self._draw_background()
                
                if not self.game_over:
                    self._update_game_state()
                else:
                    self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(FPS)

    def _handle_start_screen(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                button_rect = self.draw_start_screen()
                if button_rect.collidepoint(mouse_pos):
                    self.game_started = True
                    self.reset_game()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and self.game_over:
                mouse_pos = pygame.mouse.get_pos()
                button_rect = self.draw_game_over()
                if button_rect.collidepoint(mouse_pos):
                    self.reset_game()

    def _update_camera(self):
        target_x = -(self.player.rect.centerx - SCREEN_WIDTH // 2)
        target_y = -(self.player.rect.centery - SCREEN_HEIGHT // 2)
        
        target_x = min(0, max(-(SCREEN_WIDTH * 0.5), target_x))
        target_y = min(0, max(-(SCREEN_HEIGHT * 0.5), target_y))
        
        self.camera_x += (target_x - self.camera_x) * 0.1
        self.camera_y += (target_y - self.camera_y) * 0.1

    def _draw_background(self):
        bg_x = self.camera_x * 0.5
        bg_y = self.camera_y * 0.5
        self.screen.blit(self.background, (bg_x, bg_y))

    def _update_game_state(self):
        self._update_player()
        self._update_projectiles()
        self._update_enemies()
        self._update_collectibles()
        self._draw_game_ui()
        self._handle_spawning()

    def _update_player(self):
        projectile = self.player.update()
        if projectile:
            self.all_sprites.add(projectile)
            self.projectiles.add(projectile)

    def _update_projectiles(self):
        for projectile in list(self.projectiles):
            projectile.update()
            if self._is_off_screen(projectile):
                projectile.kill()

        for projectile in list(self.enemy_projectiles):
            projectile.update()
            if self._is_off_screen(projectile):
                projectile.kill()
            if pygame.sprite.collide_rect(projectile, self.player):
                projectile.kill()
                self.player.hp -= 10
                if self.player.hp <= 0:
                    self.player.hp = 0
                    self.game_over = True

    def _is_off_screen(self, sprite):
        return (sprite.rect.bottom < 0 or sprite.rect.top > SCREEN_HEIGHT or 
                sprite.rect.right < 0 or sprite.rect.left > SCREEN_WIDTH)

    def _update_enemies(self):
        for sprite in list(self.all_sprites):
            if isinstance(sprite, (Enemy, Boss)):
                enemy_projectile = sprite.update(self.player)
                if enemy_projectile:
                    self.all_sprites.add(enemy_projectile)
                    self.enemy_projectiles.add(enemy_projectile)
                
                hits = pygame.sprite.spritecollide(sprite, self.projectiles, True)
                if hits:
                    sprite.hp -= 20
                    if sprite.hp > 0:
                        sprite.max_hp = int(sprite.max_hp * 1.5)
                    else:
                        sprite.kill()
                        self.score += 100 if isinstance(sprite, Boss) else 10
                        self.check_level_up()

    def _update_collectibles(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_collectible_spawn > self.collectible_spawn_delay:
            collectible = Collectible()
            self.all_sprites.add(collectible)
            self.collectibles.add(collectible)
            self.last_collectible_spawn = current_time

        for collectible in list(self.collectibles):
            if pygame.sprite.collide_rect(collectible, self.player):
                self.player.hp = min(self.player.max_hp, self.player.hp + collectible.heal_amount)
                collectible.kill()

    def _draw_game_ui(self):
        self.all_sprites.draw(self.screen)
        
        for sprite in self.all_sprites:
            if isinstance(sprite, (Enemy, Boss)):
                sprite.draw_hp_bar(self.screen)
        
        score_text = self.font.render(f'Score: {self.score}', True, (255, 255, 255))
        score_rect = score_text.get_rect()
        score_rect.topright = (SCREEN_WIDTH - 20, 20)
        self.screen.blit(score_text, score_rect)
        
        level_text = self.font.render(f'Level: {self.level}', True, (255, 255, 255))
        level_rect = level_text.get_rect()
        level_rect.topleft = (20, 20)
        self.screen.blit(level_text, level_rect)
        
        self.draw_health_bar()

    def _handle_spawning(self):
        if self.level == 3 and not self.boss_spawned and self.get_current_enemy_count() == 0:
            boss = Boss()
            self.all_sprites.add(boss)
            self.boss_spawned = True
        elif (random.randint(0, 1000) < self.get_spawn_rate() and 
              self.get_current_enemy_count() < self.get_max_enemies()):
            self.all_sprites.add(Enemy())

    def get_current_enemy_count(self):
        return sum(1 for sprite in self.all_sprites if isinstance(sprite, Enemy))

if __name__ == "__main__":
    game = Game()
    game.run()
    
    