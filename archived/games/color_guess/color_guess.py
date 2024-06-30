import random

class ColorGuess:
    COLORS = {"R", "G", "B", "Y", "W", "O"}
    MAX_TRIES = 10
    CODE_LENGTH = 4

    def __init__(self):
        self.code = self.generate_code()
        self.score = 0

    def generate_code(self):
        # Generates a random code using colors from a specified set.
        return random.choices(tuple(self.COLORS), k=self.CODE_LENGTH)

    def get_guess(self):
        # Prompts the user to enter a guess and validates the input.
        while True:
            try:
                guess = input("Guess: ").upper().split(" ")

                if len(guess) != self.CODE_LENGTH:
                    raise ValueError(f"You must guess {self.CODE_LENGTH} colors.")

                if any(color not in self.COLORS for color in guess):
                    raise ValueError(f"Invalid color. Try again.")

                return guess

            except ValueError as error:
                print(error)

    def check_guess(self, guess):
        # Compares the user's guess with the actual code to determine correct and incorrect positions.
        colors_count = {color: self.code.count(color) for color in self.COLORS}
        correct_position = sum(guess_color == real_color for guess_color, real_color in zip(guess, self.code))
        incorrect_position = sum(guess_color in colors_count and colors_count[guess_color] > 0 for guess_color in guess)
        return correct_position, incorrect_position

    def end_game(self):
        # Displays the player's final score and prompts for a replay option.
        print(f"Your score is: {self.score}")
        replay = input("Do you want to play again? (Y/N) ").upper()
        return replay == "Y"

    def play_game(self):
        # Implements the main game loop where the user can make multiple attempts to guess the code.
        while True:
            try:
                print(f"Welcome to Color Guess! You have {self.MAX_TRIES} tries to guess the code.")
                # print(f"Demo Mode. Answer Sheet is: {self.code}")
                print("The valid colors are", *self.COLORS)

                for attempts in range(1, self.MAX_TRIES + 1):
                    guess = self.get_guess()
                    correct_position, incorrect_position = self.check_guess(guess)

                    if correct_position == self.CODE_LENGTH:
                        print(f"You guessed the code in {attempts} tries!")
                        self.score += 1
                        break

                    print(f"Correct Positions: {correct_position} | Incorrect Positions: {incorrect_position}")

                else:
                    print("You ran out of tries, the code was:", *self.code)

                if not self.end_game():
                    break

            except KeyboardInterrupt:
                print("\nGame ended.")
                break
            except Exception as error:
                print("An error occurred:", error)


if __name__ == "__main__":
    # Instantiate the  class and call the method to start playing the color guessing game.
    game = ColorGuess()
    game.play_game()
