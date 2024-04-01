import logging
import spacy

def load_spacy_model(model_name):
    # Load a Spacy model with the given model name.
    try:
        nlp = spacy.load(model_name)
        return nlp
    except OSError as error:
        logging.error(f"Error loading Spacy model: {error}")
        return None
    except Exception as exception:
        logging.error(f"An error occurred while loading Spacy model: {exception}")
        return None

def validate_word(text, nlp):
    # Validate the input text to ensure it is a valid English word.
    try:
        doc = nlp(text)
        if all(token.is_alpha or token.text in [' ', '-'] for token in doc):
            return True
        else:
            logging.error(f"Invalid input: {text}, contains non-alphabetic characters.")
            return False
    except Exception as exception:
        logging.error(f"An error occurred while validating word: {exception}")
        return False

def get_user_input():
    # Get user input and validate it using the Spacy model.
    text = ""
    nlp = load_spacy_model("en_core_web_sm")

    if nlp is None:
        logging.error("Spacy model could not be loaded. Exiting program.")
        exit()

    while text != 'q':
        text = input("Enter a word or sentence (or 'q' to quit): ").lower()

        if text == 'q':
            return text

        if text.strip() != "" and validate_word(text, nlp):
            return text
        else:
            logging.error(f"Invalid input {text}. Please enter a valid English word or 'q' to quit.")
            print("Invalid input. Please enter a valid English word or sentence or 'q' to quit.")

def word_type(token):
    # Determine the word type (Noun, Verb, Adjective) for a given token.
    if token.pos_ == 'NOUN':
        return 'Noun'
    elif token.pos_ == 'VERB':
        return 'Verb'
    elif token.pos_ == 'ADJ':
        return 'Adjective'
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
    except Exception as exception:
        logging.error(f"An error occurred while processing text: {exception}")

def main():
    # The main function to run the Word Count App and handle user input.
    try:
        logging.basicConfig(filename='error.log', level=logging.ERROR)
        print("Welcome to the Word Count App!")
        nlp = load_spacy_model("en_core_web_sm")

        if nlp is None:
            logging.error("Spacy model could not be loaded. Exiting program.")
            exit()

        while True:
            text = get_user_input()

            if text == 'q':
                break

            logging.info(f"Processing text: {text}")
            process_text(text, nlp)
            print()

    except Exception as exception:
        logging.error(f"An error occurred in the main function: {exception}")

if __name__ == "__main__":
    main()
