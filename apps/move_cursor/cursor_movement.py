import pyautogui
import time
import numpy as np
import math

def move_cursor_like_person(num_moves: int) -> None:
    # Function to move mouse cursor like a regular person
    for _ in range(num_moves):
        choice: str = np.random.choice(["random", "horizontal", "vertical", "circular"])
        if choice == "random":
            x_offset: int = np.random.randint(-10, 11)  # 11 to include upper bound
            y_offset: int = np.random.randint(-10, 11)
        elif choice == "horizontal":
            x_offset: int = np.random.choice([-10, 11])  # 11 is exclusive
            y_offset: int = 0
        elif choice == "vertical":
            x_offset: int = 0
            y_offset: int = np.random.choice([-10, 11])
        elif choice == "circular":
            angle: float = np.random.uniform(0, 2*np.pi)
            radius: int = np.random.randint(5, 21)  # 21 to include upper bound
            x_offset: int = int(radius * math.cos(angle))
            y_offset: int = int(radius * math.sin(angle))
        pyautogui.move(x_offset, y_offset, duration=np.random.uniform(0.001, 0.05))
        time.sleep(np.random.uniform(0.01, 0.1))
