import configparser
import os
from pathlib import Path


class ConfigManager:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = configparser.ConfigParser()

        if not config_path.exists():
            self.create_default_config()

        self.load_config()
        self.validate_config()

    def create_default_config(self):
        userprofile = os.environ.get("USERPROFILE", os.path.expanduser("~"))
        programfiles_x86 = os.environ.get(
            "PROGRAMFILES(X86)", "C:\\Program Files (x86)"
        )

        default_config = f"""[PATHS]
# Directory where packages are downloaded
download_dir = {userprofile}\\Downloads

# EuroScope documents directory (contains AIRAC data)
euroscope_docs = {userprofile}\\AppData\\Roaming\\EuroScope

# EuroScope application directory
euroscope_app = {programfiles_x86}\\EuroScope

# Backup directory for old packages
backup_dir = {userprofile}\\AppData\\Roaming\\EuroScope\\_Backups

# NavData directory (optional - for Navigraph users)
navdata_dir = {userprofile}\\AppData\\Roaming\\EuroScope\\_NavData\\Bin

# Custom files directory (optional)
custom_files_dir = {userprofile}\\AppData\\Roaming\\EuroScope\\_Custom

[LOGIN]
# Your VATSIM credentials
cid = YOUR_VATSIM_ID
password = YOUR_PASSWORD
name = YOUR REAL NAME
rating = 1 # S1=1, S2=2, S3=3, C1=4, C3=5

# Observer callsign (without _OBS suffix)
initials = XX

# Hoppie code for CPDLC
hoppie = YOUR_HOPPIE_CODE

[SETTINGS]
# Text size for displays (leave empty to keep defaults)
text_size = 

[VCCS]
# Voice communications settings
ptt = 
mode = 
playback = 
capture = 

[OPTIONS]
# Use subdirectories for each package
use_subdirs = false

# Copy custom files
use_custom_files = false

# Delete package after installation
delete_package = false
"""

        with open(self.config_path, "w") as f:
            f.write(default_config)

        print(f"✓ Created default configuration at {self.config_path}")
        print(
            "Please edit the configuration file with your settings before running again."
        )
        exit(0)

    def load_config(self):
        self.config.read(self.config_path)

    def validate_config(self):
        required_sections = ["PATHS", "LOGIN", "SETTINGS", "VCCS", "OPTIONS"]

        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required configuration section: [{section}]")

        if self.config["LOGIN"]["cid"] == "YOUR_VATSIM_ID":
            raise ValueError(
                "Please update your VATSIM credentials in the configuration file"
            )

    def get(self, section: str, key: str, fallback: str = "") -> str:
        return self.config.get(section, key, fallback=fallback)

    def getboolean(self, section: str, key: str, fallback: bool = False) -> bool:
        return self.config.getboolean(section, key, fallback=fallback)

    def getpath(self, section: str, key: str, fallback: str = "") -> Path:
        path_str = self.get(section, key, fallback)
        return Path(path_str) if path_str else Path()

    @property
    def download_dir(self) -> Path:
        return self.getpath("PATHS", "download_dir")

    @property
    def euroscope_docs(self) -> Path:
        return self.getpath("PATHS", "euroscope_docs")

    @property
    def euroscope_app(self) -> Path:
        return self.getpath("PATHS", "euroscope_app")

    @property
    def backup_dir(self) -> Path:
        return self.getpath("PATHS", "backup_dir")

    @property
    def navdata_dir(self) -> Path:
        return self.getpath("PATHS", "navdata_dir")

    @property
    def custom_files_dir(self) -> Path:
        return self.getpath("PATHS", "custom_files_dir")

    @property
    def vatsim_cid(self) -> str:
        return self.get("LOGIN", "cid")

    @property
    def vatsim_password(self) -> str:
        return self.get("LOGIN", "password")

    @property
    def real_name(self) -> str:
        return self.get("LOGIN", "name")

    @property
    def rating(self) -> str:
        return self.get("LOGIN", "rating")

    @property
    def initials(self) -> str:
        return self.get("LOGIN", "initials")

    @property
    def hoppie_code(self) -> str:
        return self.get("LOGIN", "hoppie")

    @property
    def observer_callsign(self) -> str:
        return f"{self.initials}_OBS"

    @property
    def text_size(self) -> str:
        return self.get("SETTINGS", "text_size")

    @property
    def use_subdirs(self) -> bool:
        return self.getboolean("OPTIONS", "use_subdirs")

    @property
    def use_custom_files(self) -> bool:
        return self.getboolean("OPTIONS", "use_custom_files")

    @property
    def delete_package(self) -> bool:
        return self.getboolean("OPTIONS", "delete_package")
