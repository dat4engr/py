from colorama import Fore, Style
import random
import os
from emoji import emojize

PLAYER_WINS = 0
COMPUTER_WINS = 0
OPTIONS = ["rock", "paper", "scissors"]
WINNING_CONDITIONS = {
    "rock": "scissors",
    "scissors": "paper",
    "paper": "rock"
}

class GameResult:
    Tie = 0
    PlayerWins = 1
    ComputerWins = 2

def get_player_choice():
    # Ask the player to input a choice (rock, paper, scissors) and validate the input.
    while True:
        try:
            player_choice = input("Enter a choice (rock, paper, scissors): ").lower()
            if player_choice in OPTIONS:
                return player_choice
            else:
                print("Invalid choice. Please enter rock, paper, or scissors.")
        except KeyboardInterrupt:
            response = input("\nGame interrupted. Do you want to continue playing? (yes/no): ")
            if response.lower() in ['no', 'n']:
                exit()
            else:
                print("Resuming the game...")
                continue

def generate_computer_choice():
    # Randomly selects a choice from the options for the computer.
    return random.choice(OPTIONS)

def check_win(player, computer):
    # Check who won the game based on player and computer choices.
    if player == computer:
        return GameResult.Tie
    elif WINNING_CONDITIONS[player] == computer:
        return GameResult.PlayerWins
    else:
        return GameResult.ComputerWins

def play_game():
    # Plays a game of Rock, Paper, Scissors and updates the win count for the player and computer.
    try:
        player_choice = get_player_choice()
        computer_choice = generate_computer_choice()

        print(f"You chose {player_choice}, computer chose {computer_choice}")

        result = check_win(player_choice, computer_choice)
        print_result(result)

        global PLAYER_WINS, COMPUTER_WINS
        update_score(result)

        print(f"Player wins: {PLAYER_WINS}")
        print(f"Computer wins: {COMPUTER_WINS}")
    except KeyboardInterrupt:
        response = input("\nGame interrupted. Do you want to continue playing? (yes/no): ")
        if response.lower() in ['no', 'n']:
            exit()
        else:
            print("Resuming the game...")

def update_score(result):
    # Update the score based on the result of the game.
    global PLAYER_WINS, COMPUTER_WINS
    if result == GameResult.PlayerWins:
        PLAYER_WINS += 1
    elif result == GameResult.ComputerWins:
        COMPUTER_WINS += 1

def print_result(result):
    # Print the result of the game based on the GameResult enum value.
    if result == GameResult.Tie:
        print(f"{Fore.WHITE}It's a tie! {emojize(':neutral_face:', use_aliases=True)}{Style.RESET_ALL}")
    elif result == GameResult.PlayerWins:
        print(f"{Fore.GREEN}You win! {emojize(':smiley:', use_aliases=True)}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Computer wins! {emojize(':squinting_face_with_tongue:', use_aliases=True)}{Style.RESET_ALL}")

def main():
    # Controls the flow of the game and allows the player to play multiple rounds.
    play_again = 'yes'
    rounds_to_play = get_rounds_to_play()

    current_round = 0
    while (play_again.lower() in ['yes', 'y']) and (current_round != rounds_to_play):
        play_game()
        current_round += 1

        if rounds_to_play != -1 and current_round == rounds_to_play:
            print(f"Reached the specified number of rounds ({rounds_to_play}). Game over.")
            break

        play_again = input("Do you want to play again? (yes/no): ").lower()

        while play_again.lower() not in ['yes', 'no', 'y', 'n']:
            play_again = input("Invalid response. Do you want to play again? (yes/no): ").lower()

        if play_again.lower() in ['yes', 'y']:
            clear_screen()

def get_rounds_to_play():
    # Get the number of rounds the player wants to play.
    try:
        return int(input("Enter the number of rounds you want to play (enter -1 for unlimited rounds): "))
    except ValueError:
        print("Invalid input. Playing unlimited rounds.")
        return -1

def clear_screen():
    # Clears the screen of the terminal window.
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        response = input("\nGame interrupted. Do you want to continue playing? (yes/no): ")
        if response.lower() in ['no', 'n']:
            exit()
