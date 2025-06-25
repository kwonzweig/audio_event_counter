# -*- coding: utf-8 -*-
"""Audio Event Counter Application.

This is a scaffold for a desktop application that listens to the microphone
in real time and counts selected audio events such as laughter or screaming.
It provides a graphical interface with options to configure detection mode,
model selection, TTS feedback, and more.

The code uses PyQt5 for the GUI, sounddevice for microphone capture, and
pyttsx3 for text-to-speech feedback. Actual audio event classification is not
implemented and is left as a TODO for future development.

To create a standalone executable on Windows you can use PyInstaller:
    pyinstaller --onefile audio_counter_app.py
"""

import sys
import threading
import time
import queue
import random
from dataclasses import dataclass

import numpy as np
import sounddevice as sd
import pyttsx3
from PyQt5 import QtCore, QtWidgets


@dataclass
class AppConfig:
    """Application configuration options."""

    mode: str = "Laughter"
    model: str = "Dummy"
    tts_enabled: bool = True
    tts_volume: float = 1.0
    language: str = "en"


class AudioWorker(QtCore.QThread):
    """Background thread that captures audio and detects events."""

    event_detected = QtCore.pyqtSignal()
    status_update = QtCore.pyqtSignal(str)

    def __init__(self, config: AppConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self._running = False
        self._last_event_time = 0.0
        self._queue = queue.Queue()
        self.stream = None
        self.threshold = 0.1  # Placeholder threshold for detection

    def run(self):
        self._running = True
        self.status_update.emit("Listening")
        try:
            with sd.InputStream(channels=1, callback=self.audio_callback,
                                samplerate=44100, blocksize=1024):
                while self._running:
                    time.sleep(0.1)
        except Exception as exc:  # pragma: no cover - placeholder
            self.status_update.emit(f"Error: {exc}")
        self.status_update.emit("Paused")

    def stop(self):
        self._running = False

    def audio_callback(self, indata, frames, time_info, status):
        if not self._running:
            return
        if status:
            self.status_update.emit(str(status))
        if self.detect_event(indata[:, 0]):
            self.event_detected.emit()

    def detect_event(self, data: np.ndarray) -> bool:
        """Placeholder detection logic.

        This should be replaced with proper audio classification using the
        selected model.
        """
        # TODO: Load and use the selected audio model for classification
        amplitude = np.abs(data).mean()
        now = time.time()
        if amplitude > self.threshold and now - self._last_event_time > 1:
            self._last_event_time = now
            return True
        # Simulate occasional detection so the UI can be tested
        if random.random() < 0.001:
            self._last_event_time = now
            return True
        return False


class MainWindow(QtWidgets.QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Event Counter")
        self.config = AppConfig()
        self.counter = 0
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('volume', self.config.tts_volume)
        self._build_ui()
        self.audio_worker = AudioWorker(self.config)
        self.audio_worker.event_detected.connect(self.on_event_detected)
        self.audio_worker.status_update.connect(self.on_status_update)

    # ------------------------------------------------------------------
    # UI setup
    # ------------------------------------------------------------------
    def _build_ui(self):
        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        central.setLayout(layout)
        self.setCentralWidget(central)

        # Counter display
        self.counter_label = QtWidgets.QLabel(self._counter_text())
        font = self.counter_label.font()
        font.setPointSize(16)
        self.counter_label.setFont(font)
        layout.addWidget(self.counter_label)

        # Status label
        self.status_label = QtWidgets.QLabel("Status: Paused")
        layout.addWidget(self.status_label)

        # Control buttons
        btn_layout = QtWidgets.QHBoxLayout()
        self.start_btn = QtWidgets.QPushButton("Start")
        self.pause_btn = QtWidgets.QPushButton("Pause")
        self.reset_btn = QtWidgets.QPushButton("Reset")
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.reset_btn)
        layout.addLayout(btn_layout)

        self.start_btn.clicked.connect(self.start_detection)
        self.pause_btn.clicked.connect(self.pause_detection)
        self.reset_btn.clicked.connect(self.reset_count)

        # Mode selection
        mode_layout = QtWidgets.QHBoxLayout()
        mode_layout.addWidget(QtWidgets.QLabel("Mode:"))
        self.mode_combo = QtWidgets.QComboBox()
        self.mode_combo.addItems(["Laughter", "Screaming"])
        self.mode_combo.currentTextChanged.connect(self.change_mode)
        mode_layout.addWidget(self.mode_combo)
        layout.addLayout(mode_layout)

        # Model selection (placeholder)
        model_layout = QtWidgets.QHBoxLayout()
        model_layout.addWidget(QtWidgets.QLabel("Model:"))
        self.model_combo = QtWidgets.QComboBox()
        self.model_combo.addItems(["Dummy", "YAMNet", "Other"])
        self.model_combo.currentTextChanged.connect(self.change_model)
        model_layout.addWidget(self.model_combo)
        layout.addLayout(model_layout)

        # TTS feedback toggle
        self.tts_checkbox = QtWidgets.QCheckBox("Enable TTS Feedback")
        self.tts_checkbox.setChecked(True)
        self.tts_checkbox.stateChanged.connect(self.toggle_tts)
        layout.addWidget(self.tts_checkbox)

        # TTS volume slider
        vol_layout = QtWidgets.QHBoxLayout()
        vol_layout.addWidget(QtWidgets.QLabel("TTS Volume:"))
        self.volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_slider.valueChanged.connect(self.change_volume)
        vol_layout.addWidget(self.volume_slider)
        layout.addLayout(vol_layout)

        # Language selection
        lang_layout = QtWidgets.QHBoxLayout()
        lang_layout.addWidget(QtWidgets.QLabel("Language:"))
        self.lang_combo = QtWidgets.QComboBox()
        self.lang_combo.addItems(["English", "Korean"])
        self.lang_combo.currentTextChanged.connect(self.change_language)
        lang_layout.addWidget(self.lang_combo)
        layout.addLayout(lang_layout)

    # ------------------------------------------------------------------
    # Control callbacks
    # ------------------------------------------------------------------
    def start_detection(self):
        if self.audio_worker.isRunning():
            return
        self.counter = 0
        self.update_counter_label()
        self.audio_worker.start()

    def pause_detection(self):
        if self.audio_worker.isRunning():
            self.audio_worker.stop()
            self.audio_worker.wait()

    def reset_count(self):
        self.counter = 0
        self.update_counter_label()

    def change_mode(self, text: str):
        self.config.mode = text
        self.counter = 0
        self.update_counter_label()

    def change_model(self, text: str):
        self.config.model = text
        # TODO: Load selected model and apply in detection

    def toggle_tts(self, state: int):
        self.config.tts_enabled = state == QtCore.Qt.Checked

    def change_volume(self, value: int):
        self.config.tts_volume = value / 100.0
        self.tts_engine.setProperty('volume', self.config.tts_volume)

    def change_language(self, text: str):
        self.config.language = 'en' if text == 'English' else 'ko'

    def on_event_detected(self):
        self.counter += 1
        self.update_counter_label()
        if self.config.tts_enabled:
            self.speak_count()

    def on_status_update(self, text: str):
        self.status_label.setText(f"Status: {text}")

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    def _counter_text(self) -> str:
        return f"{self.config.mode} count: {self.counter}"

    def update_counter_label(self):
        self.counter_label.setText(self._counter_text())

    def speak_count(self):
        phrases = {
            'en': {
                'Laughter': 'You laughed {n} times.',
                'Screaming': 'You screamed {n} times.'
            },
            'ko': {
                'Laughter': '당신은 {n}번 웃었습니다.',
                'Screaming': '당신은 {n}번 비명을 질렀습니다.'
            }
        }
        phrase = phrases[self.config.language][self.config.mode].format(n=self.counter)
        threading.Thread(target=self._speak, args=(phrase,), daemon=True).start()

    def _speak(self, text: str):  # pragma: no cover - GUI / TTS
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()


def main():  # pragma: no cover - entry point
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
