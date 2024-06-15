def get_user_input():
    # Function to get user input for the number of cursor moves
    while True:
        try:
            num_moves = int(input("Enter the number of cursor moves you want to make (positive integer that is greater than 0): "))
            if num_moves <= 0:
                print("Please enter a positive integer greater than 0.")
                continue
            return num_moves
        except ValueError:
            print("Invalid input. Please enter a positive integer.")
        except KeyboardInterrupt:
            print("\nExiting program.")
            exit()
