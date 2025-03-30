"""New Remote Dialog"""

import subprocess
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                           QLabel, QComboBox, QLineEdit, QFormLayout,
                           QGroupBox, QMessageBox, QScrollArea, QWidget)
from PyQt6.QtCore import Qt

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
            
    def configure_remote(self):
        """Configure the selected remote"""
        name = self.name_edit.text().strip()
        provider = self.provider_combo.currentText()
        
        if not name:
            QMessageBox.warning(self, "Error", "Please enter a name for the remote")
            return
            
        try:
            # Try different terminal emulators
            terminals = ['konsole', 'gnome-terminal', 'xterm']
            cmd = None
            
            for term in terminals:
                if subprocess.run(['which', term], capture_output=True).returncode == 0:
                    if term == 'konsole':
                        cmd = [term, '-e', 'rclone', 'config', 'create', name, provider]
                    elif term == 'gnome-terminal':
                        cmd = [term, '--', 'rclone', 'config', 'create', name, provider]
                    else:
                        cmd = [term, '-e', f'rclone config create {name} {provider}']
                    break
            
            if cmd:
                subprocess.Popen(cmd)
                self.accept()  # Close dialog
            else:
                QMessageBox.critical(self, "Error", "No suitable terminal emulator found")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to configure remote: {e}")