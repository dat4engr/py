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
        try:
            player_choice = input("Enter a choice (rock, paper, scissors): ").lower()
            if player_choice in OPTIONS:
                return player_choice
            else:
                print("Invalid choice. Please enter rock, paper, or scissors.")
        except KeyboardInterrupt:
            print("\nGame interrupted. Exiting game.")
            exit()

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
    try:
        player_choice = get_player_choice()
        computer_choice = generate_computer_choice()

        print(f"You chose {player_choice}, computer chose {computer_choice}")

        result = check_win(player_choice, computer_choice)
        print(result)

        global PLAYER_WINS, COMPUTER_WINS
        if result == f"{Fore.GREEN}You win! {emojize(':smiley:', use_aliases=True)}{Style.RESET_ALL}":
            PLAYER_WINS += 1
        elif result == f"{Fore.RED}Computer wins! {emojize(':squinting_face_with_tongue:', use_aliases=True)}{Style.RESET_ALL}":
            COMPUTER_WINS += 1

        print(f"Player wins: {PLAYER_WINS}")
        print(f"Computer wins: {COMPUTER_WINS}")
    except KeyboardInterrupt:
        print("\nGame interrupted. Exiting game.")
        exit()

def main():
    # Controls the flow of the game and allows the player to play multiple rounds.
    play_again = 'yes'
    rounds_to_play = -1  # Set default value to play an unlimited number of rounds

    try:
        rounds_to_play = int(input("Enter the number of rounds you want to play (enter -1 for unlimited rounds): "))
    except ValueError:
        print("Invalid input. Playing unlimited rounds.")
    
    current_round = 0
    while (play_again.lower() == 'yes') and (current_round != rounds_to_play):
        play_game()
        current_round += 1

        if rounds_to_play != -1 and current_round == rounds_to_play:
            print(f"Reached the specified number of rounds ({rounds_to_play}). Game over.")
            break

        try:
            play_again = input("Do you want to play again? (yes/no): ").lower()
            os.system('cls' if os.name == 'nt' else 'clear')
        except KeyboardInterrupt:
            print("\nGame interrupted. Exiting game.")
            exit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGame interrupted. Exiting game.")
        exit()
