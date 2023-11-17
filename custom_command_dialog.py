from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

custom_command_file = "start.txt"

class CustomCommandDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("自定义启动命令")
        layout = QVBoxLayout()
        label = QLabel("请输入您的自定义启动命令:")
        self.input_text = QLineEdit()
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.save_command)
        layout.addWidget(label)
        layout.addWidget(self.input_text)
        layout.addWidget(save_button)
        self.setLayout(layout)

    def save_command(self):
        custom_command = self.input_text.text()
        with open(custom_command_file, "w") as file:
            file.write(custom_command)
        self.accept()
