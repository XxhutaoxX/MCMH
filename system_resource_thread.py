from PyQt5.QtCore import QThread, pyqtSignal
import psutil

class SystemResourceThread(QThread):
    system_resource_signal = pyqtSignal(float, float)

    def run(self):
        while True:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            self.system_resource_signal.emit(cpu_percent, memory_percent)
