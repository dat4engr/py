import logging
from nltk.corpus import words

# Set up logging configuration
logging.basicConfig(filename='error.log', level=logging.ERROR)

def word_count(text):
# Calculates the number of words in a given text.
    try:
        count = len(text.split())
        return count
    except Exception as e:
        logging.error(f"Error in word_count function: {e}")
        raise

def word_type(text):
# Determines whether the given text consists of multiple words.
    try:
        words = text.split()
        num_words = len(words)

        if num_words == 2:
            return "two"
        elif num_words > 2:
            return "multiple"
        else:
            return "single"
    except Exception as e:
        logging.error(f"Error in word_type function: {e}")
        raise

def validate_word(text):
    try:
        english_words = set(words.words())
        words_to_validate = text.split()

        for word in words_to_validate:
            if word.lower() not in english_words:
                return False

        return True
    except Exception as e:
        logging.error(f"Error in validate_word function: {e}")
        raise

def get_user_input():
    while True:
        try:
            text = input("Enter some text (or 'q' to quit): ").lower()
            if text == 'q':
                return text
            elif text.strip() != "" and validate_word(text):
                return text
            else:
                raise ValueError
        except ValueError:
            logging.error(f"Invalid input {text}. Please enter a valid English word or 'q' to quit.")
            print("Invalid input. Please enter a valid English word or 'q' to quit.")   

def main():
# The main function that runs the app. Prints the welcome message.
    print("Welcome to Word Count App!")

    while True:
        text = get_user_input()

        if text == 'q':
            break

        count = word_count(text)
        word_type_text = word_type(text)

        display_count(count)
        display_word_type(word_type_text)

        print()

def display_count(count):
    print(f"Number of words: {count}")

def display_word_type(word_type_text):
    if word_type_text == "two":
        print("The input text is two words.")
    elif word_type_text == "multiple":
        print("The input text is multiple words.")
    else:
        print("The input text is a single word.")

if __name__ == "__main__":
    main()
