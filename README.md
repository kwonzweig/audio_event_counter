# Audio Event Counter

This project contains a scaffold for a desktop application that detects and counts audio events (such as laughter or screaming) in real time. The application uses **PyQt5** for the user interface, **sounddevice** for capturing microphone input, and **pyttsx3** for optional text-to-speech feedback.

The current implementation includes placeholders for the actual audio classification model. Event detection is simulated using a simple amplitude threshold so that the UI can be tested. All major features are represented in the code and marked with TODO comments where further development is needed.

## Running
Install the required dependencies first (for example using `pip`):

```bash
pip install PyQt5 sounddevice pyttsx3 numpy
```

Then run the application:

```bash
python audio_counter_app.py
```

## Packaging as an Executable
To create a standalone Windows executable you can use [PyInstaller](https://pyinstaller.org/):

```bash
pyinstaller --onefile audio_counter_app.py
```

Adjust the command as needed to include Qt plugins and other resources.
