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
        return f"{Fore.WHITE}It's a tie! {emojize(':neutral_face:', use_aliases=True)}{Style.RESET_ALL}"
    elif WINNING_CONDITIONS[player] == computer:
        return f"{Fore.GREEN}You win! {emojize(':smiley:', use_aliases=True)}{Style.RESET_ALL}"
    else:
        return f"{Fore.RED}Computer wins! {emojize(':squinting_face_with_tongue:', use_aliases=True)}{Style.RESET_ALL}"

def play_game():
    # Plays a game of Rock, Paper, Scissors and updates the win count for the player and computer.
    player_choice = get_player_choice()
    computer_choice = generate_computer_choice()

    print(f"You chose {player_choice}, computer chose {computer_choice}")

    result = check_win(player_choice, computer_choice)
    print(result)

    global PLAYER_WINS, COMPUTER_WINS
    if result == f"{Fore.GREEN}You win! {emojize(':smiley:', use_aliases=True)}{Style.RESET_ALL}":
        PLAYER_WINS += 1
    elif result == f"{Fore.RED}Computer wins! {emojize(':disappointed:', use_aliases=True)}{Style.RESET_ALL}":
        COMPUTER_WINS += 1

    print(f"Player wins: {PLAYER_WINS}")
    print(f"Computer wins: {COMPUTER_WINS}")

def main():
    # Controls the flow of the game and allows the player to play multiple rounds.
    play_again = 'yes'
    while play_again.lower() == 'yes':
        play_game()
        play_again = input("Do you want to play again? (yes/no): ").lower()
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    main()
