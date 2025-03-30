"""Rclone process management module"""

import os
import subprocess
from pathlib import Path
from typing import Optional
from PyQt6.QtCore import QProcess

class RcloneManager:
    def __init__(self, config=None):
        # Check if rclone is installed
        try:
            version = subprocess.check_output(['rclone', 'version']).decode()
            print(f"Using {version.splitlines()[0]}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            raise RuntimeError("rclone is not installed or not in PATH. Please install rclone first.") from e
            
        self.mounts = {}
        self.config = config
        self.config_path = Path(config.get('config_path')) if config else Path.home() / '.config' / 'rclone' / 'rclone.conf'
        self.refresh_mounts()  # Initialize current mounts

    def mount(self, remote: str, mount_point: str) -> Optional[QProcess]:
        """Mount a remote"""
        if not self.config_path.exists():
            raise FileNotFoundError("Rclone config not found")

        # Check if already mounted
        if self.is_mounted(remote):
            return None

        # Create mount point if it doesn't exist
        Path(mount_point).mkdir(parents=True, exist_ok=True)

        process = QProcess()
        process.setProgram('rclone')
        args = ['mount', f'{remote}:/', mount_point, '--vfs-cache-mode', 'full']
        
        # Add mount options from config
        if self.config:
            mount_opts = self.config.get_mount_options(remote)
            if mount_opts:
                args.extend(mount_opts.split())
            
            # Add network settings with proper units
            bandwidth = self.config.get('bandwidth_limit')
            if bandwidth and bandwidth != '0':
                if not any(unit in bandwidth for unit in ['K', 'M', 'G', 'T']):
                    bandwidth += 'M'  # Default to MB/s
                args.extend(['--bwlimit', bandwidth])
                
            timeout = self.config.get('timeout')
            if timeout:
                args.extend(['--timeout', f"{timeout}s"])  # Add seconds unit
                
            retries = self.config.get('retries')
            if retries:
                args.extend(['--retries', str(retries)])
                
            buffer_size = self.config.get('buffer_size')
            if buffer_size:
                if not any(unit in buffer_size for unit in ['K', 'M', 'G', 'T']):
                    buffer_size += 'M'  # Default to MB
                args.extend(['--buffer-size', buffer_size])
                
            transfers = self.config.get('transfers')
            if transfers:
                args.extend(['--transfers', str(transfers)])
        
        # Add mount options for better reliability
        args.extend([
            '--daemon',                    # Run in background
            '--log-level', 'DEBUG',        # Verbose logging
            '--stats', '1s',               # Frequent stats
            '--dir-cache-time', '5m',      # Directory caching
            '--poll-interval', '15s',      # Check for changes
            '--vfs-write-back', '5s',      # Write-back cache
            '--vfs-read-chunk-size', '32M', # Read in chunks
            '--vfs-cache-max-age', '1h',   # Cache files
            '--vfs-read-ahead', '128M',    # Read-ahead buffer
            '--buffer-size', '32M',        # Transfer buffer
            '--transfers', '4',            # Concurrent transfers
            '--low-level-retries', '3',    # Connection retries
            '--contimeout', '15s',         # Connect timeout
            '--timeout', '30s',            # Operation timeout
        ])
        
        # Connect process signals for debugging
        process.readyReadStandardOutput.connect(
            lambda: print(f"rclone mount output: {process.readAllStandardOutput().data().decode()}")
        )
        process.readyReadStandardError.connect(
            lambda: print(f"rclone mount error: {process.readAllStandardError().data().decode()}")
        )
        process.errorOccurred.connect(
            lambda error: print(f"rclone mount process error: {error}")
        )
        
        print(f"Starting rclone mount with args: {' '.join(args)}")
        process.setArguments(args)
        process.start()
        
        # Wait for the process to start
        if not process.waitForStarted(5000):  # 5 second timeout
            error = process.readAllStandardError().data().decode()
            raise RuntimeError(f"Failed to start rclone process: {error}")
            
        print("Rclone process started, waiting for mount...")
        
        # Give it time to mount and check multiple times
        max_attempts = 10
        for attempt in range(max_attempts):
            import time
            time.sleep(3)  # Wait longer between checks
            print(f"Checking mount attempt {attempt + 1}/{max_attempts}...")
            
            # First check process state
            if process.state() != QProcess.ProcessState.Running:
                error = process.readAllStandardError().data().decode()
                print(f"Process exited with error: {error}")
                process.kill()
                raise RuntimeError(f"Mount process failed: {error}")
            
            # Then verify mount
            if self.verify_mount(mount_point):
                print(f"Mount successful on attempt {attempt + 1}")
                self.mounts[remote] = process
                return process
            
            # Check for fusermount process
            try:
                fuse_check = subprocess.run(
                    ['pgrep', '-f', f'fusermount.*{mount_point}'],
                    capture_output=True,
                    text=True
                )
                if fuse_check.returncode == 0:
                    print("Fusermount process found, continuing to wait...")
                else:
                    print("No fusermount process found")
            except Exception as e:
                print(f"Error checking fusermount: {e}")
        
        # If we get here, mount failed after all attempts
        error = process.readAllStandardError().data().decode()
        process.kill()
        # Try to clean up
        try:
            subprocess.run(['fusermount', '-u', mount_point], check=False)
        except:
            pass
        raise RuntimeError(f"Mount failed to initialize after {max_attempts} attempts: {error}")

    def unmount(self, remote: str) -> bool:
        """Unmount a remote"""
        if not self.is_mounted(remote):
            return False

        mount_point = Path.home() / 'mnt' / remote
        process = self.mounts.get(remote)
        
        if process:
            process.terminate()
            if not process.waitForFinished(5000):  # 5 second timeout
                process.kill()
        
        # Also try fusermount -u as backup
        try:
            subprocess.run(['fusermount', '-u', str(mount_point)], check=True)
        except subprocess.CalledProcessError:
            pass
        
        # Remove from mounts dict if it was there
        if remote in self.mounts:
            del self.mounts[remote]
        
        return True
        
    def is_mounted(self, remote: str) -> bool:
        """Check if a remote is currently mounted"""
        mount_point = Path.home() / 'mnt' / remote
        
        # Check if in mounts dict and process is running
        if remote in self.mounts:
            process = self.mounts[remote]
            if process.state() == QProcess.ProcessState.Running:
                return self.verify_mount(str(mount_point))
            else:
                # Process died, clean up
                del self.mounts[remote]
                return False
        
        # Check if mounted in system
        return self.verify_mount(str(mount_point))
        
    def verify_mount(self, mount_point: str) -> bool:
        """Verify if a mount point is working"""
        try:
            # Check mount status using findmnt
            result = subprocess.run(
                ['findmnt', mount_point],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"findmnt shows {mount_point} is not mounted")
                return False
                
            print(f"Mount point status:\n{result.stdout}")
            return True
            
        except Exception as e:
            print(f"Error checking mount with findmnt: {e}")
            
            # Fallback to checking /proc/mounts
            try:
                with open('/proc/mounts', 'r') as f:
                    mounts = f.read()
                    if mount_point in mounts:
                        print(f"Found {mount_point} in /proc/mounts")
                        return True
                    print(f"Mount point {mount_point} not found in /proc/mounts")
                    return False
            except Exception as e2:
                print(f"Error checking /proc/mounts: {e2}")
                return False
                
    def list_remotes(self) -> list:
        """List available remotes"""
        try:
            result = subprocess.run(
                ['rclone', 'listremotes'],
                capture_output=True,
                text=True,
                check=True
            )
            return [r.strip(':') for r in result.stdout.splitlines()]
        except Exception as e:
            print(f"Error listing remotes: {e}")
            return []
            
    def refresh_mounts(self):
        """Refresh the current mount status"""
        # Clear current mounts
        self.mounts.clear()
        
        # Check mnt directory for existing mounts
        mnt_dir = Path.home() / 'mnt'
        if not mnt_dir.exists():
            return
            
        for mount_point in mnt_dir.iterdir():
            if mount_point.is_mount():
                remote = mount_point.name
                # Try to find the rclone process for this mount
                try:
                    output = subprocess.check_output(['pgrep', '-f', f'rclone mount.*{remote}:/']).decode()
                    if output.strip():
                        pid = int(output.strip())
                        # Create a QProcess for the existing mount
                        process = QProcess()
                        # Store the PID for later use
                        process.pid = pid
                        self.mounts[remote] = process
                except subprocess.CalledProcessError:
                    pass  # No process found

    def list_remotes(self) -> list[str]:
        """List configured remotes"""
        if not self.config_path.exists():
            return []

        try:
            output = subprocess.check_output(['rclone', 'listremotes'])
            return [r.strip(':') for r in output.decode().splitlines()]
        except subprocess.CalledProcessError:
            return []

    def cleanup(self):
        """Clean up all mounts"""
        for remote in list(self.mounts.keys()):
            self.unmount(remote)
