from nltk.corpus import words

# Calculates the number of words in a given text.
def word_count(text):
    count = len(text.split())
    return count

# Determines whether the given text consists of multiple words.
def word_type(text):
    words = text.split()
    num_words = len(words)
    
    if num_words == 2:
        return "two"
    elif num_words > 2:
        return "multiple"
    else:
        return "single"

def validate_word(text):
    english_words = set(words.words())
    words_to_validate = text.split()
    
    for word in words_to_validate:
        if word.lower() not in english_words:
            return False
    
    return True

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
            print("Invalid input. Please enter a valid English word or 'q' to quit.")

# The main function that runs the app. Prints the welcome message.
def main():
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

