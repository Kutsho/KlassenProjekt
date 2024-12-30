System aktualisieren und grundlegende Tools installieren
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv build-essential cmake wget unzip \
libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg

Python-Bibliotheken installieren
python3 -m venv ~/venv
source ~/venv/bin/activate
pip install --upgrade pip
pip install face_recognition opencv-python pyttsx3 sounddevice vosk

Zusätzliche Tools für Ollama installieren
sudo apt install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo docker pull ollama/dolphin-llama3

VOSK-Modell herunterladen (falls nicht vorhanden)
mkdir -p ~/Projects/ProjectWeek/SpeechAI
cd ~/Projects/ProjectWeek/SpeechAI
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip

Berechtigungen sicherstellen
sudo chmod -R 755 ~/Projects/ProjectWeek/SpeechAI
