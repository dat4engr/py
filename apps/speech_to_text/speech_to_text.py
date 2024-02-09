import speech_recognition as sr
from pydub import AudioSegment

def convert_wav_to_flac(wav_file):
    audio = AudioSegment.from_wav(wav_file)
    flac_file = "audio.flac"
    audio.export(flac_file, format="flac")
    return flac_file

def speech_to_text(flac_file):
    r = sr.Recognizer()
    
    with sr.AudioFile(flac_file) as source:
        audio = r.record(source)
    
    try:
        text = r.recognize_google(audio)
        print("Recognized Text:", text)
    except sr.UnknownValueError:
        print("Unable to recognize speech")
    
    return text

wav_file = "audio.wav"
flac_file = convert_wav_to_flac(wav_file)

text = speech_to_text(flac_file)
