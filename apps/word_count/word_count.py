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
    except Exception as e:
        logging.error(f"An error occurred while loading Spacy model: {e}")
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
    except Exception as e:
        logging.error(f"An error occurred while validating word: {e}")
        return False

def get_user_input():
    # Get user input and validate it using the Spacy model.
    text = ""
    nlp = load_spacy_model("en_core_web_sm")

    if nlp is None:
        logging.error("Spacy model could not be loaded. Exiting program.")
        exit()

    while text != 'q':
        text = input("Enter some text (or 'q' to quit): ").lower()

        if text == 'q':
            return text

        if text.strip() != "" and validate_word(text, nlp):
            return text
        else:
            logging.error(f"Invalid input {text}. Please enter a valid English word or 'q' to quit.")
            print("Invalid input. Please enter a valid English word or 'q' to quit.")

def process_text(input_text, nlp):
    # Process the input text using the Spacy model and print relevant information.
    try:
        doc = nlp(input_text)
        word_count = len(doc)

        nouns = [token.text for token in doc if token.pos_ == 'NOUN']
        verbs = [token.text for token in doc if token.pos_ == 'VERB']
        adjectives = [token.text for token in doc if token.pos_ == 'ADJ']

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
    # The main function to run the Word Count App and handle user input.
    try:
        logging.basicConfig(filename='error.log', level=logging.ERROR)
        print("Welcome to Word Count App!")
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
    except Exception as e:
        logging.error(f"An error occurred in the main function: {e}")

if __name__ == "__main__":
    main()
