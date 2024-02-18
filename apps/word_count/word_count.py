import logging
from nltk.corpus import words
import multiprocessing

# Set up logging configuration with parameters
def setup_logging(log_file='error.log', log_level=logging.ERROR):
    logging.basicConfig(filename=log_file, level=log_level)

def word_count(text):
    try:
        count = len(text.split())
        return count
    except Exception as error:
        logging.error(f"Error in word_count function: {error}")
        raise

def word_type(text):
    try:
        words = text.split()
        number_of_words = len(words)

        if number_of_words == 2:
            return "two"
        elif number_of_words > 2:
            return "multiple"
        else:
            return "single"
    except Exception as error:
        logging.error(f"Error in word_type function: {error}")
        raise

def validate_word(text):
    try:
        english_words = set(words.words())
        words_to_validate = text.split()

        for word in words_to_validate:
            if word.lower() not in english_words:
                return False

        return True
    except Exception as error:
        logging.error(f"Error in validate_word function: {error}")
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

def display_count(count):
    print(f"Number of words: {count}")

def display_word_type(word_type_text):
    if word_type_text == "two":
        print("The input text is two words.")
    elif word_type_text == "multiple":
        print("The input text is multiple words.")
    else:
        print("The input text is a single word.")

def process_text(input_text):
    count = word_count(input_text)
    word_type_text = word_type(input_text)
    display_count(count)
    display_word_type(word_type_text)

def main():
    setup_logging(log_file='error.log', log_level=logging.ERROR)
    print("Welcome to Word Count App!")

    while True:
        text = get_user_input()

        if text == 'q':
            break

        # Use multiprocessing to process the text simultaneously
        with multiprocessing.Pool() as pool:
            result = pool.apply_async(process_text, (text,))
            result.get()

        print()

if __name__ == "__main__":
    main()
