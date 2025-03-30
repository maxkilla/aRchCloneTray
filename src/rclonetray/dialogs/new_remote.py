"""New Remote Dialog"""

import subprocess
import logging
import os
import sys
import shutil
from pathlib import Path
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                           QLabel, QComboBox, QLineEdit, QFormLayout,
                           QGroupBox, QMessageBox, QScrollArea, QWidget)
from PyQt6.QtCore import Qt

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Rclone providers and their descriptions
PROVIDERS = {
    "1Fichier": "1Fichier file sharing",
    "Alibaba": "Alibaba Cloud (Aliyun) Object Storage System (OSS)",
    "Amazon Drive": "Amazon Drive",
    "Amazon S3": "Amazon S3 and compatible",
    "Backblaze B2": "Backblaze B2",
    "Box": "Box",
    "Dropbox": "Dropbox",
    "Enterprise File Fabric": "Enterprise File Fabric",
    "FTP": "FTP",
    "Google Cloud Storage": "Google Cloud Storage",
    "Google Drive": "Google Drive",
    "Google Photos": "Google Photos",
    "HDFS": "Hadoop distributed file system",
    "HTTP": "HTTP",
    "Internet Archive": "Internet Archive",
    "Jottacloud": "Jottacloud",
    "Mail.ru Cloud": "Mail.ru Cloud",
    "Mega": "Mega",
    "Microsoft Azure Blob Storage": "Microsoft Azure Blob Storage",
    "Microsoft OneDrive": "Microsoft OneDrive",
    "OpenDrive": "OpenDrive",
    "OpenStack Swift": "OpenStack Swift (Rackspace Cloud Files, Memset Memstore, OVH)",
    "Oracle Cloud": "Oracle Cloud Infrastructure Object Storage",
    "pCloud": "pCloud",
    "premiumize.me": "premiumize.me",
    "Put.io": "Put.io",
    "QingStor": "QingStor Object Storage",
    "SFTP": "SFTP",
    "Sia": "Sia decentralized cloud",
    "SMB": "SMB / CIFS",
    "Storj": "Storj Decentralized Cloud Storage",
    "Sugarsync": "Sugarsync",
    "Uptobox": "Uptobox",
    "WebDAV": "WebDAV",
    "Yandex Disk": "Yandex Disk",
}

# Mapping from display names to rclone backend names
PROVIDER_BACKEND_NAMES = {
    "1Fichier": "fichier",
    "Alibaba": "alibabacloud",
    "Amazon Drive": "amazon cloud drive",
    "Amazon S3": "s3",
    "Backblaze B2": "b2",
    "Box": "box",
    "Dropbox": "dropbox",
    "Enterprise File Fabric": "filefabric",
    "FTP": "ftp",
    "Google Cloud Storage": "google cloud storage",
    "Google Drive": "drive",
    "Google Photos": "google photos",
    "HDFS": "hdfs",
    "HTTP": "http",
    "Internet Archive": "internetarchive",
    "Jottacloud": "jottacloud",
    "Mail.ru Cloud": "mailru",
    "Mega": "mega",
    "Microsoft Azure Blob Storage": "azureblob",
    "Microsoft OneDrive": "onedrive",
    "OpenDrive": "opendrive",
    "OpenStack Swift": "swift",
    "Oracle Cloud": "oraclecloud",
    "pCloud": "pcloud",
    "premiumize.me": "premiumizeme",
    "Put.io": "putio",
    "QingStor": "qingstor",
    "SFTP": "sftp",
    "Sia": "sia",
    "SMB": "smb",
    "Storj": "storj",
    "Sugarsync": "sugarsync",
    "Uptobox": "uptobox",
    "WebDAV": "webdav",
    "Yandex Disk": "yandex"
}

class NewRemoteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Add New Remote')
        self.setMinimumSize(600, 400)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Provider selection section
        provider_group = QGroupBox("Select Provider")
        provider_layout = QFormLayout()
        
        # Remote name input
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter a name for this remote")
        provider_layout.addRow("Remote Name:", self.name_edit)
        
        # Provider dropdown
        self.provider_combo = QComboBox()
        for provider in sorted(PROVIDERS.keys()):
            self.provider_combo.addItem(provider, PROVIDERS[provider])
        provider_layout.addRow("Provider:", self.provider_combo)
        
        # Provider description
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        provider_layout.addRow("Description:", self.description_label)
        
        provider_group.setLayout(provider_layout)
        layout.addWidget(provider_group)
        
        # Provider documentation
        doc_group = QGroupBox("Provider Documentation")
        doc_layout = QVBoxLayout()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        doc_content = QWidget()
        doc_content_layout = QVBoxLayout()
        
        self.doc_label = QLabel()
        self.doc_label.setWordWrap(True)
        self.doc_label.setTextFormat(Qt.TextFormat.RichText)
        self.doc_label.setMinimumWidth(500)
        doc_content_layout.addWidget(self.doc_label)
        
        doc_content.setLayout(doc_content_layout)
        scroll.setWidget(doc_content)
        doc_layout.addWidget(scroll)
        
        doc_group.setLayout(doc_layout)
        layout.addWidget(doc_group)
        
        # Buttons
        buttons = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)
        
        buttons.addStretch()
        
        self.configure_btn = QPushButton("Configure")
        self.configure_btn.clicked.connect(self.configure_remote)
        self.configure_btn.setDefault(True)
        buttons.addWidget(self.configure_btn)
        
        layout.addLayout(buttons)
        self.setLayout(layout)
        
        # Initialize with first provider's description
        self.update_description(self.provider_combo.currentText())
        
        # Connect signal using a direct slot
        self.provider_combo.currentIndexChanged.connect(self.on_provider_changed)

    def __del__(self):
        """Clean up signal connections"""
        try:
            self.provider_combo.currentIndexChanged.disconnect(self.on_provider_changed)
        except:
            pass

    def on_provider_changed(self, _):
        """Handle provider selection change"""
        self.update_description(self.provider_combo.currentText())
        
    def update_description(self, provider):
        """Update the provider description and documentation"""
        # Update basic description
        description = PROVIDERS.get(provider, "")
        self.description_label.setText(description)
        
        # Fetch and display provider documentation
        try:
            # Get detailed provider info
            output = subprocess.check_output(
                ['rclone', 'config', 'providers', provider, '--help'],
                text=True
            )
            
            # Process and format the documentation
            docs = []
            in_description = False
            
            for line in output.split('\n'):
                if line.strip() == "Description:":
                    in_description = True
                    continue
                if in_description:
                    if not line.strip():  # Empty line marks end of description
                        in_description = False
                    else:
                        docs.append(line.strip())
            
            # Add configuration options section
            if "Configuration:" in output:
                docs.extend([
                    "",
                    "<b>Configuration Options:</b>",
                    ""
                ])
                config_section = output.split("Configuration:")[1]
                for line in config_section.split('\n'):
                    if line.strip():
                        docs.append(line.strip())
            
            # Format documentation with HTML
            formatted_docs = "<br>".join(docs)
            formatted_docs = formatted_docs.replace("*", "•")  # Convert asterisks to bullets
            
            self.doc_label.setText(formatted_docs)
            
        except subprocess.CalledProcessError as e:
            self.doc_label.setText(
                f"Could not fetch provider documentation. Basic configuration will be available in the next step.\n\n"
                f"Error: {e.output.decode() if e.output else str(e)}"
            )
            
    def check_dependencies(self):
        """Check if required dependencies are available"""
        missing_deps = []
        
        # Check for rclone
        if not shutil.which('rclone'):
            missing_deps.append('rclone')
            
        # Check for FUSE
        try:
            subprocess.run(['fusermount', '-V'], capture_output=True)
        except FileNotFoundError:
            missing_deps.append('fuse3')
            
        return missing_deps

    def configure_remote(self):
        """Configure the selected remote"""
        # Check dependencies first
        missing_deps = self.check_dependencies()
        if missing_deps:
            deps_str = ", ".join(missing_deps)
            logger.error(f"Missing dependencies: {deps_str}")
            QMessageBox.critical(self, "Error", 
                               f"Missing required dependencies: {deps_str}\n"
                               "Please install them using your package manager.")
            return
            
        name = self.name_edit.text().strip()
        display_provider = self.provider_combo.currentText()
        
        # Convert display name to rclone backend name
        provider = PROVIDER_BACKEND_NAMES.get(display_provider)
        if not provider:
            logger.error(f"No backend mapping found for provider: {display_provider}")
            QMessageBox.critical(self, "Error", f"Unknown provider type: {display_provider}")
            return
            
        logger.debug(f"Attempting to configure remote - Name: {name}, Display Provider: {display_provider}, Backend: {provider}")
        
        if not name:
            logger.warning("Remote name is empty")
            QMessageBox.warning(self, "Error", "Please enter a name for the remote")
            return
            
        try:
            # Get the virtual environment path if we're in one
            venv_path = os.environ.get('VIRTUAL_ENV')
            logger.debug(f"Virtual environment path: {venv_path}")
            
            # Try different terminal emulators
            terminals = ['konsole', 'gnome-terminal', 'xterm']
            cmd = None
            
            for term in terminals:
                logger.debug(f"Checking for terminal emulator: {term}")
                which_result = subprocess.run(['which', term], capture_output=True)
                
                if which_result.returncode == 0:
                    logger.info(f"Found terminal emulator: {term}")
                    
                    # Base rclone command
                    rclone_cmd = f"rclone config create {name} {provider}"
                    
                    # If we're in a virtual environment, we need to activate it
                    if venv_path:
                        # Create a script that activates venv, runs rclone, and keeps terminal open
                        script_content = f"""#!/bin/bash
source "{venv_path}/bin/activate"
{rclone_cmd}
echo "Press Enter to close this window..."
read
"""
                        # Create temporary script
                        script_path = os.path.join(venv_path, 'temp_rclone_config.sh')
                        with open(script_path, 'w') as f:
                            f.write(script_content)
                        os.chmod(script_path, 0o755)
                        
                        if term == 'konsole':
                            cmd = [term, '-e', script_path]
                        elif term == 'gnome-terminal':
                            cmd = [term, '--', script_path]
                        else:  # xterm
                            cmd = [term, '-e', script_path]
                    else:
                        # Without venv, just run rclone and keep terminal open
                        script_content = f"""#!/bin/bash
{rclone_cmd}
echo "Press Enter to close this window..."
read
"""
                        # Create temporary script in /tmp
                        script_path = '/tmp/temp_rclone_config.sh'
                        with open(script_path, 'w') as f:
                            f.write(script_content)
                        os.chmod(script_path, 0o755)
                        
                        if term == 'konsole':
                            cmd = [term, '-e', script_path]
                        elif term == 'gnome-terminal':
                            cmd = [term, '--', script_path]
                        else:  # xterm
                            cmd = [term, '-e', script_path]
                    break
                else:
                    logger.debug(f"Terminal {term} not found: {which_result.stderr.decode()}")
            
            if cmd:
                logger.info(f"Executing command: {' '.join(cmd)}")
                try:
                    process = subprocess.Popen(cmd)
                    logger.debug(f"Process started with PID: {process.pid}")
                    
                    # Clean up the temporary script after a delay
                    def cleanup_script():
                        import time
                        time.sleep(2)  # Wait for terminal to start
                        try:
                            os.remove(script_path)
                            logger.debug(f"Cleaned up temporary script: {script_path}")
                        except Exception as e:
                            logger.warning(f"Failed to clean up script: {e}")
                    
                    from threading import Thread
                    cleanup_thread = Thread(target=cleanup_script)
                    cleanup_thread.daemon = True
                    cleanup_thread.start()
                    
                    self.accept()  # Close dialog
                except subprocess.SubprocessError as se:
                    logger.error(f"Failed to execute terminal command: {se}")
                    if os.path.exists(script_path):
                        os.remove(script_path)
                    raise
            else:
                logger.error("No suitable terminal emulator found")
                QMessageBox.critical(self, "Error", 
                                   "No suitable terminal emulator found.\n"
                                   "Please install konsole, gnome-terminal, or xterm.")
        except Exception as e:
            logger.error(f"Failed to configure remote: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to configure remote: {e}")