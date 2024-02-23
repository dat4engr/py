import logging
import multiprocessing
import spacy

def load_spacy_model(model_name):
    # Load a Spacy model with the specified model name.
    try:
        nlp = spacy.load(model_name)
        return nlp
    except OSError as error:
        logging.error(f"Error loading Spacy model: {error}")
        return None
    except Exception as e:
        logging.error(f"An error occurred while loading Spacy model: {e}")
        return None

nlp = load_spacy_model("en_core_web_sm")

if nlp is None:
    logging.error("Spacy model could not be loaded. Exiting program.")
    exit()

def setup_logging(log_file='error.log', log_level=logging.ERROR):
    # Setup logging configuration for the application.
    try:
        logging.basicConfig(filename=log_file, level=log_level)
    except Exception as e:
        logging.error(f"Error setting up logging: {e}")

def word_count(text):
    # Count the number of words in the input text using the loaded Spacy model.
    try:
        doc = nlp(text)
        logging.info(f"Text processed: {text}")
        logging.info(f"Word count: {len(doc)}")
        return len(doc)
    except Exception as e:
        logging.error(f"An error occurred while counting words: {e}")
        return 0

def word_type(text):
    try:
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
    except Exception as e:
        logging.error(f"An error occurred while determining word type: {e}")
        return "unknown"

def validate_word(text):
    try:
        doc = nlp(text)
        for token in doc:
            if not token.is_alpha and not token.text in [' ', '-']:
                logging.error(f"Invalid input: {text}, contains non-alphabetic characters.")
                return False
        return True
    except Exception as e:
        logging.error(f"An error occurred while validating word: {e}")
        return False

def get_user_input():
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
    try:
        print(f"Number of words: {count}")
    except Exception as e:
        logging.error(f"An error occurred while displaying word count: {e}")

def display_word_type(word_type_text):
    try:
        if word_type_text == "two":
            print("The input text is two words.")
        elif word_type_text == "multiple":
            print("The input text is multiple words.")
        else:
            print("The input text is a single word.")
    except Exception as e:
        logging.error(f"An error occurred while displaying word type: {e}")

def process_text(input_text):
    try:
        doc = nlp(input_text)
        word_count = len(doc)

        # Count specific types of words
        nouns = [token.text for token in doc if token.pos_ == 'NOUN']
        verbs = [token.text for token in doc if token.pos_ == 'VERB']
        adjectives = [token.text for token in doc if token.pos_ == 'ADJ']

        # Analyzing sentence structure
        sentence_structure = {}
        for sent in doc.sents:
            for token in sent:
                if token.dep_ in sentence_structure:
                    sentence_structure[token.dep_] += 1
                else:
                    sentence_structure[token.dep_] = 1

        # Providing suggestions for improving text readability
        readability_suggestions = []
        if word_count > 20:
            readability_suggestions.append("Consider breaking down the text into shorter sentences.")

        # Display the results
        print(f"Number of words: {word_count}")
        print(f"Nouns: {nouns}")
        print(f"Verbs: {verbs}")
        print(f"Adjectives: {adjectives}")
        print(f"Sentence Structure: {sentence_structure}")
        print("Readability Suggestions:")
        for suggestion in readability_suggestions:
            print(suggestion)
    except Exception as e:
        logging.error(f"An error occurred while processing text: {e}")


def main():
    try:
        setup_logging(log_file='error.log', log_level=logging.ERROR)
        print("Welcome to Word Count App!")

        while True:
            text = get_user_input()

            if text == 'q':
                break

            logging.info(f"Processing text: {text}")

            with multiprocessing.Pool() as pool:
                result = pool.apply_async(process_text, (text,))
                result.get()

            print()
    except Exception as e:
        logging.error(f"An error occurred in the main function: {e}")

if __name__ == "__main__":
    main()
