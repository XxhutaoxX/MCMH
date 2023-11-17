import atexit
import os
import subprocess
import sys
import time

from PyQt5.QtCore import QProcess, pyqtSlot, Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QPlainTextEdit,
    QLineEdit,
    QHBoxLayout,
    QMessageBox,
    QComboBox, QDialog,
)

from system_resource_thread import SystemResourceThread
from custom_command_dialog import CustomCommandDialog
from command_completer import CommandCompleter
from tools import Tools

minecraft_server_jar = "paper.jar"
additional_exe = "update.exe"
custom_command_file = "start.txt"

class MinecraftServerManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("梦幻我的世界服务器管理面板")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("./app_icon.ico"))

        # 使用 Fusion 样式
        self.app = QApplication.instance() or QApplication([])
        self.app.setStyle("Fusion")

        # 创建字体对象
        font = self.create_font()

        # 创建按钮样式
        self.setStyleSheet(self.create_button_style())

        self.create_widgets(font)
        self.create_layouts()
        self.create_connections()

        self.process = None
        self.special_feature_dialog = Tools(self)

        try:
            self.start_additional_script()
        except Exception as e:
            print(f"Error: {e}")

        atexit.register(self.closeEvent)

    def create_font(self):
        font = QFont()
        font.setFamily("微软雅黑")  # 设置字体族
        font.setPointSize(12)  # 设置字体大小
        return font

    def create_button_style(self):
        return (
            "QPushButton { background-color: #3498db; color: white; border: none; "
            "padding: 10px; border-radius: 5px; }"
            "QPushButton:hover { background-color: #2980b9; }"
        )

    def create_widgets(self, font):
        self.create_buttons(font)
        self.create_input_output_widgets(font)
        self.create_combobox(font)

        # 创建自动完成器并关联到输入文本框
        self.create_command_completer()

    def create_buttons(self, font):
        self.start_button = self.create_button("启动服务器", self.on_start_button_click, font)
        self.stop_button = self.create_button("停止服务器", self.on_stop_button_click, font)
        self.custom_command_button = self.create_button("自定义启动命令", self.on_custom_command_button_click, font)
        self.special_feature_button = self.create_button("工具", self.open_special_feature_dialog, font)

    def create_button(self, text, on_click, font):
        button = QPushButton(text)
        self.set_button_font(button, 16, font)
        button.clicked.connect(on_click)
        return button

    def create_input_output_widgets(self, font):
        self.input_text = self.create_text_input(font)
        self.output_widget = self.create_text_output(font)

    def create_text_input(self, font):
        input_text = QLineEdit()
        input_text.returnPressed.connect(self.send_command)
        self.set_widget_font(input_text, 14, font)
        return input_text

    def create_text_output(self, font):
        output_widget = QPlainTextEdit()
        output_widget.setReadOnly(True)
        output_widget.setFocusPolicy(Qt.StrongFocus)
        output_widget.setFocus()
        self.set_widget_font(output_widget, 14, font)
        return output_widget

    def create_combobox(self, font):
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(["12", "14", "16", "18", "20"])
        self.font_size_combo.currentIndexChanged.connect(self.change_font_size)

    def create_layouts(self):
        buttons_layout = self.create_buttons_layout()

        main_layout = self.create_main_layout(buttons_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def create_buttons_layout(self):
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.stop_button)
        buttons_layout.addWidget(self.custom_command_button)
        buttons_layout.addWidget(self.special_feature_button)
        return buttons_layout

    def create_main_layout(self, buttons_layout):
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.output_widget)
        main_layout.addWidget(self.input_text)
        main_layout.addWidget(self.font_size_combo)
        main_layout.addLayout(buttons_layout)
        return main_layout

    def create_command_completer(self):
        # 获取Minecraft服务器命令列表
        minecraft_commands = ["help", "start", "stop", "reload", "say", "list", "..."]
        completer = CommandCompleter(minecraft_commands, self.input_text)
        self.input_text.setCompleter(completer)

    def create_connections(self):
        self.system_resource_thread = SystemResourceThread()
        self.system_resource_thread.system_resource_signal.connect(self.update_system_resource)
        self.system_resource_thread.start()

    def set_button_font(self, button, font_size, font):
        button.setFont(font)
        button.setProperty("opacity", 1.0)
        button.setStyleSheet(
            f"QPushButton {{ background-color: #3498db; color: white; border: none; "
            f"padding: 10px; border-radius: 5px; font-size: {font_size}px; }}"
            f"QPushButton:hover {{ background-color: #2980b9; }}"
        )

    def set_widget_font(self, widget, font_size, font):
        font.setPointSize(font_size)
        widget.setFont(font)

    def update_system_resource(self, cpu_percent, memory_percent):
        self.statusBar().showMessage(f"CPU占用：{cpu_percent}%  内存占用：{memory_percent}%")

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

    def on_custom_command_button_click(self):
        dialog = CustomCommandDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            QMessageBox.information(self, '保存成功', '自定义命令已成功保存！')

    @pyqtSlot()
    def open_special_feature_dialog(self):
        self.special_feature_dialog.show()

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
