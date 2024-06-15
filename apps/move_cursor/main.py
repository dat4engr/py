import cursor_movement
import user_input

def main():
    # Main function
    num_moves = user_input.get_user_input()
    cursor_movement.move_cursor_like_person(num_moves)
    print("Cursor movements completed!")

if __name__ == "__main__":
    main()
