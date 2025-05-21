from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import speech_recognition as sr
from gtts import gTTS
import pygame
import os
import time
from googletrans import Translator

app = Flask(__name__)
socketio = SocketIO(app)

# Initialize translator
translator = Translator()
pygame.mixer.init()

@app.route('/')
def index():
    return render_template('index.html')  # Serve the HTML frontend

@socketio.on('start_translation')
def handle_translation(data):
    input_lang = data['input_lang']
    output_lang = data['output_lang']

    # Example logic for speech recognition and translation
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            emit('log', {'message': f"Listening for speech in {input_lang}..."})
            audio_data = recognizer.listen(source, timeout=None, phrase_time_limit=5)
            recognized_text = recognizer.recognize_google(audio_data, language=input_lang)
            emit('log', {'message': f"Recognized Text: {recognized_text}"})
            
            # Translate
            translated_text = translator.translate(recognized_text, src=input_lang, dest=output_lang).text
            emit('log', {'message': f"Translated Text: {translated_text}"})

            # Convert to speech
            tts = gTTS(text=translated_text, lang=output_lang)
            tts_output = f"output_{str(int(time.time()))}.mp3"
            tts.save(tts_output)
            emit('log', {'message': "Playing translated speech..."})

            # Play the audio
            pygame.mixer.music.load(tts_output)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pass
            os.remove(tts_output)

    except Exception as e:
        emit('log', {'message': f"Error: {str(e)}"})

if __name__ == '__main__':
    socketio.run(app, debug=True)
