# Audio Event Counter

This project contains a scaffold for a desktop application that detects and counts audio events (such as laughter or screaming) in real time. The application uses **PyQt5** for the user interface, **sounddevice** for capturing microphone input, and **pyttsx3** for optional text-to-speech feedback.

The current implementation includes placeholders for the actual audio classification model. Event detection is simulated using a simple amplitude threshold so that the UI can be tested. All major features are represented in the code and marked with TODO comments where further development is needed.

## Running
This project uses pip for dependency management. First, create a virtual environment (recommended):

```bash
python -m venv venv
venv\Scripts\activate
```

Then install the project dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python src/audio_counter_app.py
```

## Packaging as an Executable
To create a standalone Windows executable, first install PyInstaller:

```bash
pip install pyinstaller
```

Then create the executable:

```bash
pyinstaller --onefile src/audio_counter_app.py
```

Adjust the command as needed to include Qt plugins and other resources.
