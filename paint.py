import pygame
import sys
import math

# Pygame-ді іске қосу
pygame.init()

# Экран өлшемдері
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Түстер
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)

# Экранды құру
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Paint - Сурет салу бағдарламасы")
clock = pygame.time.Clock()

# Шрифт
font = pygame.font.Font(None, 24)


class Button:
    """Құралдар таңдау батырмасы"""
    def __init__(self, x, y, width, height, text, color, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.action = action
        self.hovered = False
    
    def draw(self, screen):
        # Батырма түсі (басылғанда немесе курсор тұрғанда өзгереді)
        color = self.color
        if self.hovered:
            color = tuple(min(255, c + 40) for c in color)
        
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        # Батырмадағы мәтінді орталау
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered
    
    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            return self.action
        return None


class Paint:
    """Paint негізгі класы"""
    def __init__(self):
        # Сурет салатын бет (canvas)
        self.canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT - 80))
        self.canvas.fill(WHITE)
        
        # Құралдар мен параметрлер
        self.tools = ["pen", "rect", "circle", "eraser"]
        self.current_tool = "pen"
        self.current_color = BLACK
        self.pen_size = 5
        self.eraser_size = 20
        
        # Сурет салу күйі
        self.drawing = False
        self.start_pos = None
        self.last_pos = None
        
        # Қосымша түстер
        self.colors = {
            "black": BLACK,
            "red": RED,
            "green": GREEN,
            "blue": BLUE,
            "yellow": YELLOW,
            "white": WHITE
        }
        
        # Батырмаларды құру
        self.create_buttons()
    
    def create_buttons(self):
        """Құралдар мен түс батырмаларын жасау"""
        self.buttons = []
        button_y = SCREEN_HEIGHT - 70
        button_height = 40
        
        # Құрал батырмалары
        tools_x = 10
        tools = [
            ("✏️ Pen", "pen"),
            ("📐 Rect", "rect"),
            ("⚪ Circle", "circle"),
            ("🧽 Eraser", "eraser")
        ]
        
        for text, tool in tools:
            btn = Button(tools_x, button_y, 80, button_height, text, LIGHT_GRAY, tool)
            self.buttons.append(btn)
            tools_x += 85
        
        # Түс батырмалары
        colors_x = 350
        for name, color in self.colors.items():
            # Түс атауының бірінші әрпін көрсету
            display_text = name[0].upper()
            btn = Button(colors_x, button_y, 35, button_height, display_text, color, color)
            self.buttons.append(btn)
            colors_x += 40
        
        # Тазалау батырмасы
        clear_btn = Button(SCREEN_WIDTH - 90, button_y, 80, button_height, "Clear", RED, "clear")
        self.buttons.append(clear_btn)
        
        # Өлшем батырмалары
        size_plus = Button(SCREEN_WIDTH - 180, button_y, 35, button_height, "+", GRAY, "size_up")
        size_minus = Button(SCREEN_WIDTH - 220, button_y, 35, button_height, "-", GRAY, "size_down")
        self.buttons.append(size_plus)
        self.buttons.append(size_minus)
    
    def draw_ui(self):
        """Интерфейсті (батырмалар, мәтіндік ақпарат) салу"""
        # Төменгі панель
        pygame.draw.rect(screen, LIGHT_GRAY, (0, SCREEN_HEIGHT - 80, SCREEN_WIDTH, 80))
        pygame.draw.line(screen, BLACK, (0, SCREEN_HEIGHT - 80), (SCREEN_WIDTH, SCREEN_HEIGHT - 80), 2)
        
        # Батырмаларды салу
        for button in self.buttons:
            button.draw(screen)
        
        # Қазіргі құрал мен түс туралы ақпарат
        tool_text = font.render(f"Tool: {self.current_tool}", True, BLACK)
        size_text = font.render(f"Size: {self.pen_size}", True, BLACK)
        screen.blit(tool_text, (SCREEN_WIDTH - 380, SCREEN_HEIGHT - 40))
        screen.blit(size_text, (SCREEN_WIDTH - 380, SCREEN_HEIGHT - 60))
        
        # Қазіргі түсті көрсету
        color_preview = pygame.Rect(SCREEN_WIDTH - 300, SCREEN_HEIGHT - 65, 30, 30)
        pygame.draw.rect(screen, self.current_color, color_preview)
        pygame.draw.rect(screen, BLACK, color_preview, 2)
    
    def draw_shape(self, start, end, shape):
        """Фигураларды салу (rect, circle)"""
        x1, y1 = start
        x2, y2 = end
        
        if shape == "rect":
            # Тіктөртбұрыш салу (талап №1)
            rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
            pygame.draw.rect(self.canvas, self.current_color, rect, self.pen_size)
        
        elif shape == "circle":
            # Шеңбер салу (талап №2)
            radius = int(math.hypot(x2 - x1, y2 - y1))
            pygame.draw.circle(self.canvas, self.current_color, start, radius, self.pen_size)
    
    def handle_mouse(self, events):
        """Тышқан оқиғаларын өңдеу"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Батырмалардың hover күйін тексеру
        for button in self.buttons:
            button.check_hover(mouse_pos)
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Сол жақ батырма
                    # Батырмаларды тексеру
                    for button in self.buttons:
                        action = button.check_click(mouse_pos)
                        if action:
                            self.handle_action(action)
                            return
                    
                    # Егер батырма басылмаса, сурет салуды бастау
                    if mouse_pos[1] < SCREEN_HEIGHT - 80:
                        self.drawing = True
                        self.start_pos = mouse_pos
                        self.last_pos = mouse_pos
                        
                        # Pen үшін бірден нүкте салу
                        if self.current_tool == "pen":
                            pygame.draw.circle(self.canvas, self.current_color, 
                                             mouse_pos, self.pen_size)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.drawing:
                    # Фигура салуды аяқтау (rect немесе circle)
                    if self.current_tool in ["rect", "circle"]:
                        self.draw_shape(self.start_pos, mouse_pos, self.current_tool)
                    self.drawing = False
                    self.start_pos = None
                    self.last_pos = None
            
            elif event.type == pygame.MOUSEMOTION and self.drawing:
                if mouse_pos[1] < SCREEN_HEIGHT - 80:
                    if self.current_tool == "pen":
                        # Pen - сызық сызу
                        pygame.draw.line(self.canvas, self.current_color, 
                                       self.last_pos, mouse_pos, self.pen_size)
                        self.last_pos = mouse_pos
                    
                    elif self.current_tool == "eraser":
                        # Өшіргіш (талап №3) - ақ түспен бояйды
                        pygame.draw.circle(self.canvas, WHITE, mouse_pos, self.eraser_size)
                        self.last_pos = mouse_pos
    
    def handle_action(self, action):
        """Батырмалардың әрекеттерін орындау"""
        if action == "clear":
            # Барлығын тазалау
            self.canvas.fill(WHITE)
        
        elif action == "size_up":
            self.pen_size = min(50, self.pen_size + 2)
            self.eraser_size = min(50, self.eraser_size + 5)
        
        elif action == "size_down":
            self.pen_size = max(1, self.pen_size - 2)
            self.eraser_size = max(5, self.eraser_size - 5)
        
        elif action in ["pen", "rect", "circle", "eraser"]:
            self.current_tool = action
        
        elif action in self.colors.values():
            self.current_color = action
    
    def run(self):
        """Негізгі ойын циклі"""
        running = True
        
        while running:
            events = []
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                events.append(event)
            
            # Тышқан оқиғаларын өңдеу
            self.handle_mouse(events)
            
            # Экранға салу
            screen.blit(self.canvas, (0, 0))
            self.draw_ui()
            
            # Егер сурет салынып жатса (rect/circle үшін алдын ала көрсету)
            if self.drawing and self.start_pos and self.current_tool in ["rect", "circle"]:
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[1] < SCREEN_HEIGHT - 80:
                    # Уақытша фигураны көрсету
                    temp_surface = self.canvas.copy()
                    self.draw_shape(self.start_pos, mouse_pos, self.current_tool)
                    screen.blit(self.canvas, (0, 0))
                    self.canvas.blit(temp_surface, (0, 0))
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()


def main():
    paint = Paint()
    paint.run()


if __name__ == "__main__":
    main()