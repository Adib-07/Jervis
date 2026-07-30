from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HeardSpeech:
    text: str
    error: str | None = None


class Speaker:
    def __init__(self) -> None:
        self._engine = None
        self._error: str | None = None

        try:
            import pyttsx3

            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", 178)
        except Exception as exc:  # Audio engines fail differently by platform.
            self._error = str(exc)

    @property
    def available(self) -> bool:
        return self._engine is not None

    @property
    def error(self) -> str | None:
        return self._error

    def say(self, text: str) -> None:
        print(text)
        if self._engine is None:
            return
        self._engine.say(text)
        self._engine.runAndWait()


class Listener:
    def __init__(self) -> None:
        self._recognizer = None
        self._microphone_cls = None
        self._error: str | None = None

        try:
            import speech_recognition as sr

            self._recognizer = sr.Recognizer()
            sr.Microphone.get_pyaudio()
            self._microphone_cls = sr.Microphone
        except Exception as exc:
            self._recognizer = None
            self._microphone_cls = None
            self._error = str(exc)

    @property
    def available(self) -> bool:
        return self._recognizer is not None and self._microphone_cls is not None

    @property
    def error(self) -> str | None:
        return self._error

    def listen(self, timeout: int = 5, phrase_time_limit: int = 10) -> HeardSpeech:
        if not self.available:
            return HeardSpeech("", self._error or "Speech recognition is unavailable.")

        try:
            with self._microphone_cls() as source:
                print("Listening...")
                self._recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self._recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit,
                )
            text = self._recognizer.recognize_google(audio)
            return HeardSpeech(text.strip())
        except Exception as exc:
            return HeardSpeech("", str(exc))
