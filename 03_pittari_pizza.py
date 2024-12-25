import pyxel
import math
import random

# Game settings
SCREEN_WIDTH = 160
SCREEN_HEIGHT = 120
PIZZA_RADIUS = 50
CUT_ANGLE = math.pi / 3  # 60 degrees
MAX_HEALTH = 3
START_X = SCREEN_WIDTH // 2
START_Y = SCREEN_HEIGHT // 2
MIN_CUTS = 4  # Minimum number of cuts

class PizzaGame:
    def __init__(self):
        self.score = 0
        self.level = 1
        self.health = MAX_HEALTH
        self.cuts = 0
        self.cut_angles = []  # List to store the cut angles
        self.game_over = False
        self.cut_line_angle = 0  # Angle of the rotating line
        self.target_cuts = random.randint(MIN_CUTS, 4 + self.level * 2)  # Max cuts based on level
        self.target_cuts_remaining = self.target_cuts
        self.is_paused = False  # Game pause state
        self.show_title_screen = True  # Title screen flag

        # Rotation speed base
        self.speed = 0.05
        self.rotation_speed = self.speed  # Initial rotation speed
        self.speed_rand = 1

        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Pittari Pizza")  # Initialize the window
        pyxel.run(self.update, self.draw)

    def update(self):
        if self.show_title_screen:
            # Show title screen and wait for the player to start
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnp(pyxel.KEY_SPACE):
                self.show_title_screen = False  # Start the game
            return

        if self.game_over:
            # Wait for restart after game over
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnp(pyxel.KEY_SPACE):
                self.reset_game()
            return

        # Game logic when not paused or in game over state
        if not self.is_paused:
            # Update level and rotation speed based on score
            self.level = min(self.score // 10 + 1, 5)
            self.rotation_speed = self.speed * ((self.level + 5) / 5) * self.speed_rand
            
            # Update the angle of the rotating cut line
            self.cut_line_angle += self.rotation_speed

            # Cut when the player presses a button
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnp(pyxel.KEY_SPACE):  
                self.make_cut()

            # Update health after target cuts are completed
            if self.target_cuts_remaining == 0:
                self.calculate_health()
                self.is_paused = True  # Pause the game

        elif pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnp(pyxel.KEY_SPACE):
            # Resume game after pausing
            self.target_cuts = random.randint(MIN_CUTS, 4 + self.level * 2)  # New target cuts based on level
            self.speed_rand = random.randint(0, 7) / 10 + 0.7
            self.target_cuts_remaining = self.target_cuts  # Reset remaining cuts
            self.cut_angles.clear()  # Clear cut angles
            self.is_paused = False  # Resume the game
            if self.health <= 0:
                self.game_over = True

    def draw(self):
        pyxel.cls(0)  # Clear screen

        if self.show_title_screen:
            # Draw title screen
            pyxel.text(SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2, "PITTARI PIZZA", (pyxel.frame_count) // 4 % 16)
            pyxel.text(SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2 + 10, "PRESS SPACE TO START", pyxel.COLOR_WHITE)
            return

        if self.game_over:
            # Draw game over screen
            pyxel.text(SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2, "GAME OVER", pyxel.COLOR_RED)
            pyxel.text(SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2 + 10, f"03-Score: {self.score}", pyxel.COLOR_WHITE)
            pyxel.text(SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 + 20, "PRESS SPACE TO RESTART", pyxel.COLOR_WHITE)
            return

        # Draw the game when not paused
        if not self.is_paused:
            # Draw the pizza
            pyxel.circ(START_X, START_Y, PIZZA_RADIUS, pyxel.COLOR_YELLOW)

            # Draw the rotating cut line
            x1 = START_X + PIZZA_RADIUS * math.cos(self.cut_line_angle)
            y1 = START_Y + PIZZA_RADIUS * math.sin(self.cut_line_angle)
            pyxel.line(START_X, START_Y, x1, y1, pyxel.COLOR_RED)

            # Draw previous cuts
            for angle in self.cut_angles:
                x1 = START_X + PIZZA_RADIUS * math.cos(angle)
                y1 = START_Y + PIZZA_RADIUS * math.sin(angle)
                pyxel.line(START_X, START_Y, x1, y1, pyxel.COLOR_RED)

            for i in range(MAX_HEALTH):
                x = SCREEN_WIDTH - 7 * (i + 1)
                y = 5
                if i < self.health:
                    pyxel.circ(x, y, 2, 7)  # Circle for remaining lives
                else:
                    pyxel.text(x - 3, y - 3, "x", 8)  # "x" for lost lives]
            
            # Display score
            pyxel.text(5, 10, f"Score: {self.score}", pyxel.COLOR_WHITE)
        
                    # 現在の目標のカット数表示
            if self.target_cuts<7:
                pyxel.text(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 10, f"Cut: {self.target_cuts}", 7)
            elif self.target_cuts == 8 or self.target_cuts == 10:
                pyxel.text(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 10, f"Cut: {self.target_cuts}", 9)
            else:
                pyxel.text(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 10, f"Cut: {self.target_cuts}",(pyxel.frame_count) // 4 % 16)

        # If paused, show health status
        if self.is_paused:
            # Draw pizza and cuts
            pyxel.circ(START_X, START_Y, PIZZA_RADIUS, pyxel.COLOR_YELLOW)

            slice_areas = self.calculate_areas()
            max_area = max(slice_areas)
            min_area = min(slice_areas)
            area_difference = max_area / min_area

            # Draw previous cuts
            for angle in self.cut_angles:
                x1 = START_X + PIZZA_RADIUS * math.cos(angle)
                y1 = START_Y + PIZZA_RADIUS * math.sin(angle)
                pyxel.line(START_X, START_Y, x1, y1, pyxel.COLOR_RED)

            # Display quality of cuts
            if abs(area_difference - 1) < 0.03:
                pyxel.text(SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 + 10, "Perfect!!", pyxel.COLOR_WHITE)
            elif abs(area_difference - 1) < 0.1:
                pyxel.text(SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 + 10, "Great!", pyxel.COLOR_WHITE)
            elif abs(area_difference - 1) < (self.target_cuts / 22):
                pyxel.text(SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 + 10, "Good!", pyxel.COLOR_WHITE)
            elif abs(area_difference - 1) < (self.target_cuts / 10):
                pyxel.text(SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 + 10, "Ok", pyxel.COLOR_WHITE)
            else:
                pyxel.text(SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 + 10, "Oops!", pyxel.COLOR_WHITE)
            pyxel.text(SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 + 20, f"Max/Min: {int(abs(area_difference) * 100)}%", pyxel.COLOR_WHITE)

            # Display score
            pyxel.text(5, 10, f"Score: {self.score}", pyxel.COLOR_WHITE)

            for i in range(MAX_HEALTH):
                x = SCREEN_WIDTH - 7 * (i + 1)
                y = 5
                if i < self.health:
                    pyxel.circ(x, y, 2, 7)  # Circle for remaining lives
                else:
                    pyxel.text(x - 3, y - 3, "x", 8)  # "x" for lost lives]

    def make_cut(self):
        if len(self.cut_angles) < self.target_cuts:
            # Make a cut based on the current cut line angle
            angle = self.cut_line_angle
            self.cut_angles.append(angle)
            self.cuts += 1
            self.target_cuts_remaining -= 1  # Decrease remaining cuts

    def calculate_health(self):
        if len(self.cut_angles) == self.target_cuts:
            # Calculate health and score after cuts
            if self.cut_angles:  # Only calculate areas if there are cuts
                slice_areas = self.calculate_areas()
                max_area = max(slice_areas)
                min_area = min(slice_areas)
                area_difference = max_area / min_area

                if self.target_cuts < 7:
                    self.bonus = 1
                elif self.target_cuts == 8 or self.target_cuts == 10:
                    self.bonus = 3
                else:
                    self.bonus = 5
                
                if abs(area_difference - 1) < 0.03:
                    self.score += 5 * self.bonus
                elif abs(area_difference - 1) < 0.1:
                    self.score += 3 * self.bonus
                elif abs(area_difference - 1) < (self.target_cuts / 22):
                    self.score += 2 * self.bonus
                elif abs(area_difference - 1) < (self.target_cuts / 10):
                    self.score += 1 * self.bonus
                else:
                    self.health -= 1  # Lose health

                self.is_paused = True  # Pause the game
                self.cuts = 0  # Reset cuts

    def calculate_areas(self):
        # Normalize angles to range 0 to 2π and sort
        angles = [(angle + 2 * math.pi) % (2 * math.pi) for angle in self.cut_angles]
        angles.sort()  # Sort angles in ascending order
        angles.append(angles[0] + 2 * math.pi)  # Add first angle to close the circle

        areas = []
        for i in range(1, len(angles)):
            angle_diff = angles[i] - angles[i - 1]
            area = 0.5 * PIZZA_RADIUS**2 * angle_diff
            areas.append(area)

        return areas

    def reset_game(self):
        # Reset all game parameters for a new game
        self.score = 0
        self.level = 1
        self.health = MAX_HEALTH
        self.cuts = 0
        self.cut_angles.clear()
        self.target_cuts = random.randint(MIN_CUTS, 4 + self.level * 2)
        self.target_cuts_remaining = self.target_cuts
        self.game_over = False
        self.is_paused = False
        self.show_title_screen = True

if __name__ == "__main__":
    PizzaGame()
