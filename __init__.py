import display, keypad, time
import sndmixer
import random

# Constants
VOL = 30  # Sound volume level
GREEN = 0x008800
YELLOW = 0x888800
ORANGE = 0x884700
RED = 0x880000
BRIGHT_PURPLE = 0xFF00FF
OFF = 0x000000  # No light
INITIAL_TIME_LIMIT = 2000  # 2 seconds for bomb expiration
INITIAL_BOMB_INTERVAL = 1200  # Initial bomb planting interval (in ms)
INTERVAL_DECREASER = 0.95
MIN_BOMB_INTERVAL = 100  # Minimum interval for bomb planting
SUCCESS_TONE = 440  # Frequency for success sound
FAILURE_TONE = 330  # Frequency for failure sound

# Color transition thresholds (percentage of time remaining)
COLOR_THRESHOLDS = [
    (0, RED),     # Less than 33% time remaining
    (0.33, ORANGE),     # Less than 33% time remaining
    (0.66, YELLOW),  # Less than 66% time remaining
    (1.00, GREEN)    # Full time remaining
]

class BombGame:
    def __init__(self):
        # Initialize sound
        sndmixer.begin(16)
        self.channels = [None] * 16

        # Game state
        self.active_bombs = {}  # Dictionary to track active bomb positions and their spawn times
        self.last_active_bomb=-1
        self.game_over = False
        self.score = 0
        self.bomb_interval = INITIAL_BOMB_INTERVAL
        self.last_bomb_time = 0

    def reset_game(self):
        """Reset the game state to initial conditions."""
        self.active_bombs.clear()
        self.game_over = False
        self.score = 0
        self.bomb_interval = INITIAL_BOMB_INTERVAL
        self.last_bomb_time = 0
        display.drawFill(OFF)
        display.flush()

    def get_bomb_color(self, elapsed_time):
        """Determine bomb color based on elapsed time."""
        time_ratio = elapsed_time / INITIAL_TIME_LIMIT
        for threshold, color in COLOR_THRESHOLDS:
            if 1 - time_ratio <= threshold:
                return color
        return GREEN

    def update_bomb_colors(self, current_time):
        """Update the color of all active bombs based on their time remaining."""
        for pos, spawn_time in self.active_bombs.items():
            elapsed = time.ticks_diff(current_time, spawn_time)
            color = self.get_bomb_color(elapsed)
            x, y = pos % 4, pos // 4
            display.drawPixel(x, y, color)
        display.flush()

    def plant_bomb(self):
        """Plant a bomb at a random available position."""
        available_positions = [i for i in range(16) if i not in self.active_bombs and i != self.last_active_bomb]

        if available_positions:
            bomb_position = random.choice(available_positions)
            current_time = time.ticks_ms()
            self.active_bombs[bomb_position] = current_time
            x, y = bomb_position % 4, bomb_position // 4
            display.drawPixel(x, y, GREEN)  # Start with green color
            display.flush()
            self.last_bomb_time = current_time

    def play_tone(self, frequency, duration_ms, vol = VOL):
        """Play a tone with the given frequency and duration."""
        synth = sndmixer.synth()
        sndmixer.volume(synth, vol)
        sndmixer.waveform(synth, 0)
        sndmixer.freq(synth, frequency)
        sndmixer.play(synth)
        time.sleep_ms(duration_ms)
        sndmixer.stop(synth)

    def handle_key(self, key_index, pressed):
        """Handle key press events."""
        if self.game_over:
            if pressed:
                self.reset_game()
            return

        if not pressed:
            return

        x, y = key_index % 4, key_index // 4

        if key_index in self.active_bombs:
            del self.active_bombs[key_index]
            self.last_active_bomb = key_index

            display.drawPixel(x, y, OFF)
            display.flush()
            # Successful bomb defusal
            # self.play_tone(SUCCESS_TONE, 90)


            self.score += 1
            # Make game harder
            self.bomb_interval = max(MIN_BOMB_INTERVAL, self.bomb_interval * INTERVAL_DECREASER)
        else:
            display.drawPixel(x, y, BRIGHT_PURPLE)
            display.flush()
            # Wrong button pressed - game over
            self.game_over = True
            self.play_tone(FAILURE_TONE, 1000, vol=VOL*2)
            print("Game Over! Score: " + str(self.score))

    def update(self):
        """Update game state - plant new bombs and check for expired ones."""
        if self.game_over:
            return

        current_time = time.ticks_ms()

        # Plant new bomb if interval has passed
        if time.ticks_diff(current_time, self.last_bomb_time) > self.bomb_interval:
            self.plant_bomb()

        # Update colors of existing bombs
        self.update_bomb_colors(current_time)

        # Check for expired bombs
        expired = [pos for pos, spawn_time in self.active_bombs.items()
                   if time.ticks_diff(current_time, spawn_time) > INITIAL_TIME_LIMIT]

        if expired:
            self.game_over = True
            self.play_tone(FAILURE_TONE, 1000, vol=VOL*2)
            print("Time ran out! Game Over! Score: " + str(self.score))

# Create game instance and set up
game = BombGame()
game.reset_game()
game.plant_bomb()
keypad.add_handler(game.handle_key)


def do_update(arg):
    game.update()

# # Create a Timer object
# interval_timer = Timer(-1)
#
# # Initialize the timer to call the function every 1000 ms (1 second)
# interval_timer.init(period=50, mode=Timer.PERIODIC, callback=do_update)

while True:
    game.update()
    time.sleep_ms(50)