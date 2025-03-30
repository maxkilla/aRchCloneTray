from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('About RcloneTray')
        self.init_ui()

    def init_ui(self):
        # Main layout
        layout = QVBoxLayout()

        # Logo
        logo = QLabel()
        logo.setPixmap(QPixmap('../ui/icons/icon.png').scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        # App name
        name = QLabel('RcloneTray')
        name.setAlignment(Qt.AlignCenter)
        layout.addWidget(name)

        # Version
        version = QLabel('Version 1.0.0')
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

        # Description
        desc = QLabel('A native KDE system tray application for Rclone')
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Close button
        close_btn = QPushButton('Close')
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)
