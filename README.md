# Dashboard

Dieses Repository enthält ein interaktives Dashboard, das mit Python und der GUI-Bibliothek PySide6 (Qt für Python) entwickelt wurde. 

Voraussetzungen
Stelle sicher, dass die folgenden Komponenten auf deinem Computer installiert sind:
	Python >3.14
	pip 
	git

Installation in 4 Schritten
1. Repository klonen
Öffne dein Terminal (Eingabeaufforderung / PowerShell / Bash) und lade das Projekt herunter:

git clone https://github.com/Fruchttee08/Dashboard.git
cd Dashboard

3. Virtuelle Umgebung erstellen (Empfohlen)
Es wird dringend empfohlen, eine virtuelle Umgebung (venv) zu verwenden. 
Unter Windows:

python -m venv venv
.\venv\Scripts\activate

Unter macOS / Linux:

python3 -m venv venv
source venv/bin/activate

5. Abhängigkeiten installieren

pip install --upgrade pip
pip install -r requirements.txt

7. Anwendung starten
Führe das Hauptskript aus, um das GUI-Dashboard zu öffnen.

python IU_dash.py
