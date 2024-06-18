import pyautogui
import time
import numpy as np
import math

def move_cursor_like_person(num_moves: int) -> None:
    # Pre-generate random values for movements
    random_offsets = np.random.randint(-10, 11, size=(num_moves, 2))
    horizontal_offsets = np.vstack(([-10, 0], [10, 0]))
    vertical_offsets = np.vstack(([0, -10], [0, 10]))
    angles = np.random.uniform(0, 2*np.pi, num_moves)
    radii = np.random.randint(5, 21, size=num_moves)
    
    for i in range(num_moves):
        choice: str = np.random.choice(["random", "horizontal", "vertical", "circular"])
        if choice == "random":
            x_offset, y_offset = random_offsets[i]
        elif choice == "horizontal":
            x_offset, y_offset = horizontal_offsets[i % 2]
        elif choice == "vertical":
            x_offset, y_offset = vertical_offsets[i % 2]
        elif choice == "circular":
            x_offset = int(radii[i] * math.cos(angles[i]))
            y_offset = int(radii[i] * math.sin(angles[i]))
        
        pyautogui.move(x_offset, y_offset, duration=np.random.uniform(0.001, 0.05))
        time.sleep(np.random.uniform(0.01, 0.1))
