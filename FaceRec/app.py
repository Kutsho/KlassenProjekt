import sys
import time
sys.path.append('/home/maximilian/venv/lib/python3.12/site-packages')
import face_recognition
import cv2
import os
from datetime import datetime, timedelta
import pyttsx3

# Starte die Text-to-Speech Engine
engine = pyttsx3.init()

# Pfad für bekannte Gesichter und Logs
KNOWN_FACES_DIR = "known_faces"
OUTPUT_FILE = "erkannt_log.txt"

# Lade bekannte Gesichter
known_encodings = []
known_names = []

print("Lade bekannte Gesichter...")
for filename in os.listdir(KNOWN_FACES_DIR):
    if filename.endswith((".jpg", ".png")):
        image_path = os.path.join(KNOWN_FACES_DIR, filename)
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_encodings.append(encodings[0])
            name = os.path.splitext(filename)[0]
            known_names.append(name)

print("Gesichter geladen!")
print("Starte Gesichtserkennung... (Beende mit 'q')")

# Webcam starten
video_capture = cv2.VideoCapture(0)

# Erkennungs-Tracker
recognized_status = {}  # {'name': {'status': 'im Raum', 'last_seen': datetime}}
FORGET_TIME = timedelta(seconds=30)  # Vergessenszeit: 30 Sekunden
CHECK_INTERVAL = timedelta(seconds=2)  # Intervall für Überprüfung: 2 Sekunden

last_check_time = datetime.now()

# Funktion für dynamische Begrüßung basierend auf der Tageszeit
def get_greeting():
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        return "Good morning"
    elif 12 <= current_hour < 18:
        return "Good day"
    else:
        return "Good evening"

# Hauptlogik
with open(OUTPUT_FILE, "w") as log_file:
    while True:
        current_time = datetime.now()

        # Überprüfe alle 2 Sekunden
        if current_time - last_check_time >= CHECK_INTERVAL:
            last_check_time = current_time

            # Nimm ein Bild auf
            ret, frame = video_capture.read()
            if not ret:
                break

            # Konvertiere das Bild zu RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Gesichtserkennung im aktuellen Bild
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            currently_seen = set()

            # Begrüßung und Erkennung
            for face_encoding, face_location in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(known_encodings, face_encoding)
                name = "Unbekannt"

                if True in matches:
                    match_index = matches.index(True)
                    name = known_names[match_index]

                    # Wenn die Person noch nicht im Raum ist, betritt sie den Raum
                    if name not in recognized_status or recognized_status[name]['status'] == 'verlassen':
                        recognized_status[name] = {'status': 'im Raum', 'last_seen': current_time}
                        log_message = f"{current_time.strftime('%Y-%m-%d %H:%M:%S')} - {name} betritt den Raum"
                        print(log_message)
                        log_file.write(log_message + "\n")
                        log_file.flush()

                        # Dynamische Begrüßung ausgeben
                        greeting = get_greeting()
                        engine.say(f"{greeting}, {name}. How are you today?")
                        engine.runAndWait()

                # Aktualisiere zuletzt gesehene Person
                if name in recognized_status:
                    recognized_status[name]['last_seen'] = current_time

                currently_seen.add(name)

                # Zeichne Rechteck und Namen ins Bild
                top, right, bottom, left = face_location
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            # Überprüfe, ob jemand den Raum verlassen hat
            for name, info in recognized_status.items():
                if info['status'] == 'im Raum' and current_time - info['last_seen'] >= FORGET_TIME:
                    recognized_status[name]['status'] = 'verlassen'
                    log_message = f"{current_time.strftime('%Y-%m-%d %H:%M:%S')} - {name} verlässt den Raum"
                    print(log_message)
                    log_file.write(log_message + "\n")
                    log_file.flush()

            # Zeige das aktuelle Bild
            cv2.imshow("Live Gesichtserkennung", frame)

        # Beenden mit 'q'
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

# Kamera freigeben und Fenster schließen
video_capture.release()
cv2.destroyAllWindows()
print(f"Log gespeichert in {OUTPUT_FILE}")
