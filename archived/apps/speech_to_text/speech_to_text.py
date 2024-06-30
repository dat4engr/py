import speech_recognition as speech_recognize
from pydub import AudioSegment
from pydub.effects import normalize
import langid
import pydub
import os
import json

def check_file_exists(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError("Input file does not exist.")

def check_file_extension(file_path, valid_extensions):
    if not file_path.lower().endswith(tuple(valid_extensions)):
        raise ValueError("Input file has an invalid extension.")

def convert_wav_to_flac(wav_file, flac_file):
    audio = AudioSegment.from_wav(wav_file)
    
    # Apply audio preprocessing (remove background noise, improve quality, etc.)
    # Example: apply a noise reduction filter
    audio = audio.low_pass_filter(1500)
    
    audio.export(flac_file, format="flac")

def recognize_speech(audio_file):
    recognize = speech_recognize.Recognizer()

    with speech_recognize.AudioFile(audio_file) as source:
        audio = recognize.record(source)

    try:
        recognized_text = recognize.recognize_google(audio)
        
        # Language detection
        try:
            language = langid.classify(recognized_text)[0]
            print(f"Detected Language: {language}")
        except Exception as exception:
            language = "Unknown"
            print(f"Error occurred during language detection: {exception}")
        
        print(f"Recognized Text: {recognized_text}")
        return recognized_text, language
    except speech_recognize.UnknownValueError:
        print("Unable to recognize speech")
    except speech_recognize.RequestError as request_error:
        print(f"Speech recognition request error: {request_error}")
    except Exception as exception:
        print(f"An error occurred: {exception}")

    return None, None

def save_to_json(data, json_file):
    with open(json_file, 'w') as file:
        json.dump(data, file)

def main():
    audio_file = "audio.wav"
    try:
        check_file_exists(audio_file)
        check_file_extension(audio_file, [".wav"])
        flac_file = "audio.flac"
        convert_wav_to_flac(audio_file, flac_file)
        text, language = recognize_speech(flac_file)
        if text:
            data = {
                "audio_file": audio_file,
                "detected_language": language,
                "recognized_text": text
            }
            json_file = "train_audio_data.json"
            save_to_json(data, json_file)
    except FileNotFoundError as file_not_found_error:
        print(f"File not found: {file_not_found_error}")
    except ValueError as value_error:
        print(f"Value error: {value_error}")
    except pydub.exceptions.CouldntDecodeError as could_not_decode_error:
        print(f"Error decoding audio file: {could_not_decode_error}")
    except Exception as exception:
        print(f"An error occurred: {exception}")


if __name__ == "__main__":
    main()
