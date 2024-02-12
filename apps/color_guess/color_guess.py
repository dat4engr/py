import random
from collections import Counter

COLORS = {"R", "G", "B", "Y", "W", "O"}
TRIES = 10
CODE_LENGTH = 4

def generate_code():
    # Generate a random code consisting of CODE_LENGTH number of colors from COLORS.
    return [random.choice(tuple(COLORS)) for _ in range(CODE_LENGTH)]

def guess_code():
    # Prompt the user to guess the code.
    while True:
        try:
            guess = input("Guess: ").upper().split(" ")
            
            if len(guess) != CODE_LENGTH:
                raise ValueError(f"You must guess {CODE_LENGTH} colors.")
            
            if any(color not in COLORS for color in guess):
                raise ValueError(f"Invalid color. Try again.")
            
            break
        
        except ValueError as error:
            print(error)

    return guess

def check_code(guess, real_code):
    # Check the correctness of the guess against the real code.
    color_counts = Counter(real_code)
    correct_position = sum(guess_color == real_color for guess_color, real_color in zip(guess, real_code))
    incorrect_position = sum(guess_color in color_counts and color_counts[guess_color] > 0 for guess_color, real_color in zip(guess, real_code))
    return correct_position, incorrect_position

def play_game():
    while True:
        try:
            code = generate_code()
            # print(f"Demo Mode. Answer Sheet is: {code}")
            print(f"Welcome to Color Guess! You have {TRIES} to guess the code.")
            print("The valid colors are", *COLORS)
            
            for attempts in range(1, TRIES + 1):
                guess = guess_code()
                correct_position, incorrect_position = check_code(guess, code)
                
                if correct_position == CODE_LENGTH:
                    print(f"You guessed the code in {attempts} tries!")
                    break
        
                print(f"Correct Positions: {correct_position} | Incorrect Positions: {incorrect_position}")
        
            else:
                print("You ran out of tries, the code was:", *code)
                
            replay = input("Do you want to play again? (Y/N) ").upper()
            if replay != "Y":
                break
        
        except KeyboardInterrupt:
            print("\nGame ended.")
            break
        except Exception as error:
            print("An error occurred:", error)
            

if __name__ == "__main__":
    play_game()
