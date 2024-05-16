import logging
import spacy
from spacy.errors import Errors
import re

logger = logging.getLogger(__name__)
nlp = None

class SpacyModelError(Exception):
    pass

class InputValidationError(Exception):
    pass

def initialize_logger():
    # Initialize the logger with timestamp and format.
    logging.basicConfig(filename='error.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_spacy_model(model_name):
    # Function to load a Spacy model based on the given model_name.
    global nlp
    if nlp is None:
        try:
            nlp = spacy.load(model_name)
            logger.info(f"Spacy model loaded successfully: {model_name}")
        except OSError as error:
            logger.error(f"Failed to load Spacy model: {error}")
            raise SpacyModelError("Failed to load Spacy model")
    return nlp

def validate_word(text, nlp):
    # Validate the input text to ensure it is a valid English word.
    try:
        if text is None or not isinstance(text, str) or not text or not re.match("^[a-zA-Z -]*$", text):
            raise InputValidationError("Invalid input")
        
        doc = nlp(text)
        return all(token.is_alpha or token.text in [' ', '-'] for token in doc)
    except InputValidationError as error:
        logger.error(f"Invalid input: {error}")
        return False
    except Exception as error:
        logger.error(f"Failed to validate input word: {error}")
        return False

def get_user_input():
    # Get user input and validate it using the Spacy model.
    model_name = "en_core_web_sm"  # Load model only once
    try:
        nlp = load_spacy_model(model_name)
    except SpacyModelError as error:
        logger.error(f"{error}. Exiting program.")
        return

    while True:
        text = input("Enter a word or sentence (or 'q' to quit): ").lower()
        if text == 'q':
            return text

        text = text.strip()
        if not text:
            logger.warning("Empty input. Please enter a valid English word or sentence or 'q' to quit.")
            print("Empty input. Please enter a valid English word or sentence or 'q' to quit.")
            continue

        if validate_word(text, nlp):
            return text
        else:
            logger.warning(f"Invalid input: {text}. Please enter a valid English word or 'q' to quit.")
            print("Invalid input. Please enter a valid English word or sentence or 'q' to quit.")

def word_type(token):
    # Determine the word type (Noun, Verb, Adjective, Preposition) for a given token.
    word_types_mapping = {'NOUN', 'VERB', 'ADJ', 'ADV', 'ADP', 'CONJ', 'PRON', 'DET', 'SCONJ', 'INTJ', 'NUM', 'SYM', 'X'}
    special_prepositions = {'about', 'above', 'across'}
    
    if token.pos_ == 'ADP' and token.text.lower() in special_prepositions:
        return 'Complex Preposition'
    
    return token.pos_ if token.pos_ in word_types_mapping else 'Other'

def process_text(input_text, nlp):
    # Process the input text using the Spacy model and print relevant information.
    try:
        doc = nlp(input_text)
        word_count = len(doc)
        
        word_types = {wt: [token.text for token in doc if word_type(token) == wt] for wt in set(word_type(token) for token in doc)}
        
        sentence_structure = {}
        for sent in doc.sents:
            for token in sent:
                sentence_structure[token.dep_] = sentence_structure.get(token.dep_, 0) + 1
                
        readability_suggestions = ["Consider breaking down the text into shorter sentences."] if word_count > 20 else []

        print(f"Number of words: {word_count}")
        for wt, words in word_types.items():
            print(f"{wt}s: {words}")
        print(f"Sentence Structure: {sentence_structure}")
        print("Readability Suggestions:")
        for suggestion in readability_suggestions:
            print(suggestion)
    except (OSError, Errors) as error:
        logger.error(f"An error occurred while processing text: {error}")
    except Exception as error:
        logger.error(f"An unexpected error occurred while processing text: {error}")

def main():
    # The main function to run the Word Count App and handle user input.
    try:
        initialize_logger()
        print("Welcome to the Word Count App!")

        while True:
            text = get_user_input()

            if text == 'q':
                break

            try:
                model_name = "en_core_web_sm"  # You can change the model name here
                nlp = load_spacy_model(model_name)
            except SpacyModelError as error:
                logger.error(f"{error}. Exiting program.")
                exit()

            process_text(text, nlp)
            print()

    except (OSError, Errors) as error:
        logger.error(f"An error occurred in the main function: {error}", exc_info=True)
    except Exception as error:
        logger.error(f"An unexpected error occurred in the main function: {error}", exc_info=True)

if __name__ == "__main__":
    main()
