import cursor_movement
import user_input

def main():
    # Main function
    try:
        num_moves = user_input.get_user_input()
        cursor_movement.move_cursor_like_person(num_moves)
        print("Cursor movements completed!")
    except Exception as exception:
        print(f"An error occurred: {exception}")

if __name__ == "__main__":
    main()
