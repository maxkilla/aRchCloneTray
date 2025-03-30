# aRchCloneTray

aRchCloneTray is a modern PyQt6-based system tray application for [Rclone](https://rclone.org/), providing seamless integration with Linux desktop environments and easy access to remote file systems.

## Features
- 🖥️ Modern PyQt6 interface with dark mode support
- 🔄 Real-time mount management and status monitoring
- 📊 Dashboard with system statistics and transfer monitoring
- ⚙️ Advanced mount options and configuration
- 🔔 System notifications for mount events
- 🎨 Clean and intuitive user interface

## Requirements
- Python 3.8 or higher
- PyQt6
- rclone (installed via system package manager)
- FUSE3

## Installation

### Arch Linux

1. Install dependencies:
```bash
sudo pacman -S python python-pyqt6 rclone fuse3 qt6-base
```

2. Install from source:
```bash
git clone https://github.com/maxkilla/aRchCloneTray.git
cd aRchCloneTray
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Run the application:
```bash
python -m rclonetray
```

4. (Optional) Add to autostart:
```bash
mkdir -p ~/.config/autostart
cp desktop/org.archclonetray.desktop ~/.config/autostart/
```

The application will automatically start with your desktop environment and appear in the system tray.

## Usage

1. Ensure rclone is installed and configured
2. Start aRchCloneTray
3. Use the system tray icon to:
   - Mount/unmount remotes
   - View transfer status
   - Access the dashboard
   - Configure settings

## Configuration

The application uses your existing rclone configuration (`~/.config/rclone/rclone.conf`) and stores its own settings in `~/.config/archclonetray/config.json`.

## Development

This is a modern Linux application built with:
- PyQt6 for the UI
- Python standard library for process management
- Modern async/await patterns for better performance

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


## FAQ

**How do I configure rclone?**

Use `rclone config` in the terminal to set up your remotes, or use the built-in configuration interface in aRchCloneTray.

**Where are my mounts located?**

By default, mounts are created in `~/mnt/<remote_name>`.

**How do I update aRchCloneTray?**

Pull the latest changes from the repository and restart the application:
```bash
git pull
pip install -r requirements.txt
```

## License

This project is licensed under the [MIT License](LICENSE.txt).
