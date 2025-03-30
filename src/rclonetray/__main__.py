"""Main entry point"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from .tray import RcloneTray

def main():
    # Enable Wayland support
    os.environ["QT_QPA_PLATFORM"] = "wayland;xcb"
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("RcloneTray")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("RcloneTray")
    app.setOrganizationDomain("rclonetray.org")
    
    # Don't quit when closing dialogs
    app.setQuitOnLastWindowClosed(False)
    
    # Create tray
    tray = RcloneTray(app)
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
