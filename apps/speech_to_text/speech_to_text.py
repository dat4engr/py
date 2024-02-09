import speech_recognition as sr
from pydub import AudioSegment
import pydub
import os

def check_file_exists(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError("Input file does not exist.")

def check_file_extension(file_path, valid_extensions):
    if not file_path.lower().endswith(tuple(valid_extensions)):
        raise ValueError("Input file has an invalid extension.")

def convert_wav_to_flac(wav_file, flac_file):
    audio = AudioSegment.from_wav(wav_file)
    audio.export(flac_file, format="flac")

def recognize_speech(audio_file):
    r = sr.Recognizer()

    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)

    try:
        recognized_text = r.recognize_google(audio)
        print(f"Recognized Text: {recognized_text}")
        return recognized_text
    except sr.UnknownValueError:
        print("Unable to recognize speech")
    except sr.RequestError as e:
        print(f"Speech recognition request error: {e}")

    return None

def main():
    audio_file = "audio.wav"
    try:
        check_file_exists(audio_file)
        check_file_extension(audio_file, [".wav"])
        flac_file = "audio.flac"
        convert_wav_to_flac(audio_file, flac_file)
        text = recognize_speech(flac_file)
        if text:
            # Do something with the recognized text
            pass
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except ValueError as e:
        print(f"Value error: {e}")
    except pydub.exceptions.CouldntDecodeError as e:
        print(f"Error decoding audio file: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
