import display, keypad, time
import sndmixer
import random

vol = 255  # Sound volume level
on = 0xFF0000  # Red color for "bomb" (can be any color code)
off = 0x000000  # No light

sndmixer.begin(16)
channels = [None] * 16

# Game state variables
active_bombs = []  # List to track active bomb positions
time_limit = 1200  # 2 seconds for bomb expiration
initial_bomb_interval = 1200  # Initial bomb planting interval (in ms)
bomb_interval = initial_bomb_interval  # Current bomb planting interval
interval_decrease = 30  # Amount to decrease interval after each bomb
min_bomb_interval = 200  # Minimum interval for bomb planting
game_over = False
score = 0
last_bomb_time = 0  # Track when the last bomb was planted

def reset_game():
    global active_bombs, game_over, score, bomb_interval
    active_bombs = []
    game_over = False
    score = 0
    bomb_interval = initial_bomb_interval  # Reset the interval
    display.drawFill(off)
    display.flush()

def plant_bomb():
    """Plant a bomb at a random position that isn't already active."""
    global active_bombs, last_bomb_time
    
    # Find an empty spot for the new bomb
    available_positions = [i for i in range(16) if i not in active_bombs]
    
    if available_positions:
        bomb_position = random.choice(available_positions)
        active_bombs.append(bomb_position)
        x, y = bomb_position % 4, int(bomb_position / 4)
        display.drawPixel(x, y, on)  # Draw the bomb on the display
        display.flush()
        
        last_bomb_time = time.ticks_ms()  # Update the last bomb time

def play_tone(frequency, duration_ms):
    """Plays a tone for the given duration."""
    synth = sndmixer.synth()
    sndmixer.volume(synth, vol)
    sndmixer.waveform(synth, 0)  # Using a basic waveform (0: sine wave)
    sndmixer.freq(synth, frequency)
    sndmixer.play(synth)
    
    # Delay for the duration to let the tone play
    time.sleep_ms(duration_ms)
    
    sndmixer.stop(synth)

def on_key(key_index, pressed):
    global game_over, score, active_bombs
    
    if game_over:
        # If the game is over, reset the game if any key is pressed
        if pressed:
            reset_game()
        return

    if pressed:
        if key_index in active_bombs:  # Player hit an active bomb!
            # Play success sound
            play_tone(440, 200)
            
            # Remove the bomb from the active list
            active_bombs.remove(key_index)
            x, y = key_index % 4, int(key_index / 4)
            display.drawPixel(x, y, off)  # Clear the bomb from display
            display.flush()
            
            # Update score
            score += 1
            
            # Decrease the bomb interval (to make game harder)
            global bomb_interval
            bomb_interval = max(min_bomb_interval, bomb_interval - interval_decrease)
        else:
            # Wrong button - game over
            game_over = True
            display.flush()
            print("Game Over! Score:", score)
            # Play game over sound
            play_tone(220, 500)

# Set up the initial game state
reset_game()
plant_bomb()  # Plant the first bomb
keypad.add_handler(on_key)

# Main loop for bomb timing and handling
while True:
    if not game_over:
        # Plant a new bomb if the interval has passed
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, last_bomb_time) > bomb_interval:
            plant_bomb()
        
        # Check if any bombs have expired
        expired_bombs = []
        for bomb_position in active_bombs:
            bomb_time = time.ticks_diff(current_time, last_bomb_time)
            if bomb_time > time_limit:
                expired_bombs.append(bomb_position)
        
        # If any bombs expired, trigger game over
        if expired_bombs:
            game_over = True
            display.flush()
            print("Time ran out! Game Over! Score:", score)
            play_tone(220, 500)  # Lower tone for failure
        
    time.sleep_ms(50)  # Small delay to avoid maxing out CPU
