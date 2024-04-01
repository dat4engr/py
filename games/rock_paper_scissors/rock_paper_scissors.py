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
    player_choice = input("Enter a choice (rock, paper, scissors): ")
    while player_choice not in options:
        print("Invalid choice. Please enter rock, paper, or scissors.")
        player_choice = input("Enter a choice (rock, paper, scissors): ")
    return player_choice

def generate_computer_choice():
    return random.choice(options)

def check_win(player, computer):
    if player == computer:
        return "It's a tie!"
    elif winning_conditions[player] == computer:
        return "You win!"
    else:
        return "Computer wins!"

def play_game():
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
    play_again = input("Do you want to play again? (yes/no): ")
    os.system('cls' if os.name == 'nt' else 'clear')
