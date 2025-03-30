"""Rclone Dashboard Dialog"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                           QLabel, QTableWidget, QTableWidgetItem, QTabWidget,
                           QWidget, QProgressBar, QGroupBox, QFormLayout,
                           QScrollArea, QMenu, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
import psutil

class DashboardDialog(QDialog):
    def __init__(self, config, rclone_manager, parent=None):
        super().__init__(parent)
        self.config = config
        self.rclone = rclone_manager
        self.setWindowTitle('RcloneTray Dashboard')
        self.setMinimumSize(800, 600)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
        # Update timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(2000)  # Update every 2 seconds
        
        self.init_ui()
        self.update_stats()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Create tab widget
        tabs = QTabWidget()
        tabs.addTab(self.create_overview_tab(), "Overview")
        tabs.addTab(self.create_mounts_tab(), "Mounts")
        tabs.addTab(self.create_transfers_tab(), "Transfers")
        layout.addWidget(tabs)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.update_stats)
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def create_overview_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Remotes section
        remotes_group = QGroupBox("Configured Remotes")
        remotes_layout = QVBoxLayout()
        self.remotes_table = QTableWidget()
        self.remotes_table.setColumnCount(3)
        self.remotes_table.setHorizontalHeaderLabels(["Remote", "Type", "Status"])
        self.remotes_table.horizontalHeader().setStretchLastSection(True)
        self.remotes_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.remotes_table.customContextMenuRequested.connect(self.show_remote_context_menu)
        remotes_layout.addWidget(self.remotes_table)
        remotes_group.setLayout(remotes_layout)
        layout.addWidget(remotes_group)
        
        # System stats section
        stats_group = QGroupBox("System Statistics")
        stats_layout = QFormLayout()
        
        self.cpu_bar = QProgressBar()
        stats_layout.addRow("CPU Usage:", self.cpu_bar)
        
        self.memory_bar = QProgressBar()
        stats_layout.addRow("Memory Usage:", self.memory_bar)
        
        self.disk_label = QLabel()
        stats_layout.addRow("Disk Usage:", self.disk_label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        tab.setLayout(layout)
        return tab

    def create_mounts_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Available remotes group
        remotes_group = QGroupBox("Available Remotes")
        remotes_layout = QVBoxLayout()
        
        self.remotes_list = QTableWidget()
        self.remotes_list.setColumnCount(3)
        self.remotes_list.setHorizontalHeaderLabels(["Remote", "Type", "Actions"])
        self.remotes_list.horizontalHeader().setStretchLastSection(True)
        self.remotes_list.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        remotes_layout.addWidget(self.remotes_list)
        
        remotes_group.setLayout(remotes_layout)
        layout.addWidget(remotes_group)
        
        # Active mounts group
        mounts_group = QGroupBox("Active Mounts")
        mounts_layout = QVBoxLayout()
        
        self.mounts_table = QTableWidget()
        self.mounts_table.setColumnCount(4)
        self.mounts_table.setHorizontalHeaderLabels(["Remote", "Mount Point", "Status", "Actions"])
        self.mounts_table.horizontalHeader().setStretchLastSection(True)
        self.mounts_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.mounts_table.customContextMenuRequested.connect(self.show_mount_context_menu)
        self.mounts_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        mounts_layout.addWidget(self.mounts_table)
        
        mounts_group.setLayout(mounts_layout)
        layout.addWidget(mounts_group)
        
        # Controls
        controls = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.update_stats)
        controls.addWidget(refresh_btn)
        
        controls.addStretch()
        
        unmount_all_btn = QPushButton("Unmount All")
        unmount_all_btn.clicked.connect(self.unmount_all)
        controls.addWidget(unmount_all_btn)
        
        layout.addLayout(controls)
        tab.setLayout(layout)
        return tab

    def create_transfers_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Active transfers
        self.transfers_table = QTableWidget()
        self.transfers_table.setColumnCount(5)
        self.transfers_table.setHorizontalHeaderLabels(["Name", "Size", "Progress", "Speed", "ETA"])
        self.transfers_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.transfers_table)
        
        tab.setLayout(layout)
        return tab

    @pyqtSlot()
    def update_stats(self):
        """Update all statistics"""
        self.update_remotes()
        self.update_system_stats()
        self.update_mounts()
        self.update_transfers()

    def update_remotes(self):
        """Update remotes table"""
        try:
            remotes = self.rclone.list_remotes()
            self.remotes_table.setRowCount(len(remotes))
            
            for i, remote in enumerate(remotes):
                # Remote name
                self.remotes_table.setItem(i, 0, QTableWidgetItem(remote))
                
                # Remote type (get from rclone config show)
                try:
                    output = subprocess.check_output(['rclone', 'config', 'show', remote])
                    config = json.loads(output)
                    remote_type = config.get('type', 'Unknown')
                except:
                    remote_type = 'Unknown'
                self.remotes_table.setItem(i, 1, QTableWidgetItem(remote_type))
                
                # Status
                status = "Mounted" if self.rclone.is_mounted(remote) else "Not Mounted"
                status_item = QTableWidgetItem(status)
                status_item.setForeground(Qt.GlobalColor.green if status == "Mounted" else Qt.GlobalColor.red)
                self.remotes_table.setItem(i, 2, status_item)
        except Exception as e:
            print(f"Error updating remotes: {e}")

    def update_system_stats(self):
        """Update system statistics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent()
            self.cpu_bar.setValue(int(cpu_percent))
            self.cpu_bar.setFormat(f"{cpu_percent:.1f}%")
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.memory_bar.setValue(int(memory.percent))
            self.memory_bar.setFormat(f"{memory.percent:.1f}% ({memory.used / 1024**3:.1f}GB / {memory.total / 1024**3:.1f}GB)")
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.disk_label.setText(f"Used: {disk.used / 1024**3:.1f}GB / {disk.total / 1024**3:.1f}GB ({disk.percent}%)")
        except Exception as e:
            print(f"Error updating system stats: {e}")

    def update_mounts(self):
        """Update mounts tables"""
        try:
            # Update available remotes
            remotes = self.rclone.list_remotes()
            self.remotes_list.setRowCount(len(remotes))
            
            for i, remote in enumerate(remotes):
                # Remote name
                self.remotes_list.setItem(i, 0, QTableWidgetItem(remote))
                
                # Remote type
                try:
                    output = subprocess.check_output(['rclone', 'config', 'show', remote])
                    output_str = output.decode()
                    # Parse the output to find the type
                    for line in output_str.splitlines():
                        if line.strip().startswith('type = '):
                            remote_type = line.split('=')[1].strip()
                            break
                    else:
                        remote_type = 'Unknown'
                except:
                    remote_type = 'Unknown'
                self.remotes_list.setItem(i, 1, QTableWidgetItem(remote_type))
                
                # Mount button
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(2, 2, 2, 2)
                
                if self.rclone.is_mounted(remote):
                    unmount_btn = QPushButton("Unmount")
                    unmount_btn.clicked.connect(lambda r=remote: self.unmount_remote(r))
                    btn_layout.addWidget(unmount_btn)
                else:
                    mount_btn = QPushButton("Mount")
                    mount_btn.clicked.connect(lambda r=remote: self.mount_remote(r))
                    btn_layout.addWidget(mount_btn)
                
                btn_layout.addStretch()
                self.remotes_list.setCellWidget(i, 2, btn_widget)
            
            # Update active mounts
            active_mounts = []
            mnt_dir = Path.home() / 'mnt'
            if mnt_dir.exists():
                for mount_point in mnt_dir.iterdir():
                    if mount_point.is_mount():
                        active_mounts.append(mount_point.name)
            
            self.mounts_table.setRowCount(len(active_mounts))
            
            for i, remote in enumerate(active_mounts):
                # Remote name
                self.mounts_table.setItem(i, 0, QTableWidgetItem(remote))
                
                # Mount point
                mount_point = mnt_dir / remote
                self.mounts_table.setItem(i, 1, QTableWidgetItem(str(mount_point)))
                
                # Status
                is_mounted = self.rclone.verify_mount(str(mount_point))
                status = "Active" if is_mounted else "Error"
                status_item = QTableWidgetItem(status)
                status_item.setForeground(
                    Qt.GlobalColor.green if is_mounted else Qt.GlobalColor.red
                )
                self.mounts_table.setItem(i, 2, status_item)
                
                # Action buttons
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(2, 2, 2, 2)
                
                unmount_btn = QPushButton("Unmount")
                remote_name = remote  # Create a local copy
                unmount_btn.clicked.connect(lambda checked, r=remote_name: self.unmount_remote(r))
                btn_layout.addWidget(unmount_btn)
                
                open_btn = QPushButton("Open")
                open_btn.clicked.connect(lambda checked, r=remote_name: self.open_mount_point(r))
                btn_layout.addWidget(open_btn)
                
                btn_layout.addStretch()
                self.mounts_table.setCellWidget(i, 3, btn_widget)
            
            # Adjust column sizes
            self.remotes_list.resizeColumnsToContents()
            self.mounts_table.resizeColumnsToContents()
            
        except Exception as e:
            print(f"Error updating mounts: {e}")

    def update_transfers(self):
        """Update transfers table"""
        try:
            # Get transfer status using rclone rc
            transfers = []  # TODO: Implement rclone rc calls to get transfer status
            self.transfers_table.setRowCount(len(transfers))
            
            for i, transfer in enumerate(transfers):
                self.transfers_table.setItem(i, 0, QTableWidgetItem(transfer.get('name', '')))
                self.transfers_table.setItem(i, 1, QTableWidgetItem(transfer.get('size', '')))
                self.transfers_table.setItem(i, 2, QTableWidgetItem(transfer.get('progress', '')))
                self.transfers_table.setItem(i, 3, QTableWidgetItem(transfer.get('speed', '')))
                self.transfers_table.setItem(i, 4, QTableWidgetItem(transfer.get('eta', '')))
        except Exception as e:
            print(f"Error updating transfers: {e}")

    class MountThread(QThread):
        mount_finished = pyqtSignal(bool, str)  # Success, Error message
        
        def __init__(self, rclone, remote, mount_point):
            super().__init__()
            self.rclone = rclone
            self.remote = remote
            self.mount_point = mount_point
            
        def run(self):
            try:
                self.rclone.mount(self.remote, str(self.mount_point))
                self.mount_finished.emit(True, "")
            except Exception as e:
                self.mount_finished.emit(False, str(e))
    
    def mount_remote(self, remote):
        """Mount a remote"""
        try:
            mount_point = Path.home() / 'mnt' / remote
            mount_point.mkdir(parents=True, exist_ok=True)
            
            # Show mounting status
            self.status_dialog = QMessageBox(self)
            self.status_dialog.setWindowTitle("Mounting Remote")
            self.status_dialog.setText(f"Mounting {remote}...")
            self.status_dialog.setStandardButtons(QMessageBox.StandardButton.NoButton)
            self.status_dialog.show()
            
            # Mount in a separate thread to keep UI responsive
            self.mount_thread = self.MountThread(self.rclone, remote, mount_point)
            self.mount_thread.mount_finished.connect(self.on_mount_finished)
            self.mount_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to mount {remote}: {e}")
            
    def on_mount_finished(self, success, error):
        """Handle mount completion"""
        self.status_dialog.accept()
        
        if success:
            self.update_stats()
        else:
            QMessageBox.critical(self, "Error", f"Failed to mount remote: {error}")
            
    def unmount_remote(self, remote):
        """Unmount a remote"""
        try:
            if self.rclone.unmount(remote):
                self.update_stats()
            else:
                QMessageBox.warning(self, "Warning", f"Failed to unmount {remote}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error unmounting {remote}: {e}")
            
    def unmount_all(self):
        """Unmount all remotes"""
        mnt_dir = Path.home() / 'mnt'
        if not mnt_dir.exists():
            return
            
        for mount_point in mnt_dir.iterdir():
            if mount_point.is_mount():
                self.unmount_remote(mount_point.name)

    def unmount_selected(self):
        """Unmount selected remote"""
        selected = self.mounts_table.selectedItems()
        if not selected:
            return
        
        remote = selected[0].text()
        self.rclone.unmount(remote)
        self.update_stats()

    def show_remote_context_menu(self, pos):
        """Show context menu for remotes table"""
        item = self.remotes_table.itemAt(pos)
        if not item:
            return
            
        remote = self.remotes_table.item(item.row(), 0).text()
        menu = QMenu(self)
        
        # Add menu items based on mount status
        if remote in self.rclone.mounts:
            menu.addAction("Unmount", lambda: self.rclone.unmount(remote))
            menu.addAction("Remount", lambda: (self.rclone.unmount(remote), self.mount_remote(remote)))
        else:
            menu.addAction("Mount", lambda: self.mount_remote(remote))
        
        # Add general actions
        menu.addSeparator()
        menu.addAction("Configure", lambda: self.configure_remote(remote))
        menu.addAction("View Stats", lambda: self.view_remote_stats(remote))
        
        # Show menu at cursor position
        menu.exec(self.remotes_table.mapToGlobal(pos))
    
    def show_mount_context_menu(self, pos):
        """Show context menu for mounts table"""
        item = self.mounts_table.itemAt(pos)
        if not item:
            return
            
        remote = self.mounts_table.item(item.row(), 0).text()
        menu = QMenu(self)
        
        # Add mount management actions
        menu.addAction("Unmount", lambda: self.rclone.unmount(remote))
        menu.addAction("Remount", lambda: (self.rclone.unmount(remote), self.mount_remote(remote)))
        
        # Add mount utilities
        menu.addSeparator()
        menu.addAction("Open in File Manager", lambda: self.open_mount_point(remote))
        menu.addAction("View Stats", lambda: self.view_remote_stats(remote))
        menu.addAction("Check Mount", lambda: self.check_mount(remote))
        
        # Show menu at cursor position
        menu.exec(self.mounts_table.mapToGlobal(pos))
    
    def configure_remote(self, remote):
        """Open configuration for a remote"""
        try:
            terminals = ['konsole', 'gnome-terminal', 'xterm']
            cmd = None
            
            for term in terminals:
                if subprocess.run(['which', term], capture_output=True).returncode == 0:
                    if term == 'konsole':
                        cmd = [term, '-e', 'rclone', 'config', 'edit', remote]
                    elif term == 'gnome-terminal':
                        cmd = [term, '--', 'rclone', 'config', 'edit', remote]
                    else:
                        cmd = [term, '-e', f'rclone config edit {remote}']
                    break
            
            if cmd:
                subprocess.Popen(cmd)
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to configure {remote}: {e}")
    
    def view_remote_stats(self, remote):
        """View statistics for a remote"""
        try:
            output = subprocess.check_output(['rclone', 'about', f'{remote}:', '--json'])
            stats = json.loads(output)
            
            msg = f"Statistics for {remote}:\n\n"
            msg += f"Total: {self.format_size(stats.get('total', 0))}\n"
            msg += f"Used: {self.format_size(stats.get('used', 0))}\n"
            msg += f"Free: {self.format_size(stats.get('free', 0))}\n"
            msg += f"Usage: {stats.get('used%', '0')}%"
            
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, f"{remote} Statistics", msg)
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Warning", f"Could not get statistics for {remote}: {e}")
    
    def check_mount(self, remote):
        """Check if a mount is working properly"""
        mount_point = Path.home() / 'mnt' / remote
        try:
            # Try to list directory contents
            next(mount_point.iterdir())
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Mount Check", f"Mount {remote} is working properly")
        except StopIteration:
            # Empty directory is fine
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Mount Check", f"Mount {remote} is working (empty directory)")
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Mount Check", f"Mount {remote} may have issues: {e}")
    
    def open_mount_point(self, remote):
        """Open mount point in file manager"""
        mount_point = Path.home() / 'mnt' / remote
        try:
            subprocess.Popen(['xdg-open', str(mount_point)])
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to open {remote} mount point: {e}")
    
    def format_size(self, size):
        """Format size in bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"
    
    def closeEvent(self, event):
        """Stop timer when closing"""
        self.timer.stop()
        super().closeEvent(event)
