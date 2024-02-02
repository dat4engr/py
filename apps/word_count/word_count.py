def word_count(text):
    # Calculates the number of words in a given text.
    count = len(text.split())
    return count

def is_two_words(text):
    words = text.split()
    return len(words) == 2

def is_multiple_words(text):
    # Determines whether the given text consists of multiple words.
    if len(text.split()) > 2:
        return True
    else:
        return False

def main():
    # The main function that runs the app. Prints the welcome message.
    print("Welcome to Word Count App!")

    while True:
        text = input("Enter some text (or 'q' to quit): ")
        if text.lower() == 'q':
            print("Thank you for using Word Count App!")
            break
        else:
            count = word_count(text)
            print("Number of words:", count)
            # Check if input is two words
            if is_two_words(text):
                print("The input text is two words")
            # Check if input is multiple words
            elif is_multiple_words(text):
                print("The input text is multiple words.")
            else:
                print("The input text is a single word.")
            print()

if __name__ == "__main__":
    main()
