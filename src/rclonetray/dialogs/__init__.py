"""Dialog modules"""

from .preferences import PreferencesDialog
from .about import AboutDialog
from .settings import SettingsDialog
from .rclone_config import RcloneConfigDialog
from .dashboard import DashboardDialog
from .transfer import TransferDialog
from .new_remote import NewRemoteDialog

__all__ = [
    'PreferencesDialog',
    'AboutDialog',
    'SettingsDialog',
    'RcloneConfigDialog',
    'DashboardDialog',
    'TransferDialog',
    'NewRemoteDialog'
]
