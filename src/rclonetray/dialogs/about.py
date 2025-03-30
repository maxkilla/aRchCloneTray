"""About dialog"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton,
                             QSpacerItem, QSizePolicy, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont
from pathlib import Path

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('About aRchCloneTray')
        self.setFixedWidth(500)
        self.setMinimumHeight(600)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)  # Clean up on close
        self.init_ui()

    def init_ui(self):
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Logo
        icon_path = Path(__file__).parent.parent.parent / 'ui' / 'icons' / 'icon.png'
        if icon_path.exists():
            logo = QLabel()
            logo.setPixmap(QPixmap(str(icon_path)).scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(logo)

        # App name
        name = QLabel('aRchCloneTray')
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        name.setFont(font)
        layout.addWidget(name)

        # Version
        version = QLabel('Version 2.0.0')
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)

        # Description
        desc = QLabel(
            'A modern PyQt6-based system tray application for Rclone'
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet('font-size: 12pt;')
        layout.addWidget(desc)
        
        # Detailed description
        details = QLabel(
            'aRchCloneTray provides seamless integration with Linux desktop\n'
            'environments, offering advanced mount management and\n'
            'real-time monitoring.'
        )
        details.setAlignment(Qt.AlignmentFlag.AlignCenter)
        details.setWordWrap(True)
        details.setStyleSheet('color: #666666;')
        layout.addWidget(details)

        # Add some spacing
        layout.addSpacing(20)

        # Features section title
        features_title = QLabel('Key Features')
        features_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        features_title.setStyleSheet('font-size: 14pt; font-weight: bold; margin-top: 20px;')
        layout.addWidget(features_title)
        
        # Features
        features = QLabel(
            '• Real-time mount management\n'
            '• System statistics and monitoring\n'
            '• Modern user interface\n'
            '• Advanced mount options\n'
            '• Native desktop notifications\n'
            '• Dark mode support'
        )
        features.setAlignment(Qt.AlignmentFlag.AlignLeft)
        features.setStyleSheet('margin: 10px 40px; font-size: 11pt;')
        layout.addWidget(features)
        
        # Spacer
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Links section
        links_frame = QFrame()
        links_frame.setStyleSheet('background-color: rgba(0, 0, 0, 0.05); border-radius: 5px; padding: 10px;')
        links_layout = QVBoxLayout(links_frame)
        
        links = QLabel(
            'GitHub: <a style="color: #0366d6;" href="https://github.com/maxkilla/aRchCloneTray">maxkilla/aRchCloneTray</a><br>'
            'Rclone: <a style="color: #0366d6;" href="https://rclone.org">rclone.org</a>'
        )
        links.setOpenExternalLinks(True)
        links.setAlignment(Qt.AlignmentFlag.AlignCenter)
        links.setStyleSheet('font-size: 11pt;')
        links_layout.addWidget(links)
        
        layout.addWidget(links_frame)
        
        # Copyright
        copyright = QLabel('© 2025 Matt Scott')
        copyright.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(copyright)
        
        # Close button
        close_btn = QPushButton('Close')
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)
