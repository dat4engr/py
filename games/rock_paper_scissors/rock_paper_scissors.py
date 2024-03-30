import random

def get_choices():
    # Function to take input from the player and generate random choice for the computer.
    options = ["rock", "paper", "scissors"]
    while True:
        player_choice = input("Enter a choice (rock, paper, scissors): ")
        if player_choice in options:
            computer_choice = random.choice(options)
            print(f"You chose {player_choice}, computer chose {computer_choice}")
            return {"player": player_choice, "computer": computer_choice}
        else:
            print("Invalid choice. Please enter rock, paper, or scissors.")

def check_win(player, computer):
    # Function that determines the winner based on the choices made.
    if player == computer:
        return "It's a tie!"
    elif player == "rock":
        if computer == "scissors":
            return "You win!"
        else:
            return "Computer wins!"
    elif player == "paper":
        if computer == "rock":
            return "You win!"
        else:
            return "Computer wins!"
    elif player == "scissors":
        if computer == "paper":
            return "You win!"
        else:
            return "Computer wins!"

choices = get_choices()
result = check_win(choices["player"], choices["computer"])
print(result)
