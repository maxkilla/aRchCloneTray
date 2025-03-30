"""System tray interface"""

from pathlib import Path
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QCursor
from PyQt6.QtCore import Qt, QObject
from .rclone import RcloneManager
from .dialogs import PreferencesDialog, AboutDialog, SettingsDialog, RcloneConfigDialog, DashboardDialog
from .config import Config

class RcloneTray(QSystemTrayIcon):
    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.config = Config()
        self.rclone = RcloneManager(self.config)
        self.init_ui()

    def init_ui(self):
        # Set icon
        icon_path = str(Path(__file__).parent.parent / 'ui' / 'icons' / 'icon.png')
        self.setIcon(QIcon(icon_path))
        self.setToolTip('RcloneTray')

        # Create menu
        self.menu = QMenu()
        self.build_menu()
        self.setContextMenu(self.menu)

        # Connect signals
        self.activated.connect(self.on_activated)

        # Show tray icon
        self.show()

    def build_menu(self):
        """Build the tray menu"""
        self.menu.clear()

        # Add remotes
        remotes = self.rclone.list_remotes()
        if remotes:
            for remote in remotes:
                remote_menu = self.menu.addMenu(remote)
                if remote in self.rclone.mounts:
                    remote_menu.addAction('Unmount', lambda: self.rclone.unmount(remote))
                else:
                    remote_menu.addAction('Mount', lambda: self.mount_remote(remote))
            self.menu.addSeparator()

        # Add standard items
        self.menu.addAction('Rclone Config', self.show_rclone_config)
        self.menu.addAction('Settings', self.show_settings)
        self.menu.addAction('About', self.show_about)
        self.menu.addSeparator()
        self.menu.addAction('Quit', self.quit_app)

    def mount_remote(self, remote: str):
        """Mount a remote"""
        mount_point = Path.home() / 'mnt' / remote
        mount_point.mkdir(parents=True, exist_ok=True)
        self.rclone.mount(remote, str(mount_point))
        self.build_menu()

    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self.config)
        if dialog.exec():
            self.build_menu()
            
    def show_rclone_config(self):
        """Show rclone config dialog"""
        dialog = RcloneConfigDialog(self.config)
        if dialog.exec():
            self.build_menu()
            
    def show_dashboard(self):
        """Show dashboard dialog"""
        dialog = DashboardDialog(self.config, self.rclone)
        dialog.exec()

    def show_about(self):
        """Show about dialog"""
        dialog = AboutDialog()
        dialog.exec()

    def on_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Left click - show dashboard
            self.show_dashboard()
        elif reason == QSystemTrayIcon.ActivationReason.Context:
            # Right click - show menu
            self.build_menu()
            cursor_pos = QCursor.pos()
            self.menu.popup(cursor_pos)

    def quit_app(self):
        """Quit the application"""
        self.rclone.cleanup()
        self.app.quit()
