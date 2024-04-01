import random
import os

PLAYER_WINS = 0
COMPUTER_WINS = 0
OPTIONS = ["rock", "paper", "scissors"]
WINNING_CONDITIONS = {
    "rock": "scissors",
    "scissors": "paper",
    "paper": "rock"
}

def get_player_choice():
    # Ask the player to input a choice (rock, paper, scissors) and validate the input.
    while True:
        player_choice = input("Enter a choice (rock, paper, scissors): ").lower()
        if player_choice in OPTIONS:
            return player_choice
        else:
            print("Invalid choice. Please enter rock, paper, or scissors.")

def generate_computer_choice():
    # Randomly selects a choice from the options for the computer.
    return random.choice(OPTIONS)

def check_win(player, computer):
    # Check who won the game based on player and computer choices.
    if player == computer:
        return "It's a tie!"
    elif WINNING_CONDITIONS[player] == computer:
        return "You win!"
    else:
        return "Computer wins!"

def play_game():
    # Play a game of Rock, Paper, Scissors.
    player_choice = get_player_choice()
    computer_choice = generate_computer_choice()

    print(f"You chose {player_choice}, computer chose {computer_choice}")

    result = check_win(player_choice, computer_choice)
    print(result)

    global PLAYER_WINS, COMPUTER_WINS
    if result == "You win!":
        PLAYER_WINS += 1
    elif result == "Computer wins!":
        COMPUTER_WINS += 1

    print(f"Player wins: {PLAYER_WINS}")
    print(f"Computer wins: {COMPUTER_WINS}")

def main():
    play_again = 'yes'
    while play_again.lower() == 'yes':
        play_game()
        play_again = input("Do you want to play again? (yes/no): ").lower()
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    main()
