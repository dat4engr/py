import logging
import multiprocessing
import spacy

def load_spacy_model(model_name):
    try:
        nlp = spacy.load(model_name)
        return nlp
    except OSError as error:
        logging.error(f"Error loading Spacy model: {error}")
        return None

nlp = load_spacy_model("en_core_web_sm")

if nlp is None:
    logging.error("Spacy model could not be loaded. Exiting program.")
    exit()

def setup_logging(log_file='error.log', log_level=logging.ERROR):
    # Set up logging configuration with specified log file and log level.
    logging.basicConfig(filename=log_file, level=log_level)

def word_count(text):
    # Count the number of words in the input text.
    doc = nlp(text)
    logging.info(f"Text processed: {text}")
    logging.info(f"Word count: {len(doc)}")
    return len(doc)

def word_type(text):
    # Determine the word type of the input text: single, two, or multiple.
    doc = nlp(text)
    number_of_words = len(doc)

    if number_of_words == 2:
        word_type_text = "two"
    elif number_of_words > 2:
        word_type_text = "multiple"
    else:
        word_type_text = "single"
    logging.info(f"Word type: {word_type_text}")
    return word_type_text

def validate_word(text):
    # Validate if all tokens in the input text are alphabetic.
    doc = nlp(text)
    for token in doc:
        if not token.is_alpha:
            logging.error(f"Invalid input: {text}")
            return False
    return True

def get_user_input():
    # Get user input text continuously until a valid English word or 'q' to quit is entered.
    text = ""
    
    while text != 'q':
        text = input("Enter some text (or 'q' to quit): ").lower()

        if text == 'q':
            return text

        if text.strip() != "" and validate_word(text):
            return text
        else:
            logging.error(f"Invalid input {text}. Please enter a valid English word or 'q' to quit.")
            print("Invalid input. Please enter a valid English word or 'q' to quit.")

def display_count(count):
    """
    Display the number of words in the input text.

    :param count: Number of words
    """
    print(f"Number of words: {count}")

def display_word_type(word_type_text):
    # Display the word type (single, two, or multiple) of the input text.
    if word_type_text == "two":
        print("The input text is two words.")
    elif word_type_text == "multiple":
        print("The input text is multiple words.")
    else:
        print("The input text is a single word.")

def process_text(input_text):
    # Process the input text by getting word count and word type, and display the results.
    count = word_count(input_text)
    word_type_text = word_type(input_text)
    display_count(count)
    display_word_type(word_type_text)

def main():
    # Main function to run the Word Count App.
    setup_logging(log_file='error.log', log_level=logging.ERROR)
    print("Welcome to Word Count App!")

    while True:
        text = get_user_input()

        if text == 'q':
            break

        logging.info(f"Processing text: {text}")

        # Use multiprocessing to process the text simultaneously
        with multiprocessing.Pool() as pool:
            result = pool.apply_async(process_text, (text,))
            result.get()

        print()

if __name__ == "__main__":
    main()
