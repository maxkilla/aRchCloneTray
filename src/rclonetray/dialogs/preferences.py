"""Preferences dialog"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, 
                           QLineEdit, QPushButton, QLabel)
from PyQt6.QtCore import Qt
from pathlib import Path

class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('RcloneTray Preferences')
        self.setMinimumWidth(400)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)  # Clean up on close
        self.init_ui()

    def init_ui(self):
        # Main layout
        layout = QVBoxLayout()
        form = QFormLayout()

        # Mount directory
        self.mount_dir = QLineEdit(str(Path.home() / 'mnt'))
        form.addRow('Default Mount Directory:', self.mount_dir)

        # Rclone config path
        self.config_path = QLineEdit(str(Path.home() / '.config' / 'rclone' / 'rclone.conf'))
        form.addRow('Rclone Config:', self.config_path)

        # Mount options
        self.mount_opts = QLineEdit('--vfs-cache-mode=full')
        form.addRow('Mount Options:', self.mount_opts)

        # Add form to main layout
        layout.addLayout(form)

        # Add some spacing
        layout.addSpacing(20)

        # Help text
        help_text = QLabel(
            "Note: Changes will take effect after restarting RcloneTray\n"
            "Mount options are passed directly to rclone mount command"
        )
        help_text.setWordWrap(True)
        layout.addWidget(help_text)

        # Buttons
        button_layout = QVBoxLayout()
        save_button = QPushButton('Save')
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)
