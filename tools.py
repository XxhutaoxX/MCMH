import time
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QCheckBox

class Tools(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("特色功能窗口")

        self.restart_count = 0
        self.max_restart_attempts = 5
        self.restart_interval = 300  # 5分钟

        self.auto_restart_checkbox = QCheckBox("自动重启服务器功能")
        self.auto_restart_checkbox.setChecked(True)  # 默认启用自动重启
        self.auto_restart_checkbox.stateChanged.connect(self.check_server_status)

        layout = QVBoxLayout()
        label = QLabel("这是特色功能窗口的内容")
        layout.addWidget(label)
        layout.addWidget(self.auto_restart_checkbox)
        self.setLayout(layout)

    def check_server_status(self, state):
        if state == 0:
            print("自动重启服务器功能已禁用")
        else:
            print("自动重启服务器功能已启用")
            self.restart_server()

    def restart_server(self):
        print("尝试重启服务器...")
        server_crashed = True  # 模拟服务器崩溃，实际情况根据需求修改

        if server_crashed:
            print("服务器崩溃，尝试重启...")
            self.restart_count += 1
            if self.restart_count >= self.max_restart_attempts:
                print("连续重启次数达到上限，暂停重启。")
                # 在这里可以添加暂停重启的逻辑，例如发送通知、记录日志等
            else:
                # 等待重启间隔
                time.sleep(self.restart_interval)
                self.restart_server()
        else:
            self.restart_count = 0  # 服务器正常运行，重置计数器
