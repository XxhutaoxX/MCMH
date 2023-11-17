import sys
from PyQt5.QtWidgets import QApplication
from minecraft_server_manager import MinecraftServerManager

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MinecraftServerManager()
    window.show()
    sys.exit(app.exec_())
