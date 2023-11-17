import atexit
import os
import subprocess
import sys

import psutil
from PyQt5.QtCore import QProcess, pyqtSlot, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QCompleter,
    QVBoxLayout,
    QWidget,
    QPlainTextEdit,
    QLineEdit,
    QHBoxLayout,
    QMessageBox,
    QComboBox,
    QDialog,
    QLabel,
)

minecraft_server_jar = "paper.jar"
additional_exe = "update.exe"
custom_command_file = "start.txt"


class SystemResourceThread(QThread):
    system_resource_signal = pyqtSignal(float, float)

    def run(self):
        while True:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            self.system_resource_signal.emit(cpu_percent, memory_percent)


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


class MinecraftServerManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("梦幻我的世界服务器管理面板")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("./app_icon.ico"))

        # 使用 Fusion 样式
        app.setStyle("Fusion")

        # 创建字体对象
        font = QFont()
        font.setFamily("微软雅黑")  # 设置字体族
        font.setPointSize(12)  # 设置字体大小

        # 创建按钮样式
        button_style = (
            "QPushButton { background-color: #3498db; color: white; border: none; "
            "padding: 10px; border-radius: 5px; }"
            "QPushButton:hover { background-color: #2980b9; }"
        )
        self.setStyleSheet(button_style)

        start_button = QPushButton("启动服务器")
        self.set_button_font(start_button, 16, font)  # 将字体应用到按钮
        start_button.clicked.connect(self.on_start_button_click)

        stop_button = QPushButton("停止服务器")
        self.set_button_font(stop_button, 16, font)  # 将字体应用到按钮
        stop_button.clicked.connect(self.on_stop_button_click)

        quit_button = QPushButton("退出")
        self.set_button_font(quit_button, 16, font)  # 将字体应用到按钮
        quit_button.clicked.connect(self.on_quit_button_click)

        self.custom_command_button = QPushButton("自定义启动命令")
        self.set_button_font(self.custom_command_button, 16, font)  # 将字体应用到按钮
        self.custom_command_button.clicked.connect(self.on_custom_command_button_click)

        self.system_resource_thread = SystemResourceThread()
        self.system_resource_thread.system_resource_signal.connect(self.update_system_resource)
        self.system_resource_thread.start()

        self.input_text = QLineEdit()
        self.input_text.returnPressed.connect(self.send_command)
        self.set_widget_font(self.input_text, 14, font)  # 将字体应用到输入框

        self.output_widget = QPlainTextEdit()
        self.output_widget.setReadOnly(True)
        self.output_widget.setFocusPolicy(Qt.StrongFocus)
        self.output_widget.setFocus()
        self.set_widget_font(self.output_widget, 14, font)  # 将字体应用到输出框

        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(["12", "14", "16", "18", "20"])
        self.font_size_combo.currentIndexChanged.connect(self.change_font_size)

        # 创建自动完成器并关联到输入文本框
        self.create_command_completer()

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(start_button)
        buttons_layout.addWidget(stop_button)
        buttons_layout.addWidget(quit_button)
        buttons_layout.addWidget(self.custom_command_button)

        layout = QVBoxLayout()
        layout.addWidget(self.output_widget)
        layout.addWidget(self.input_text)
        layout.addWidget(self.font_size_combo)
        layout.addLayout(buttons_layout)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)
        self.process = None
        try:
            self.start_additional_script()
        except:
            print("can't check update")

        atexit.register(self.closeEvent)

    def create_command_completer(self):
        completer = QCompleter(self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        self.input_text.setCompleter(completer)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Tab and self.input_text.hasFocus():
            self.complete_command()
        else:
            super().keyPressEvent(event)

    def complete_command(self):
        current_text = self.input_text.text().lower()

        # 获取Minecraft服务器命令列表
        minecraft_commands = ["help", "start", "stop", "reload", "say", "list", "..."]

        # 筛选以当前文本开头的命令
        matching_commands = [cmd for cmd in minecraft_commands if cmd.lower().startswith(current_text)]

        if len(matching_commands) == 1:
            # 如果只有一个匹配，自动补全
            self.input_text.setText(matching_commands[0])
            self.input_text.setCursorPosition(len(matching_commands[0]))
        elif len(matching_commands) > 1:
            # 如果有多个匹配，显示匹配列表
            self.show_command_completion_options(matching_commands)

    def show_command_completion_options(self, options):
        completer = self.input_text.completer()
        completer.setModel(QCompleter(options, self.input_text))
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.complete()

    def update_system_resource(self, cpu_percent, memory_percent):
        self.statusBar().showMessage(f"CPU占用：{cpu_percent}%  内存占用：{memory_percent}%")

    def set_button_font(self, button, font_size, font):
        button.setFont(font)  # 将字体应用到按钮
        button.setProperty("opacity", 1.0)  # 添加此行
        button.setStyleSheet(
            f"QPushButton {{ background-color: #3498db; color: white; border: none; "
            f"padding: 10px; border-radius: 5px; font-size: {font_size}px; }}"
            f"QPushButton:hover {{ background-color: #2980b9; }}"
        )

    def set_widget_font(self, widget, font_size, font):
        font.setPointSize(font_size)  # 设置字体大小
        widget.setFont(font)

    @pyqtSlot()
    def on_start_button_click(self):
        if os.path.isfile(custom_command_file):
            with open(custom_command_file, "r") as file:
                custom_command = file.read()
                self.process = QProcess()
                self.process.readyRead.connect(self.data_ready)
                self.process.start(custom_command)
        else:
            if not os.path.isfile(minecraft_server_jar):
                QMessageBox.warning(self, '错误', '未找到jar文件！')
                return
            self.process = QProcess()
            self.process.readyRead.connect(self.data_ready)
            self.process.start("java", ["-Dfile.encoding=UTF-8", "-jar", minecraft_server_jar, "-nogui"])

    @pyqtSlot()
    def on_stop_button_click(self):
        if self.process is not None:
            self.process.write("stop\n".encode())
            self.statusBar().showMessage("向Minecraft服务器发送停止命令")

    def on_quit_button_click(self):
        if self.confirm_exit():
            self.close()

    def on_custom_command_button_click(self):
        dialog = CustomCommandDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            QMessageBox.information(self, '保存成功', '自定义命令已成功保存！')

    def send_command(self):
        command = self.input_text.text()
        if self.process is not None:
            self.process.write(f"{command}\n".encode())
            self.append_colored_text(f"> {command}", "#0000FF")
        self.input_text.clear()

    def append_colored_text(self, text, color):
        cursor = self.output_widget.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertHtml(f'<span style="color: {color};">{text}</span>')
        cursor.insertBlock()
        self.output_widget.setTextCursor(cursor)

    @pyqtSlot()
    def data_ready(self):
        data = self.process.readAllStandardOutput().data().decode("utf-8", "ignore")
        self.append_colored_text(data, "#000000")
        self.output_widget.moveCursor(self.output_widget.textCursor().End)

    def change_font_size(self, index):
        font_size = int(self.font_size_combo.currentText())
        self.set_widget_font(self.input_text, font_size)
        self.set_widget_font(self.output_widget, font_size)

    def confirm_exit(self):
        reply = QMessageBox.question(
            self,
            '确认退出',
            '确认要退出吗？未保存的数据将会丢失。',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        return reply == QMessageBox.Yes

    def start_additional_script(self):
        subprocess.Popen([additional_exe])

    def closeEvent(self, event):
        if self.confirm_exit():
            self.on_stop_button_click()
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MinecraftServerManager()
    window.show()
    sys.exit(app.exec_())
