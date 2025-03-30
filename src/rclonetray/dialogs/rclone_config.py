"""Rclone configuration dialog"""

import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                           QTextEdit, QMessageBox, QLabel, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont
from .new_remote import NewRemoteDialog

class RcloneConfigDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.app_config = config
        self.setWindowTitle('Rclone Configuration')
        self.setMinimumSize(800, 600)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.new_remote_dialog = None  # Keep reference to prevent premature cleanup
        self.init_ui()
        self.load_config()

    def init_ui(self):
        layout = QVBoxLayout()

        # Add help text
        help_text = QLabel(
            "Edit your rclone configuration below. You can also use the buttons to:\n"
            "- Run 'rclone config' in a terminal for interactive configuration\n"
            "- Import an existing config file\n"
            "- Create a new remote using the interactive wizard"
        )
        help_text.setWordWrap(True)
        layout.addWidget(help_text)

        # Config text editor
        self.editor = QTextEdit()
        self.editor.setFont(QFont('monospace'))
        layout.addWidget(self.editor)

        # Buttons
        button_layout = QHBoxLayout()

        # Left-side buttons
        left_buttons = QHBoxLayout()
        self.run_config_btn = QPushButton("Run rclone config")
        self.run_config_btn.clicked.connect(self.run_rclone_config)
        left_buttons.addWidget(self.run_config_btn)

        self.new_remote_btn = QPushButton("New Remote")
        self.new_remote_btn.clicked.connect(self.new_remote)
        left_buttons.addWidget(self.new_remote_btn)

        self.import_btn = QPushButton("Import Config")
        self.import_btn.clicked.connect(self.import_config)
        left_buttons.addWidget(self.import_btn)

        button_layout.addLayout(left_buttons)
        button_layout.addStretch()

        # Right-side buttons
        right_buttons = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_config)
        right_buttons.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        right_buttons.addWidget(self.cancel_btn)

        button_layout.addLayout(right_buttons)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_config(self):
        """Load the current rclone config"""
        config_path = Path(self.app_config.get('config_path'))
        if config_path.exists():
            self.editor.setPlainText(config_path.read_text())
        else:
            self.editor.setPlainText("# Rclone configuration file\n\n")

    @pyqtSlot()
    def save_config(self):
        """Save the config file"""
        try:
            config_path = Path(self.app_config.get('config_path'))
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(self.editor.toPlainText())
            QMessageBox.information(self, "Success", "Configuration saved successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {e}")

    @pyqtSlot()
    def run_rclone_config(self):
        """Run rclone config in a terminal"""
        try:
            # Try different terminal emulators
            terminals = ['konsole', 'gnome-terminal', 'xterm']
            cmd = None
            
            for term in terminals:
                if subprocess.run(['which', term], capture_output=True).returncode == 0:
                    if term == 'konsole':
                        cmd = [term, '-e', 'rclone', 'config']
                    elif term == 'gnome-terminal':
                        cmd = [term, '--', 'rclone', 'config']
                    else:
                        cmd = [term, '-e', 'rclone config']
                    break
            
            if cmd:
                subprocess.Popen(cmd)
                self.hide()  # Hide the dialog while using the terminal
            else:
                QMessageBox.critical(self, "Error", "No suitable terminal emulator found")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run rclone config: {e}")

    @pyqtSlot()
    def new_remote(self):
        """Create a new remote using the provider selection dialog"""
        dialog = NewRemoteDialog(parent=self)
        # Keep a reference to prevent premature cleanup
        self.new_remote_dialog = dialog
        if dialog.exec():
            # Reload config after new remote is configured
            self.load_config()
        # Clean up reference
        self.new_remote_dialog = None

    @pyqtSlot()
    def import_config(self):
        """Import config from a file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Rclone Config",
            str(Path.home()),
            "Rclone Config (rclone.conf);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path) as f:
                    self.editor.setPlainText(f.read())
                QMessageBox.information(self, "Success", "Configuration imported successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import configuration: {e}")

    def showEvent(self, event):
        """Reload config when dialog is shown"""
        super().showEvent(event)
        self.load_config()

    def closeEvent(self, event):
        """Handle dialog close"""
        if self.editor.document().isModified():
            reply = QMessageBox.question(
                self,
                "Save Changes?",
                "The configuration has been modified. Save changes?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                if self.save_config():
                    event.accept()
                else:
                    event.ignore()
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
        else:
            event.accept()
