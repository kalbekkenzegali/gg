import pygame
import random
import sys
import math
 
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
 
WIDTH, HEIGHT = 600, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer Game")
 
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
GRAY   = (50, 50, 50)
DARK   = (30, 30, 30)
RED    = (220, 50, 50)
YELLOW = (255, 220, 0)
GREEN  = (50, 200, 50)
BLUE   = (50, 100, 220)
ORANGE = (255, 160, 0)
CYAN   = (0, 200, 255)
 
clock = pygame.time.Clock()
 
font_large  = pygame.font.SysFont("Arial", 48, bold=True)
font_medium = pygame.font.SysFont("Arial", 28, bold=True)
font_small  = pygame.font.SysFont("Arial", 20)
 
ROAD_LEFT  = 100
ROAD_RIGHT = 500
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT
LANE_COUNT = 3
LANE_WIDTH = ROAD_WIDTH // LANE_COUNT
 
def lane_center(lane):
    return ROAD_LEFT + lane * LANE_WIDTH + LANE_WIDTH // 2
 
 
# ── Дыбыс генераторлары ───────────────────────────────────────
 
def make_sound(samples):
    """Сэмплдер тізімінен Sound объектісін жасау."""
    buf = bytearray()
    for s in samples:
        s = max(-32767, min(32767, int(s)))
        buf += s.to_bytes(2, byteorder='little', signed=True)
        buf += s.to_bytes(2, byteorder='little', signed=True)  # stereo
    return pygame.mixer.Sound(buffer=bytes(buf))
 
 
def generate_engine(base_freq=80, duration_ms=500, vol=0.18):
    """Машина қозғалтқышының гудрономы (rumble + harmonic)."""
    sr = 44100
    n  = int(sr * duration_ms / 1000)
    samples = []
    for i in range(n):
        t = i / sr
        # Негізгі жиілік + кертпеш + дірілдеу
        s  = math.sin(2 * math.pi * base_freq * t)
        s += 0.5 * math.sin(2 * math.pi * base_freq * 2 * t)
        s += 0.25 * math.sin(2 * math.pi * base_freq * 3 * t)
        # Аздап шу қос (дизель эффекті)
        s += 0.15 * (random.random() * 2 - 1)
        # Fade in/out
        fade = min(i, n - i, 500) / 500
        samples.append(vol * 32767 * s * fade)
    return make_sound(samples)
 
 
def generate_crash(duration_ms=600, vol=0.6):
    """Соқтығысу дыбысы — күшті шу + төмен жарылыс."""
    sr = 44100
    n  = int(sr * duration_ms / 1000)
    samples = []
    for i in range(n):
        t = i / sr
        # Ақ шу негізі
        noise = random.random() * 2 - 1
        # Төмен жарылыс (bass thud)
        boom = math.sin(2 * math.pi * 60 * t) * math.exp(-t * 8)
        # Металл сырқырауы
        metal = math.sin(2 * math.pi * 300 * t) * math.exp(-t * 15)
        s = noise * 0.6 + boom * 0.8 + metal * 0.3
        # Экспоненциалды сөну
        decay = math.exp(-t * 5)
        samples.append(vol * 32767 * s * decay)
    return make_sound(samples)
 
 
def generate_coin(duration_ms=120, vol=0.3):
    """Тиын алу — жоғары жиілікті пинг."""
    sr = 44100
    n  = int(sr * duration_ms / 1000)
    samples = []
    for i in range(n):
        t = i / sr
        s = math.sin(2 * math.pi * 1200 * t) + 0.3 * math.sin(2 * math.pi * 1800 * t)
        decay = math.exp(-t * 20)
        samples.append(vol * 32767 * s * decay)
    return make_sound(samples)
 
 
def generate_levelup(duration_ms=300, vol=0.3):
    """Деңгей өсу сигналы."""
    sr = 44100
    n  = int(sr * duration_ms / 1000)
    samples = []
    for i in range(n):
        t   = i / sr
        pct = i / n
        freq = 400 + 400 * pct   # жиілік өседі
        s = math.sin(2 * math.pi * freq * t)
        samples.append(vol * 32767 * s)
    return make_sound(samples)
 
 
# Дыбыстарды жасау
sound_engine = generate_engine(base_freq=90,  duration_ms=800, vol=0.18)
sound_crash  = generate_crash(duration_ms=700, vol=0.6)
sound_coin   = generate_coin(duration_ms=130,  vol=0.3)
sound_level  = generate_levelup(duration_ms=300, vol=0.3)
 
# Қозғалтқыш дыбысын үздіксіз ойнату үшін арнайы канал
engine_channel = pygame.mixer.Channel(0)
sound_engine.set_volume(0.18)
 
def play(sound):
    if sound:
        sound.play()
 
def start_engine():
    engine_channel.play(sound_engine, loops=-1)
 
def stop_engine():
    engine_channel.stop()
 
def set_engine_pitch(speed, base_speed=4.0, max_speed=10.0):
    """Жылдамдыққа байланысты қозғалтқыш дыбысының деңгейін реттеу."""
    ratio = (speed - base_speed) / (max_speed - base_speed)
    vol = 0.12 + 0.12 * max(0, min(1, ratio))
    engine_channel.set_volume(vol)
 
 
# ── Ойыншы машинасы ───────────────────────────────────────────
class PlayerCar:
    W, H = 50, 80
 
    def __init__(self):
        self.lane = 1
        self.x    = lane_center(self.lane)
        self.y    = HEIGHT - 120
 
    def move(self, direction):
        new_lane = self.lane + direction
        if 0 <= new_lane <= 2:
            self.lane = new_lane
            self.x    = lane_center(self.lane)
 
    def draw(self, surface):
        x, y = self.x - self.W // 2, self.y - self.H // 2
        pygame.draw.rect(surface, BLUE, (x, y, self.W, self.H), border_radius=8)
        pygame.draw.rect(surface, CYAN, (x + 8, y + 10, self.W - 16, 20), border_radius=4)
        for wx, wy in [(x-6, y+10), (x+self.W-4, y+10),
                       (x-6, y+self.H-28), (x+self.W-4, y+self.H-28)]:
            pygame.draw.rect(surface, BLACK, (wx, wy, 10, 18), border_radius=3)
        pygame.draw.circle(surface, YELLOW, (x+8,        y+self.H-8), 5)
        pygame.draw.circle(surface, YELLOW, (x+self.W-8, y+self.H-8), 5)
 
    def get_rect(self):
        return pygame.Rect(self.x - self.W//2 + 4, self.y - self.H//2 + 4,
                           self.W - 8, self.H - 8)
 
 
ENEMY_COLORS = [RED, ORANGE, GREEN, (180, 0, 180), (0, 180, 180)]
 
class EnemyCar:
    W, H = 50, 80
 
    def __init__(self, speed):
        self.lane  = random.randint(0, 2)
        self.x     = lane_center(self.lane)
        self.y     = -self.H
        self.speed = speed
        self.color = random.choice(ENEMY_COLORS)
 
    def update(self):
        self.y += self.speed
 
    def draw(self, surface):
        x, y = self.x - self.W//2, self.y - self.H//2
        pygame.draw.rect(surface, self.color, (x, y, self.W, self.H), border_radius=8)
        pygame.draw.rect(surface, CYAN, (x+8, y+self.H-30, self.W-16, 20), border_radius=4)
        for wx, wy in [(x-6, y+10), (x+self.W-4, y+10),
                       (x-6, y+self.H-28), (x+self.W-4, y+self.H-28)]:
            pygame.draw.rect(surface, BLACK, (wx, wy, 10, 18), border_radius=3)
        pygame.draw.circle(surface, (255,255,150), (x+8,        y+8), 5)
        pygame.draw.circle(surface, (255,255,150), (x+self.W-8, y+8), 5)
 
    def get_rect(self):
        return pygame.Rect(self.x - self.W//2 + 4, self.y - self.H//2 + 4,
                           self.W - 8, self.H - 8)
 
    def is_off_screen(self):
        return self.y > HEIGHT + self.H
 
 
class Coin:
    R = 14
 
    def __init__(self, speed):
        self.lane  = random.randint(0, 2)
        self.x     = lane_center(self.lane)
        self.y     = -self.R * 2
        self.speed = speed
 
    def update(self):
        self.y += self.speed
 
    def draw(self, surface):
        pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), self.R)
        pygame.draw.circle(surface, ORANGE, (int(self.x), int(self.y)), self.R, 2)
        txt = font_small.render("$", True, DARK)
        surface.blit(txt, (self.x - txt.get_width()//2, self.y - txt.get_height()//2))
 
    def get_rect(self):
        return pygame.Rect(self.x - self.R, self.y - self.R, self.R*2, self.R*2)
 
    def is_off_screen(self):
        return self.y > HEIGHT + self.R * 2
 
 
stripe_offset = 0
STRIPE_H   = 40
STRIPE_GAP = 60
 
def draw_road(surface, speed):
    global stripe_offset
    stripe_offset = (stripe_offset + speed) % (STRIPE_H + STRIPE_GAP)
    pygame.draw.rect(surface, GRAY, (ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT))
    for lane in range(1, LANE_COUNT):
        lx = ROAD_LEFT + lane * LANE_WIDTH
        y  = -STRIPE_H + stripe_offset - (STRIPE_H + STRIPE_GAP)
        while y < HEIGHT:
            pygame.draw.rect(surface, WHITE, (lx - 2, y, 4, STRIPE_H))
            y += STRIPE_H + STRIPE_GAP
    pygame.draw.rect(surface, WHITE, (ROAD_LEFT,      0, 4, HEIGHT))
    pygame.draw.rect(surface, WHITE, (ROAD_RIGHT - 4, 0, 4, HEIGHT))
 
 
def draw_hud(surface, score, coins, level, spd):
    coin_txt = font_medium.render(f"Coins: {coins}", True, YELLOW)
    surface.blit(coin_txt, (WIDTH - coin_txt.get_width() - 16, 12))
    surface.blit(font_medium.render(f"Score: {score}", True, WHITE), (16, 12))
    surface.blit(font_small.render(f"Level {level}", True, GREEN),   (16, 44))
    surface.blit(font_small.render(f"Speed: {spd:.1f}", True, CYAN), (16, 66))
 
 
def game_over_screen(surface, score, coins):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))
    items = [
        (font_large.render("GAME OVER", True, RED),                  HEIGHT//2 - 100),
        (font_medium.render(f"Score: {score}", True, WHITE),         HEIGHT//2 - 30),
        (font_medium.render(f"Coins: {coins}", True, YELLOW),        HEIGHT//2 + 10),
        (font_small.render("R — restart   ESC — quit", True, GRAY), HEIGHT//2 + 60),
    ]
    for txt, y in items:
        surface.blit(txt, (WIDTH//2 - txt.get_width()//2, y))
    pygame.display.flip()
 
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
 
 
def main():
    while True:
        player      = PlayerCar()
        enemies     = []
        coins       = []
        score       = 0
        coin_count  = 0
        level       = 1
        prev_level  = 1
        enemy_speed = 4.0
        enemy_timer = 0
        coin_timer  = 0
        running     = True
 
        start_engine()  # Қозғалтқыш дыбысын қос
 
        while running:
            clock.tick(60)
 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        player.move(-1)
                    elif event.key == pygame.K_RIGHT:
                        player.move(1)
 
            score += 1
            level  = 1 + score // 600
            enemy_speed = 4.0 + (level - 1) * 1.2
 
            # Жылдамдыққа байланысты қозғалтқыш дыбысын реттеу
            set_engine_pitch(enemy_speed)
 
            if level != prev_level:
                play(sound_level)
                prev_level = level
 
            enemy_timer += 1
            spawn_interval = max(30, 90 - level * 8)
            if enemy_timer >= spawn_interval:
                enemies.append(EnemyCar(enemy_speed))
                enemy_timer = 0
 
            coin_timer += 1
            if coin_timer >= 120:
                coins.append(Coin(enemy_speed))
                coin_timer = 0
 
            for e in enemies: e.update()
            for c in coins:   c.update()
            enemies = [e for e in enemies if not e.is_off_screen()]
            coins   = [c for c in coins   if not c.is_off_screen()]
 
            prect = player.get_rect()
 
            for e in enemies:
                if prect.colliderect(e.get_rect()):
                    stop_engine()           # Қозғалтқышты өшір
                    play(sound_crash)       # Соқтығысу дыбысы
                    pygame.time.delay(700)  # Дыбыс аяқталғанша күт
                    running = False
                    break
 
            for c in coins[:]:
                if prect.colliderect(c.get_rect()):
                    coin_count += 1
                    coins.remove(c)
                    play(sound_coin)
 
            screen.fill(DARK)
            draw_road(screen, enemy_speed)
            for e in enemies: e.draw(screen)
            for c in coins:   c.draw(screen)
            player.draw(screen)
            draw_hud(screen, score // 10, coin_count, level, enemy_speed)
            pygame.display.flip()
 
        game_over_screen(screen, score // 10, coin_count)
 
 
if __name__ == "__main__":
    main()
 