import cursor_movement
import user_input

def main() -> None:
    # Main function
    try:
        num_moves: int = user_input.get_user_input()
        cursor_movement.move_cursor_like_person(num_moves)
        print("Cursor movements completed!")
    except ValueError as value_error:
        print(f"An error occurred in user input: {value_error}")
    except Exception as exception:
        print(f"An unexpected error occurred: {exception}")

if __name__ == "__main__":
    main()
