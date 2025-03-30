"""Transfer Dialog"""

import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                           QLabel, QComboBox, QLineEdit, QFormLayout,
                           QGroupBox, QCheckBox)
from PyQt6.QtCore import Qt

class TransferDialog(QDialog):
    def __init__(self, operation_type, remotes, parent=None):
        super().__init__(parent)
        self.operation_type = operation_type  # 'sync' or 'copy'
        self.remotes = remotes
        self.setWindowTitle(f"New {operation_type.title()} Operation")
        self.setMinimumWidth(500)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Source selection
        source_group = QGroupBox("Source")
        source_layout = QFormLayout()
        
        self.source_remote = QComboBox()
        self.source_remote.addItems(self.remotes)
        source_layout.addRow("Remote:", self.source_remote)
        
        self.source_path = QLineEdit()
        self.source_path.setPlaceholderText("Path (optional)")
        source_layout.addRow("Path:", self.source_path)
        
        source_group.setLayout(source_layout)
        layout.addWidget(source_group)
        
        # Destination selection
        dest_group = QGroupBox("Destination")
        dest_layout = QFormLayout()
        
        self.dest_remote = QComboBox()
        self.dest_remote.addItems(self.remotes)
        dest_layout.addRow("Remote:", self.dest_remote)
        
        self.dest_path = QLineEdit()
        self.dest_path.setPlaceholderText("Path (optional)")
        dest_layout.addRow("Path:", self.dest_path)
        
        dest_group.setLayout(dest_layout)
        layout.addWidget(dest_group)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        
        # Common flags
        self.dry_run = QCheckBox("Dry Run (test without copying)")
        options_layout.addWidget(self.dry_run)
        
        self.verbose = QCheckBox("Verbose Output")
        options_layout.addWidget(self.verbose)
        
        self.update = QCheckBox("Skip files that are newer on destination")
        options_layout.addWidget(self.update)
        
        self.create_empty_dirs = QCheckBox("Create empty directories")
        options_layout.addWidget(self.create_empty_dirs)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Buttons
        buttons = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)
        
        buttons.addStretch()
        
        start_btn = QPushButton("Start")
        start_btn.clicked.connect(self.accept)
        start_btn.setDefault(True)
        buttons.addWidget(start_btn)
        
        layout.addLayout(buttons)
        self.setLayout(layout)
        
    def get_values(self):
        """Get dialog values"""
        source = f"{self.source_remote.currentText()}:"
        if self.source_path.text():
            source = os.path.join(source, self.source_path.text().lstrip('/'))
            
        dest = f"{self.dest_remote.currentText()}:"
        if self.dest_path.text():
            dest = os.path.join(dest, self.dest_path.text().lstrip('/'))
            
        # Build flags list
        flags = []
        if self.dry_run.isChecked():
            flags.append('--dry-run')
        if self.verbose.isChecked():
            flags.append('-v')
        if self.update.isChecked():
            flags.append('--update')
        if self.create_empty_dirs.isChecked():
            flags.append('--create-empty-dirs')
            
        return source, dest, flags