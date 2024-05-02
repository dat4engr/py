import logging
import spacy
from spacy.errors import Errors

logger = logging.getLogger(__name__)

def initialize_logger():
    # Initialize the logger with timestamp and format.
    logging.basicConfig(filename='error.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_spacy_model(model_name):
    # Load a Spacy model with the given model name and cache it.
    try:
        if not hasattr(load_spacy_model, "nlp"):
            load_spacy_model.nlp = spacy.load(model_name)
            logger.info(f"Spacy model loaded successfully: {model_name}")
    except OSError as error:
        logger.error(f"Failed to load Spacy model due to an OSError: {error}")
        load_spacy_model.nlp = None
    except Errors as error:
        logger.error(f"Failed to load Spacy model due to a Spacy Error: {error}")
        load_spacy_model.nlp = None
        
    return load_spacy_model.nlp

def validate_word(text, nlp):
    # Validate the input text to ensure it is a valid English word.
    try:
        if not isinstance(text, str):
            raise ValueError("Input must be a string.")

        if len(text) == 0:
            raise ValueError("Empty input string.")
        
        doc = nlp(text)
        
        if all(token.is_alpha or token.text in [' ', '-'] for token in doc):
            return True
        else:
            logger.error(f"Invalid input: {text}, contains non-alphabetic characters.")
            return False
    except ValueError as error:
        logger.error(f"ValueError occurred while validating word: {error}")
        return False
    except OSError as error:
        logger.error(f"OSError occurred while validating word: {error}")
        return False
    except Errors as error:
        logger.error(f"Spacy Error occurred while validating word: {error}")
        return False

def get_user_input():
    # Get user input and validate it using the Spacy model.
    text = ""
    nlp = load_spacy_model("en_core_web_sm")

    if nlp is None:
        logger.error("Failed to load Spacy model. Exiting program.")
        exit()

    while text != 'q':
        text = input("Enter a word or sentence (or 'q' to quit): ").lower()

        if text == 'q':
            return text

        if text.strip() != "" and validate_word(text, nlp):
            return text
        else:
            logger.warning(f"Invalid input: {text}. Please enter a valid English word or 'q' to quit.")
            print("Invalid input. Please enter a valid English word or sentence or 'q' to quit.")

def word_type(token):
    # Determine the word type (Noun, Verb, Adjective, Preposition) for a given token.
    if token.pos_ == 'NOUN':
        return 'Noun'
    elif token.pos_ == 'VERB':
        return 'Verb'
    elif token.pos_ == 'ADJ':
        return 'Adjective'
    elif token.pos_ == 'ADP':
        if any(token.text.lower() == preposition.lower() for preposition in ['about', 'above', 'across']):
            return 'Complex Preposition'
        else:
            return 'Simple Preposition'
    else:
        return 'Other'

def process_text(input_text, nlp):
    # Process the input text using the Spacy model and print relevant information.
    try:
        doc = nlp(input_text)
        word_count = len(doc)
        word_types = {}
        
        for token in doc:
            wt = word_type(token)
            if wt in word_types:
                word_types[wt].append(token.text)
            else:
                word_types[wt] = [token.text]

        sentence_structure = {}
        for sent in doc.sents:
            for token in sent:
                if token.dep_ in sentence_structure:
                    sentence_structure[token.dep_] += 1
                else:
                    sentence_structure[token.dep_] = 1
                    
        readability_suggestions = []
        if word_count > 20:
            readability_suggestions.append("Consider breaking down the text into shorter sentences.")

        print(f"Number of words: {word_count}")
        for wt, words in word_types.items():
            print(f"{wt}s: {words}")
        print(f"Sentence Structure: {sentence_structure}")
        print("Readability Suggestions:")
        for suggestion in readability_suggestions:
            print(suggestion)
    except OSError as error:
        logger.error(f"OSError occurred while processing text: {error}")
    except Errors as error:
        logger.error(f"Spacy Error occurred while processing text: {error}")
    except Exception as error:
        logger.error(f"An error occurred while processing text: {error}", exc_info=True)  # Log exception details

def main():
    # The main function to run the Word Count App and handle user input.
    try:
        initialize_logger()
        print("Welcome to the Word Count App!")
        nlp = load_spacy_model("en_core_web_sm")

        if nlp is None:
            logger.error("Failed to load Spacy model. Exiting program.")
            exit()

        while True:
            text = get_user_input()

            if text == 'q':
                break

            logger.info(f"Processing text: {text}")
            process_text(text, nlp)
            print()

    except Exception as exception:
        logger.error(f"An error occurred in the main function: {exception}", exc_info=True)

if __name__ == "__main__":
    main()
