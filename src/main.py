#!/usr/bin/env python3
import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QObject, pyqtSignal as Signal, pyqtSlot as Slot, QProcess

class RcloneTray(QSystemTrayIcon):
    def __init__(self):
        super().__init__()
        self.rclone_process = None
        self.init_ui()

    def init_ui(self):
        # Set icon
        icon_path = str(Path(__file__).parent / 'ui' / 'icons' / 'icon.png')
        self.setIcon(QIcon(icon_path))
        self.setToolTip('RcloneTray')

        # Create menu
        self.menu = QMenu()
        self.menu.addAction('Mount', self.mount)
        self.menu.addAction('Unmount', self.unmount)
        self.menu.addSeparator()
        self.menu.addAction('Preferences', self.show_preferences)
        self.menu.addAction('About', self.show_about)
        self.menu.addSeparator()
        self.menu.addAction('Quit', self.quit_app)

        # Set context menu
        self.setContextMenu(self.menu)

        # Show tray icon
        self.show()

    @Slot()
    def mount(self):
        if not self.rclone_process:
            self.rclone_process = QProcess()
            self.rclone_process.start('rclone', ['mount', 'remote:/', '/mnt/rclone'])

    @Slot()
    def unmount(self):
        if self.rclone_process:
            self.rclone_process.terminate()
            self.rclone_process = None

    @Slot()
    def show_preferences(self):
        # TODO: Implement preferences dialog
        pass

    @Slot()
    def show_about(self):
        # TODO: Implement about dialog
        pass

    @Slot()
    def quit_app(self):
        self.unmount()
        QApplication.quit()

def main():
    # Enable Wayland support
    os.environ["QT_QPA_PLATFORM"] = "wayland;xcb"
    
    # Create application
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Set application metadata
    app.setApplicationName("RcloneTray")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("RcloneTray")
    app.setOrganizationDomain("rclonetray.org")
    
    # Create tray
    tray = RcloneTray()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
