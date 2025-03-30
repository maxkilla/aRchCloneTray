from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton
from PySide6.QtCore import Qt

class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Preferences')
        self.init_ui()

    def init_ui(self):
        # Main layout
        layout = QVBoxLayout()
        form = QFormLayout()

        # Remote path
        self.remote_path = QLineEdit()
        form.addRow('Remote Path:', self.remote_path)

        # Mount point
        self.mount_point = QLineEdit()
        form.addRow('Mount Point:', self.mount_point)

        # Add form to main layout
        layout.addLayout(form)

        # Buttons
        buttons = QVBoxLayout()
        save_button = QPushButton('Save')
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(save_button)
        buttons.addWidget(cancel_button)
        layout.addLayout(buttons)

        self.setLayout(layout)
