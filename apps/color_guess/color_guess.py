import random

class ColorGuess:
    COLORS = {"R", "G", "B", "Y", "W", "O"}
    TRIES = 10
    CODE_LENGTH = 4
    
    def __init__(self):
        self.code = self.generate_code()
        self.score = 0
    
    def generate_code(self):
        # Generate a random code consisting of CODE_LENGTH number of colors from COLORS.
        return [random.choice(tuple(self.COLORS)) for _ in range(self.CODE_LENGTH)]
    
    def guess_code(self):
        # Prompt the user to guess the code.
        while True:
            try:
                guess = input("Guess: ").upper().split(" ")

                if len(guess) != self.CODE_LENGTH:
                    raise ValueError(f"You must guess {self.CODE_LENGTH} colors.")

                if any(color not in self.COLORS for color in guess):
                    raise ValueError(f"Invalid color. Try again.")

                break

            except ValueError as error:
                print(error)

        return guess
    
    def check_code(self, guess):
        # Check the correctness of the guess against the real code.
        color_counts = {color: self.code.count(color) for color in self.COLORS}
        correct_position = sum(guess_color == real_color for guess_color, real_color in zip(guess, self.code))
        incorrect_position = sum(guess_color in color_counts and color_counts[guess_color] > 0 for guess_color in guess)
        return correct_position, incorrect_position
    
    def play_game(self):
        
        while True:
            try:
                print(f"Welcome to Color Guess! You have {self.TRIES} to guess the code.")
                # print(f"Demo Mode. Answer Sheet is: {self.code}")
                print("The valid colors are", *self.COLORS)

                for attempts in range(1, self.TRIES + 1):
                    guess = self.guess_code()
                    correct_position, incorrect_position = self.check_code(guess)

                    if correct_position == self.CODE_LENGTH:
                        print(f"You guessed the code in {attempts} tries!")
                        self.score += 1
                        break

                    print(f"Correct Positions: {correct_position} | Incorrect Positions: {incorrect_position}")

                else:
                    print("You ran out of tries, the code was:", *self.code)

                print("Your score is:", self.score)

                replay = input("Do you want to play again? (Y/N) ").upper()
                if replay != "Y":
                    break

            except KeyboardInterrupt:
                print("\nGame ended.")
                break
            except Exception as error:
                print("An error occurred:", error)

if __name__ == "__main__":
    game = ColorGuess()
    game.play_game()
