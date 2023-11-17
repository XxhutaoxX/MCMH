from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCompleter

class CommandCompleter(QCompleter):
    def __init__(self, commands, parent=None):
        super().__init__(commands, parent)
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setFilterMode(Qt.MatchContains)
