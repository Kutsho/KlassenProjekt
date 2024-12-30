import os
import sounddevice as sd
import queue
import vosk
import pyttsx3
import subprocess
import json
import threading

# Globale Variablen
model_path = "/home/maximilian/Projects/ProjectWeek/SpeechAI/vosk-model-small-en-us-0.15"
vosk_model = vosk.Model(model_path)
ollama_model = "dolphin-llama3"  # Name deines Ollama-Modells
activation_word = "jojo"  # Aktivierungswort
# Initialisierung von TTS
tts_engine = pyttsx3.init()
voices = tts_engine.getProperty('voices')
tts_engine.setProperty('voice', voices[1].id)

# Initialisierung von VOSK
if not os.path.exists(model_path):
    print("Das VOSK-Modell wurde nicht gefunden. Bitte lade ein Modell herunter.")
    exit(1)
vosk_model = vosk.Model(model_path)
recognizer = vosk.KaldiRecognizer(vosk_model, 16000)
audio_queue = queue.Queue()

# Flag für Aktivierungswort
activation_detected = False

# Funktion: Sprachausgabe
def speak(text):
    tts_engine.say(text)
    tts_engine.runAndWait()

# Funktion: Callback für Spracherkennung
def callback(indata, frames, time, status):
    if status:
        print(f"Status: {status}")
    audio_queue.put(bytes(indata))

# Funktion: Spracherkennung für Aktivierungswort 'jojo'
def recognize_activation_word():
    global activation_detected
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16",
                           channels=1, callback=callback):
        print(f"Warten auf Aktivierungswort '{activation_word}'...")
        while not activation_detected:  # Solange 'jojo' nicht erkannt wurde, weiter hören
            data = audio_queue.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")
                if activation_word in text.lower():
                    # Sprachausgabe in einem separaten Thread starten
                    threading.Thread(target=speak, args=("Yes?",)).start()
                    print(f"Aktivierungswort '{activation_word}' erkannt!")
                    activation_detected = True  # Aktivierungswort erkannt, Flag setzen
                    return

# Funktion: Text nach Aktivierungswort aufnehmen
def record_after_activation():
    user_input = ""
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16", channels=1, callback=callback):
        print("Erkenne Text...")
        while True:
            data = audio_queue.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                user_input = result.get("text", "")
                if user_input:
                    print(f"Erkannt: {user_input}")
                    return user_input

# Funktion: Anfrage an Ollama senden
def query_ollama(prompt):
    command = f"ollama run {ollama_model} \"{prompt}\""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error running Ollama: {result.stderr}")
    return result.stdout.strip()

# Hauptprogramm
if __name__ == "__main__":
    try:
        while True:
            # Warten auf das Aktivierungswort 'jojo'
            recognize_activation_word()

            # Nachdem 'jojo' erkannt wurde, Text aufnehmen
            user_input = record_after_activation()

            if user_input:
                
                print("Anfrage an Ollama senden...")
                response = query_ollama(user_input)
                print(f"Ollama antwortet: {response}")

                print("Antwort ausgeben...")
                speak(response)

                # Nach Antwort von Ollama erneut auf 'jojo' warten
                print("Warten auf nächstes Aktivierungswort 'jojo'...")
                activation_detected = False  # Flag zurücksetzen
    except KeyboardInterrupt:
        print("\nProgramm beendet.")

