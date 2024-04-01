import random
import os

player_wins = 0
computer_wins = 0
options = ["rock", "paper", "scissors"]
winning_conditions = {
    "rock": "scissors",
    "scissors": "paper",
    "paper": "rock"
}

def get_player_choice():
    # Ask the player to input a choice (rock, paper, scissors) and validate the input.
    while True:
        player_choice = input("Enter a choice (rock, paper, scissors): ").lower()
        if player_choice in options:
            return player_choice
        else:
            print("Invalid choice. Please enter rock, paper, or scissors.")

def generate_computer_choice():
    # Randomly selects a choice from the options for the computer.
    return random.choice(options)

def check_win(player, computer):
    # Check who won the game based on player and computer choices.
    if player == computer:
        return "It's a tie!"
    elif winning_conditions[player] == computer:
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

    global player_wins, computer_wins
    if result == "You win!":
        player_wins += 1
    elif result == "Computer wins!":
        computer_wins += 1

    print(f"Player wins: {player_wins}")
    print(f"Computer wins: {computer_wins}")

play_again = 'yes'
while play_again.lower() == 'yes':
    play_game()
    play_again = input("Do you want to play again? (yes/no): ").lower()
    os.system('cls' if os.name == 'nt' else 'clear')
