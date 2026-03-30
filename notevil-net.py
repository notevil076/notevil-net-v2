import sys
import os
import subprocess
import ctypes
import psutil
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit, QLabel
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_base_path():
    # Если запущено как скомпилированный EXE
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    # Если запущен просто .py скрипт
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_path()
CORE_EXE = os.path.join(BASE_DIR, "core", "sing-box.exe")
CONFIG_JSON = os.path.join(BASE_DIR, "config", "config.json")
ICON_PATH = os.path.join(BASE_DIR, "icons", "notevil.ico")

# Класс для чтения логов в реальном времени, чтобы UI не зависал
class LogWorker(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, process):
        super().__init__()
        self.process = process

    def run(self):
        while self.process.poll() is None:
            line = self.process.stdout.readline()
            if line:
                self.log_signal.emit(line.strip())

class NotEvilNetApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NOTEVIL//NET v2.0")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setFixedSize(450, 550)
        self.sing_box_process = None
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        title_label = QLabel("N O T E V I L // N E T")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #00FF00;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background-color: #1e1e1e; color: #dcdcdc; font-family: Consolas;")
        layout.addWidget(self.log_output)

        self.start_btn = QPushButton("[ INITIALIZE UPLINK ]")
        self.start_btn.setFixedHeight(40)
        self.start_btn.clicked.connect(self.start_connection)
        layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("[ DISCONNECT / CLEANUP ]")
        self.stop_btn.setFixedHeight(40)
        self.stop_btn.clicked.connect(self.stop_connection)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)

        self.log_msg("[+] System status: READY")
        if not is_admin():
             self.log_msg("[!] WARNING: Admin rights missing! TUN will fail.")

    def log_msg(self, msg):
        self.log_output.append(msg)

    def force_cleanup(self):
        """ Убивает все зависшие процессы sing-box """
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == 'sing-box.exe':
                try:
                    proc.kill()
                    self.log_msg("[+] Residual process terminated.")
                except:
                    pass

    def start_connection(self):
        if not is_admin():
            self.log_msg("[-] FATAL: Elevation required!")
            return

        self.force_cleanup() # Чистим перед запуском

        if not os.path.exists(CORE_EXE) or not os.path.exists(CONFIG_JSON):
            self.log_msg("[-] FATAL: Core or Config missing!")
            return

        try:
            self.sing_box_process = subprocess.Popen(
                [CORE_EXE, "run", "-c", CONFIG_JSON],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Запускаем поток чтения логов
            self.log_worker = LogWorker(self.sing_box_process)
            self.log_worker.log_signal.connect(self.log_msg)
            self.log_worker.start()

            self.log_msg("[+] Uplink active. gVisor stack engaged.")
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
        except Exception as e:
            self.log_msg(f"[-] Startup error: {e}")

    def stop_connection(self):
        self.log_msg("[*] Terminating connection...")
        if self.sing_box_process:
            self.sing_box_process.terminate()
            self.sing_box_process.wait(timeout=3)
            self.sing_box_process = None
        
        self.force_cleanup() # Гарантированно возвращаем интернет
        self.log_msg("[+] System restored to direct path.")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def closeEvent(self, event):
        self.stop_connection()
        event.accept()

if __name__ == "__main__":
    if not is_admin():
        # Магия авто-перезапуска от админа
        script = os.path.abspath(sys.argv[0])
        params = ' '.join(sys.argv[1:])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
        sys.exit()

    app = QApplication(sys.argv)
    window = NotEvilNetApp()
    window.show()
    sys.exit(app.exec())