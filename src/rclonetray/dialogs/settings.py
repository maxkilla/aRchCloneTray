"""Settings dialog"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                           QWidget, QFormLayout, QLineEdit, QSpinBox,
                           QCheckBox, QComboBox, QPushButton, QLabel,
                           QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSlot
from pathlib import Path

class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle('RcloneTray Settings')
        self.setMinimumWidth(600)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Create tab widget
        tabs = QTabWidget()
        tabs.addTab(self.create_general_tab(), "General")
        tabs.addTab(self.create_mount_tab(), "Mount")
        tabs.addTab(self.create_network_tab(), "Network")
        tabs.addTab(self.create_advanced_tab(), "Advanced")
        layout.addWidget(tabs)
        
        # Buttons
        buttons = QHBoxLayout()
        
        # Import/Export buttons
        import_btn = QPushButton("Import Settings")
        import_btn.clicked.connect(self.import_settings)
        export_btn = QPushButton("Export Settings")
        export_btn.clicked.connect(self.export_settings)
        buttons.addWidget(import_btn)
        buttons.addWidget(export_btn)
        
        buttons.addStretch()
        
        # Save/Cancel buttons
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        
        layout.addLayout(buttons)
        self.setLayout(layout)

    def create_general_tab(self):
        tab = QWidget()
        layout = QFormLayout()
        
        # Interface settings
        self.start_minimized = QCheckBox()
        self.start_minimized.setChecked(str(self.config.get('start_minimized', True)).lower() == 'true')
        layout.addRow("Start Minimized:", self.start_minimized)
        
        self.show_notifications = QCheckBox()
        self.show_notifications.setChecked(str(self.config.get('show_notifications', True)).lower() == 'true')
        layout.addRow("Show Notifications:", self.show_notifications)
        
        self.dark_mode = QCheckBox()
        self.dark_mode.setChecked(str(self.config.get('dark_mode', True)).lower() == 'true')
        layout.addRow("Dark Mode:", self.dark_mode)
        
        self.minimize_to_tray = QCheckBox()
        self.minimize_to_tray.setChecked(str(self.config.get('minimize_to_tray', True)).lower() == 'true')
        layout.addRow("Minimize to Tray:", self.minimize_to_tray)
        
        tab.setLayout(layout)
        return tab

    def create_mount_tab(self):
        tab = QWidget()
        layout = QFormLayout()
        
        # Mount settings
        self.mount_base_dir = QLineEdit(self.config.get('mount_base_dir'))
        layout.addRow("Base Mount Directory:", self.mount_base_dir)
        
        self.mount_options = QLineEdit(self.config.get('mount_options'))
        layout.addRow("Default Mount Options:", self.mount_options)
        
        self.auto_mount = QCheckBox()
        self.auto_mount.setChecked(str(self.config.get('auto_mount', False)).lower() == 'true')
        layout.addRow("Auto Mount:", self.auto_mount)
        
        self.mount_on_startup = QCheckBox()
        self.mount_on_startup.setChecked(str(self.config.get('mount_on_startup', False)).lower() == 'true')
        layout.addRow("Mount on Startup:", self.mount_on_startup)
        
        tab.setLayout(layout)
        return tab

    def create_network_tab(self):
        tab = QWidget()
        layout = QFormLayout()
        
        # Network settings
        self.bandwidth_limit = QLineEdit(self.config.get('bandwidth_limit'))
        layout.addRow("Bandwidth Limit (0 for unlimited):", self.bandwidth_limit)
        
        self.timeout = QSpinBox()
        self.timeout.setRange(1, 3600)
        self.timeout.setValue(self.config.get('timeout', 30))
        layout.addRow("Timeout (seconds):", self.timeout)
        
        self.retries = QSpinBox()
        self.retries.setRange(0, 100)
        self.retries.setValue(self.config.get('retries', 3))
        layout.addRow("Retries:", self.retries)
        
        self.low_level_retries = QSpinBox()
        self.low_level_retries.setRange(0, 100)
        self.low_level_retries.setValue(self.config.get('low_level_retries', 10))
        layout.addRow("Low Level Retries:", self.low_level_retries)
        
        tab.setLayout(layout)
        return tab

    def create_advanced_tab(self):
        tab = QWidget()
        layout = QFormLayout()
        
        # Advanced settings
        self.rclone_path = QLineEdit(self.config.get('rclone_path'))
        layout.addRow("Rclone Path:", self.rclone_path)
        
        self.config_path = QLineEdit(self.config.get('config_path'))
        layout.addRow("Config Path:", self.config_path)
        
        self.log_level = QComboBox()
        self.log_level.addItems(['DEBUG', 'INFO', 'WARNING', 'ERROR'])
        self.log_level.setCurrentText(self.config.get('log_level', 'INFO'))
        layout.addRow("Log Level:", self.log_level)
        
        self.buffer_size = QLineEdit(self.config.get('buffer_size'))
        layout.addRow("Buffer Size:", self.buffer_size)
        
        self.transfers = QSpinBox()
        self.transfers.setRange(1, 32)
        self.transfers.setValue(self.config.get('transfers', 4))
        layout.addRow("Concurrent Transfers:", self.transfers)
        
        tab.setLayout(layout)
        return tab

    @pyqtSlot()
    def save_settings(self):
        # General settings
        self.config.set('start_minimized', str(self.start_minimized.isChecked()))
        self.config.set('show_notifications', str(self.show_notifications.isChecked()))
        self.config.set('dark_mode', str(self.dark_mode.isChecked()))
        self.config.set('minimize_to_tray', str(self.minimize_to_tray.isChecked()))
        
        # Mount settings
        self.config.set('mount_base_dir', self.mount_base_dir.text())
        self.config.set('mount_options', self.mount_options.text())
        self.config.set('auto_mount', str(self.auto_mount.isChecked()))
        self.config.set('mount_on_startup', str(self.mount_on_startup.isChecked()))
        
        # Network settings
        self.config.set('bandwidth_limit', self.bandwidth_limit.text())
        self.config.set('timeout', self.timeout.value())
        self.config.set('retries', self.retries.value())
        self.config.set('low_level_retries', self.low_level_retries.value())
        
        # Advanced settings
        self.config.set('rclone_path', self.rclone_path.text())
        self.config.set('config_path', self.config_path.text())
        self.config.set('log_level', self.log_level.currentText())
        self.config.set('buffer_size', self.buffer_size.text())
        self.config.set('transfers', self.transfers.value())
        
        self.accept()

    @pyqtSlot()
    def import_settings(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Settings",
            str(Path.home()),
            "JSON Files (*.json)"
        )
        if file_path:
            try:
                self.config.import_settings(Path(file_path))
                QMessageBox.information(self, "Success", "Settings imported successfully")
                self.accept()  # Close and reopen to show new settings
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import settings: {e}")

    @pyqtSlot()
    def export_settings(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Settings",
            str(Path.home() / "rclonetray_settings.json"),
            "JSON Files (*.json)"
        )
        if file_path:
            try:
                self.config.export_settings(Path(file_path))
                QMessageBox.information(self, "Success", "Settings exported successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export settings: {e}")
