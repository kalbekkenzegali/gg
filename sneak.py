import pygame
import random
import sys

# Pygame-ді іске қосу
pygame.init()

# Ойын өлшемдері
GRID_SIZE = 20          # Бір ұяшық өлшемі (пиксель)
GRID_WIDTH = 30         # Ені (30 ұяшық)
GRID_HEIGHT = 20        # Биіктігі (20 ұяшық)

SCREEN_WIDTH = GRID_WIDTH * GRID_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * GRID_SIZE

# Түстер
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_GREEN = (0, 150, 0)

# Шрифт
font = pygame.font.Font(None, 36)

class Snake:
    """Жылан класы"""
    def __init__(self):
        # Бастапқы позиция (ортада, ұзындығы 3)
        self.body = [
            [GRID_WIDTH // 2, GRID_HEIGHT // 2],
            [GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2],
            [GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2]
        ]
        self.direction = "RIGHT"    # Қозғалыс бағыты
        self.new_direction = "RIGHT"
        
    def change_direction(self, new_dir):
        """Бағытты өзгерту (кері бағытқа бұрылуға болмайды)"""
        opposite_dirs = {
            "UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"
        }
        if new_dir != opposite_dirs.get(self.direction):
            self.new_direction = new_dir
    
    def move(self, grow=False):
        """Жыланды жылжыту"""
        self.direction = self.new_direction
        
        # Жаңа бас позициясын есептеу
        new_head = self.body[0].copy()
        if self.direction == "UP":
            new_head[1] -= 1
        elif self.direction == "DOWN":
            new_head[1] += 1
        elif self.direction == "LEFT":
            new_head[0] -= 1
        elif self.direction == "RIGHT":
            new_head[0] += 1
        
        # Жаңа басты алға қосу
        self.body.insert(0, new_head)
        
        # Егер өсу керек болмаса, құйрықты алып тастау
        if not grow:
            self.body.pop()
    
    def check_collision(self):
        """Өзіне немесе қабырғаға соғылуды тексеру"""
        head = self.body[0]
        
        # Қабырғаға соғылу (талап №1)
        if (head[0] < 0 or head[0] >= GRID_WIDTH or
            head[1] < 0 or head[1] >= GRID_HEIGHT):
            return True
        
        # Өзіне соғылу
        if head in self.body[1:]:
            return True
        
        return False
    
    def draw(self, screen):
        """Жыланды экранға салу"""
        for i, segment in enumerate(self.body):
            color = DARK_GREEN if i == 0 else GREEN
            rect = pygame.Rect(segment[0] * GRID_SIZE, segment[1] * GRID_SIZE,
                               GRID_SIZE - 1, GRID_SIZE - 1)
            pygame.draw.rect(screen, color, rect)


class Food:
    """Тағам класы"""
    def __init__(self, snake_body=None):
        self.position = [0, 0]
        self.generate_random_position(snake_body)
    
    def generate_random_position(self, snake_body):
        """Кездейсоқ позиция (жыланға түспейтін) - талап №2"""
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if snake_body is None or [x, y] not in snake_body:
                self.position = [x, y]
                break
    
    def draw(self, screen):
        """Тағамды экранға салу"""
        rect = pygame.Rect(self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE,
                           GRID_SIZE - 1, GRID_SIZE - 1)
        pygame.draw.rect(screen, RED, rect)


class Game:
    """Ойынды басқару класы"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake - Деңгейлі ойын")
        self.clock = pygame.time.Clock()
        
        self.reset_game()
    
    def reset_game(self):
        """Ойынды қайта бастау"""
        self.snake = Snake()
        self.food = Food(self.snake.body)
        self.score = 0
        self.level = 1
        self.speed = 8           # Бастапқы жылдамдық (FPS)
        self.game_over = False
    
    def update_level_and_speed(self):
        """Деңгей мен жылдамдықты жаңарту (талап №3, №4)"""
        # Әр 4 тағам жеген сайын деңгей көтеріледі
        new_level = self.score // 4 + 1
        
        if new_level > self.level:
            self.level = new_level
            self.speed += 2      # Жылдамдықты арттыру
            print(f"Деңгей {self.level} көтерілді! Жылдамдық: {self.speed}")
    
    def handle_input(self):
        """Пернелерді өңдеу"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.snake.change_direction("UP")
        elif keys[pygame.K_DOWN]:
            self.snake.change_direction("DOWN")
        elif keys[pygame.K_LEFT]:
            self.snake.change_direction("LEFT")
        elif keys[pygame.K_RIGHT]:
            self.snake.change_direction("RIGHT")
        # R батырмасы - ойынды қайта бастау
        if keys[pygame.K_r] and self.game_over:
            self.reset_game()
    
    def update(self):
        """Ойын логикасын жаңарту"""
        if self.game_over:
            return
        
        # Тағамды жеу тексеру
        if self.snake.body[0] == self.food.position:
            # Жыланның өсуі керек (grow=True)
            self.snake.move(grow=True)
            self.score += 1
            # Жаңа тағам жасау (жыланға түспейтін)
            self.food.generate_random_position(self.snake.body)
            # Деңгей мен жылдамдықты жаңарту
            self.update_level_and_speed()
        else:
            self.snake.move(grow=False)
        
        # Соғылу тексеру (талап №1)
        if self.snake.check_collision():
            self.game_over = True
    
    def draw(self):
        """Барлығын экранға салу"""
        self.screen.fill(BLACK)
        
        # Тор сызықтары (әдемілік үшін)
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, (40, 40, 40), (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, (40, 40, 40), (0, y), (SCREEN_WIDTH, y), 1)
        
        self.snake.draw(self.screen)
        self.food.draw(self.screen)
        
        # Ұпай және деңгей личигі (талап №5)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        level_text = font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(level_text, (10, 45))
        
        # Ойын аяқталса, хабарлама көрсету
        if self.game_over:
            game_over_text = font.render("GAME OVER! Press R to restart", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(game_over_text, text_rect)
            
            final_score_text = font.render(f"Final Score: {self.score}  Level: {self.level}", 
                                           True, WHITE)
            score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
            self.screen.blit(final_score_text, score_rect)
        
        pygame.display.flip()
    
    def run(self):
        """Негізгі ойын циклі"""
        running = True
        move_timer = 0
        
        while running:
            # Оқиғаларды өңдеу
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            self.handle_input()
            
            # Жылдамдыққа байланысты қозғалыс аралығы
            # move_timer - жыланның қаншалықты жылдам қозғалатынын басқарады
            if move_timer <= 0:
                self.update()
                self.draw()
                move_timer = self.speed
            else:
                self.draw()  # Экранды жаңарту (қозғалыссыз)
                move_timer -= 1
            
            self.clock.tick(60)  # Максимум 60 FPS
        
        pygame.quit()
        sys.exit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()