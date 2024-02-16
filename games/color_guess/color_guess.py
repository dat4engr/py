import random

class ColorGuess:
    COLORS = {"R", "G", "B", "Y", "W", "O"}
    CODE_LENGTH = 4
    
    def __init__(self):
        self.code = self.generate_code()
        self.score = 0

    def generate_code(self):
        return [random.choice(tuple(self.COLORS)) for _ in range(self.CODE_LENGTH)]

    def guess_code(self):
        while True:
            try:
                user_guess = self.get_valid_guess()
                break

            except ValueError as error:
                print(error)

        return user_guess

    def get_valid_guess(self):
        user_guess = input("Guess: ").upper().split(" ")

        if len(user_guess) != self.CODE_LENGTH:
            raise ValueError(f"You must guess {self.CODE_LENGTH} colors.")

        if any(color not in self.COLORS for color in user_guess):
            raise ValueError(f"Invalid color. Try again.")

        return user_guess

    def evaluate_guess(self, user_guess):
        color_counts = {color: self.code.count(color) for color in self.COLORS}
        correct_position = sum(guess_color == real_color for guess_color, real_color in zip(user_guess, self.code))
        incorrect_position = sum(guess_color in color_counts and color_counts[guess_color] > 0 for guess_color in user_guess)
        return correct_position, incorrect_position

    def play_game(self):
        while True:
            print(f"Welcome to Color Guess! You have {self.TRIES} to guess the code.")
            # print(f"Demo Mode. Answer Sheet is: {self.code}")
            print("The valid colors are", *self.COLORS)

            try:
                tries = self.get_valid_integer_input("Enter the number of tries: ")
            except ValueError as error:
                print(error)
                continue

            self.TRIES = tries

            for attempts in range(1, self.TRIES + 1):
                user_guess = self.guess_code()
                correct_position, incorrect_position = self.evaluate_guess(user_guess)

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

    def get_valid_integer_input(self, message):
        while True:
            try:
                value = int(input(message))
                return value
            except ValueError:
                print("Invalid input. Enter an integer.")

if __name__ == "__main__":
    game = ColorGuess()
    game.play_game()
