import pyautogui
import time
import random

def move_cursor_like_person(num_moves):
  # Function to move mouse cursor like a regular person
    for _ in range(num_moves):
        x_offset = random.randint(-10, 10)
        y_offset = random.randint(-10, 10)
        pyautogui.move(x_offset, y_offset, duration=random.uniform(0.001, 0.05)) # Decreased duration for faster movement
        time.sleep(random.uniform(0.01, 0.1))

def main():
  # Main function
    num_moves = int(input("Enter the number of cursor moves you want to make: "))
    move_cursor_like_person(num_moves)
    print("Cursor movements completed!")

if __name__ == "__main__":
    main()
