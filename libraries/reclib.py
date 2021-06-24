# from PyQt5 import QtWidgets, QtGui
# from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QEventLoop, QThread, QObject, pyqtSlot, pyqtSignal

import pyaudio
import wave

CHUNK = 1024  # Запись кусками по 1024 сэмпла
SAMPLE_FORMAT = pyaudio.paInt16  # 16 бит на выборку
CHANNELS = 2
FS = 44100  # Запись со скоростью 44100 выборок(samples) в секунду


class MorseWriter(QObject):
    run_trigger = pyqtSignal()
    stop_trigger = pyqtSignal(bool)

    def __init__(self, widjet, filename, finish):
        super(MorseWriter, self).__init__()

        self.widjet = widjet
        self.filename = filename
        self.finish = finish

        self.run_trigger.connect(self.run)
        self.stop_trigger.connect(self.stop)

        self.not_stopped = True
        self.finished = True
        self.save = True
        self.recorded = False

    @pyqtSlot()
    def run(self):
        # print('Recording')
        self.widjet.reciver.emit("started")
        self.finished = False  # flag of writing

        p = pyaudio.PyAudio()

        stream = p.open(format=SAMPLE_FORMAT,
                        channels=CHANNELS,
                        rate=FS,
                        frames_per_buffer=CHUNK,
                        input=True)
        frames = []

        self.widjet.reciver.emit("REC")

        while self.not_stopped:
            data = stream.read(CHUNK)
            frames.append(data)

        # Остановить и закрыть поток
        stream.stop_stream()
        stream.close()
        # Завершить интерфейс PortAudio
        p.terminate()

        if self.save:
            self.widjet.reciver.emit("saving")
            wf = wave.open(self.filename, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(SAMPLE_FORMAT))
            wf.setframerate(FS)
            wf.writeframes(b''.join(frames))
            wf.close()

        self.finished = True
        self.recorded = True
        msg = "finished"
        if not self.save: msg = "force quit"
        self.widjet.reciver.emit(msg)
        self.finish.set()
        # print('Finished recording')

    # @pyqtSlot()
    def stop(self, save):
        # print("here")
        self.save = save
        self.not_stopped = False