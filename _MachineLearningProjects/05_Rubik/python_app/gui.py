import pygame
import sys
import random
from cube_env import RubikEnv
from solver import train_agent_demo

# Constants for UI
WINDOW_WIDTH = 850
WINDOW_HEIGHT = 650
FPS = 60

# Colors for stickers: U, D, F, B, L, R
COLOR_MAP = {
    0: (255, 255, 255),  # White (Up)
    1: (255, 215, 0),    # Yellow (Down)
    2: (0, 155, 72),     # Green (Front)
    3: (0, 69, 173),     # Blue (Back)
    4: (255, 88, 0),     # Orange (Left)
    5: (183, 18, 52)     # Red (Right)
}

FACE_NAMES = {
    0: "UP (White)",
    1: "DOWN (Yellow)",
    2: "FRONT (Green)",
    3: "BACK (Blue)",
    4: "LEFT (Orange)",
    5: "RIGHT (Red)"
}

class RubikGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Rubik's Cube Reinforcement Learning Solver")
        self.clock = pygame.clock.Clock()
        self.env = RubikEnv()
        self.moves = ['U', "U'", 'D', "D'", 'F', "F'", 'B', "B'", 'L', "L'", 'R', "R'"]
        
        # Pretrain simple Q-learning agent on launch
        self.agent = train_agent_demo()
        self.scramble_history = []
        self.solving = False
        self.solve_moves = []
        self.font = pygame.font.SysFont('Arial', 18)
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)

    def draw_flat_cube(self):
        """
        Draws a flat 2D net layout of the Rubik's Cube.
        """
        # Starting offsets for each face in the layout net
        # Net pattern:
        #      U
        #    L F R B
        #      D
        offsets = {
            0: (250, 50),   # U
            4: (100, 200),  # L
            2: (250, 200),  # F
            5: (400, 200),  # R
            3: (550, 200),  # B
            1: (250, 350)   # D
        }
        
        size = 35  # sticker side length
        gap = 2    # border gap
        
        for face, (ox, oy) in offsets.items():
            # Draw face label
            lbl = self.font.render(FACE_NAMES[face].split()[0], True, (200, 200, 200))
            self.screen.blit(lbl, (ox + 5, oy - 20))
            
            # Draw 3x3 stickers
            for r in range(3):
                for c in range(3):
                    val = self.env.state[face, r, c]
                    color = COLOR_MAP.get(val, (50, 50, 50))
                    
                    x = ox + c * (size + gap)
                    y = oy + r * (size + gap)
                    
                    pygame.draw.rect(self.screen, color, (x, y, size, size))
                    pygame.draw.rect(self.screen, (0, 0, 0), (x, y, size, size), 1)

    def draw_panel(self):
        # Draw status panels and controls
        title = self.title_font.render("Rubik's Cube RL Solver (Python)", True, (255, 255, 255))
        self.screen.blit(title, (50, 500))

        inst1 = self.font.render("[S] Scramble (Random 3 moves)   [A] AI Solve Step   [R] Reset Cube", True, (200, 200, 200))
        self.screen.blit(inst1, (50, 540))

        inst2 = self.font.render("Keyboard manual moves: U, D, F, B, L, R  (Hold SHIFT for counter-clockwise)", True, (150, 150, 150))
        self.screen.blit(inst2, (50, 570))

        # Status text
        solved_status = "SOLVED" if self.env.is_solved() else "SCRAMBLED"
        status_color = (0, 255, 100) if self.env.is_solved() else (255, 150, 0)
        status_lbl = self.font.render(f"Cube Status: {solved_status}", True, status_color)
        self.screen.blit(status_lbl, (550, 500))

    def scramble(self):
        self.scramble_history = []
        for _ in range(3):  # Limit to 3 moves so our simple Q-table agent can solve it easily!
            m = random.choice(self.moves)
            self.env.step(m)
            self.scramble_history.append(m)

    def run(self):
        while True:
            self.screen.fill((15, 23, 42))  # slate-900 background
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    mods = pygame.key.get_mods()
                    is_shift = mods & pygame.KMOD_SHIFT
                    
                    if event.key == pygame.K_s:
                        self.scramble()
                    elif event.key == pygame.K_r:
                        self.env.reset()
                        self.scramble_history = []
                    elif event.key == pygame.K_a:
                        # Query our trained AI Q-solver
                        state_key = self.agent.get_state_key(self.env.get_state_flat())
                        if state_key in self.agent.q_table:
                            q_vals = self.agent.q_table[state_key]
                            best_action = max(q_vals, key=q_vals.get)
                            self.env.step(best_action)
                        else:
                            # If state unknown to AI, pick a random move towards solving
                            m = random.choice(self.moves)
                            self.env.step(m)
                    
                    # Keyboard direct moves mappings
                    elif event.key == pygame.K_u:
                        self.env.step("U'" if is_shift else "U")
                    elif event.key == pygame.K_d:
                        self.env.step("D'" if is_shift else "D")
                    elif event.key == pygame.K_f:
                        self.env.step("F'" if is_shift else "F")
                    elif event.key == pygame.K_b:
                        self.env.step("B'" if is_shift else "B")
                    elif event.key == pygame.K_l:
                        self.env.step("L'" if is_shift else "L")
                    elif event.key == pygame.K_r:
                        self.env.step("R'" if is_shift else "R")

            self.draw_flat_cube()
            self.draw_panel()
            
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    gui = RubikGUI()
    gui.run()
