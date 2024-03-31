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

def get_choices():
    # Function to take input from the player and generate random choice for the computer.
    player_choice = input("Enter a choice (rock, paper, scissors): ")
    while player_choice not in options:
        print("Invalid choice. Please enter rock, paper, or scissors.")
        player_choice = input("Enter a choice (rock, paper, scissors): ")
    
    computer_choice = random.choice(options)
    print(f"You chose {player_choice}, computer chose {computer_choice}")
    
    return {"player": player_choice, "computer": computer_choice}

def check_win(player, computer):
    # Function that determines the winner based on the choices made.
    if player == computer:
        return "It's a tie!"
    elif winning_conditions[player] == computer:
        return "You win!"
    else:
        return "Computer wins!"

play_again = 'yes'

while play_again.lower() == 'yes':
    choices = get_choices()
    result = check_win(choices["player"], choices["computer"])
    print(result)

    if result == "You win!":
        player_wins += 1
    elif result == "Computer wins!":
        computer_wins += 1

    print(f"Player wins: {player_wins}")
    print(f"Computer wins: {computer_wins}")

    play_again = input("Do you want to play again? (yes/no): ")
    os.system('cls' if os.name == 'nt' else 'clear')
