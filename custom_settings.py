"""
Custom Settings and Preferences for EuroScope Updater
Simple, direct approach - customize whatever you want!
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple


class CustomSettings:
    def __init__(self, config):
        self.config = config
    
    def apply_all_settings(self, package_info: Dict[str, str]):
        """Apply all custom settings for the package"""
        print("⚙️  Applying custom settings...")
        
        fir_code = package_info['fir']
        base_dir = self._get_base_dir(package_info)
        
        # Apply your custom settings here!
        # Uncomment and modify the sections you want to use
        
        # ========================================
        # GENERAL SETTINGS (All FIRs)
        # ========================================
        
        # Set VCCS Mini position for all profiles
        self.update_all_profiles(base_dir, {
            'TsVccsMiniControlX': '2181',
            'TsVccsMiniControlY': '26'
        })
        
        # Special VCCS position for TWR profiles
        self.update_profiles(base_dir, "*TWR*.prf", {
            'TsVccsMiniControlX': '1327'
        })
        
        # ========================================
        # FIR-SPECIFIC SETTINGS
        # ========================================
        
        if fir_code == 'EDGG':
            self._apply_edgg_settings(base_dir)
        elif fir_code == 'EDMM':
            self._apply_edmm_settings(base_dir)
        elif fir_code == 'EDWW':
            self._apply_edww_settings(base_dir)
        elif fir_code == 'EDXX':
            self._apply_edxx_settings(base_dir)
        elif fir_code == 'EXCXO':
            self._apply_excxo_settings(base_dir)
        # Add your own FIR here!
        
        print(f"   ✓ Applied custom settings for {fir_code}")
    
    # ============================================================================
    # FIR-SPECIFIC SETTINGS - CUSTOMIZE THESE AS NEEDED
    # ============================================================================
    
    def _apply_edgg_settings(self, base_dir: Path):

        ##### LANGEN RADAR #####
        self.update_file(base_dir / "EDGG/Settings/EDGG/EDGG_Screen.txt", {
            'm_ScreenNumber': '0',
            'm_ScreenPosition': '0',
            'm_ScreenMaximized': '0',
            'm_MetarListX': '1431',
            'm_MetarListY': '45',
            'm_ControllerListX': '1536',
            'm_ControllerListY': '232'
        })

        self.update_file(base_dir / "EDGG/Plugins/Topsky/EDGG/TopSkySettings.txt", {
            'Window_QNHTL': '0,1422,974',
            'Window_CARD': '0,1350,1180',
            'Window_LFUNCFP': '0,1536,45',
            'Window_CPDLC_Current': '0,0,650',
            'Window_CPDLC_Setting': '1,0,650'
        }, delimiter='=')

        ##### PHX #####
        self.update_file(base_dir / "EDGG/Settings/PHX/PHX_Screen.txt", {
            'm_ScreenNumber': '0',
            'm_ScreenPosition': '0',
            'm_ScreenMaximized': '0',
            'm_MetarListX': '713',
            'm_ControllerListX': '713',
            'm_ControllerListY': '77',
            'm_MetarListY': '45',
            'm_VoiceListX': '1857',
            'm_VoiceListY': '381'
        })

        self.update_file(base_dir / "EDGG/Settings/PHX/PHX_Symbology_Night.txt", {
            'Datablock:AC list background': '0:3.2:0:0:7',
            'Other:list header': '11447982:3.5:0:0:7',
            'Controller:normal': '16777215:3.5:0:0:7',
            'Controller:breaking': '4227327:3.5:0:0:7',
            'Controller:timeout': '255:4.0:0:0:7',
            'Metar:normal': '11447982:3.5:0:0:7',
            'Metar:modified': '33023:3.5:0:0:7',
            'Metar:timeout': '255:3.5:0:0:7',
            'Other:freetext': '8454143:3.5:0:1:7',
            'Chat:background': '0:3.5:0:0:7',
            'Chat:name normal': '10790052:3.5:0:0:7',
            'Chat:name unread': '16777215:3.5:0:0:7'
        })
        
        # Set active airports by sectors
        self.update_file(base_dir / "EDGG/Settings/EDGG_General.txt", {
            'SET_SetActiveAptBySectors': '1'
        })
        
        # Fix ATIS URL
        self.replace_in_profiles(base_dir, "EDGG_*.prf", [
            (r'&atistype=.{3}&', '&'),
            (r'&depfreq=', '&atistype=&depfreq=')
        ])
    
    def _apply_edmm_settings(self, base_dir: Path):
        """EDMM-specific settings - modify as you like!"""
        
        # Screen settings
        self.update_file(base_dir / "EDMM/Settings/iCAS2/Screen.txt", {
            'm_ScreenNumber': '0',
            'm_ScreenPosition': '6',
            'm_ScreenMaximized': '0',
            'm_MetarListX': '1431',
            'm_MetarListY': '45',
            'm_ControllerListX': '1574',
            'm_ControllerListY': '45'
        })
        
        self.update_file(base_dir / "EDMM/Settings/TWR_PHX/Screen.txt", {
            'm_ScreenNumber': '0',
            'm_ScreenPosition': '6',
            'm_ScreenMaximized': '0',
            'm_MetarListX': '1431',
            'm_MetarListY': '45',
            'm_ControllerListX': '1574',
            'm_ControllerListY': '45'
        })
    
    def _apply_edww_settings(self, base_dir: Path):
        """EDWW-specific settings - modify as you like!"""
        
        # Screen settings for multiple profiles
        screen_files = [
            "EDWW/Settings/Settings EDWW/SCREEN.txt",
            "EDWW/Settings/Settings EDUU/SCREEN.txt",
            "EDWW/Settings/Settings EDYY/SCREEN.txt",
            "EDWW/Settings/Settings PHX/SCREEN.txt"
        ]
        
        for screen_file in screen_files:
            self.update_file(base_dir / screen_file, {
                'm_ScreenNumber': '0',
                'm_ScreenPosition': '6',
                'm_ScreenMaximized': '0'
            })
        
        # Additional EDWW-specific settings
        self.update_file(base_dir / "EDWW/Settings/Settings EDWW/SCREEN.txt", {
            'm_MetarListX': '1431',
            'm_MetarListY': '45',
            'm_ControllerListX': '1574',
            'm_ControllerListY': '45'
        })
        
        # TopSky window positions
        self.update_file(base_dir / "EDWW/Plugins/TOPSKY EDWW/TopSkySettings.txt", {
            'Window_MsgIn': '1,0,900',
            'Window_CARD': '3,1350,1180',
            'Window_CPDLC_Current': '1,0,650',
            'Window_CPDLC_Setting': '1,368,650'
        }, delimiter='=')
    
    def _apply_edxx_settings(self, base_dir: Path):
        """EDXX (FIS) specific settings - modify as you like!"""
        
        # Screen settings
        self.update_file(base_dir / "EDXX/Settings/Screen.txt", {
            'm_ScreenNumber': '0',
            'm_ScreenPosition': '6',
            'm_ScreenMaximized': '0',
            'm_MetarListX': '1328',
            'm_MetarListY': '45',
            'm_ControllerListX': '2337',
            'm_ControllerListY': '45'
        })
        
        # Update airport name color and size
        self.update_file(base_dir / "EDXX/Settings/Symbology.txt", {
            'Airports:name': '11053224:3.5:0:0:1'
        })
        
        # TopSky window positions
        self.update_file(base_dir / "EDXX/Plugins/TopSky/TopSkySettings.txt", {
            'Window_QNHTL': '3,1422,974',
            'Window_FlightPlanSelect': '3,500,45'
        }, delimiter='=')
    
    def _apply_excxo_settings(self, base_dir: Path):
        """EXCXO-specific settings - modify as you like!"""
        
        self.update_file(base_dir / "EXCXO/Settings/Screen Layout.txt", {
            'm_ScreenNumber': '0',
            'm_ScreenPosition': '9',
            'm_ScreenMaximized': '0',
            'm_ControllerListX': '3281',
            'm_ControllerListY': '45'
        })
    
    # ============================================================================
    # HELPER METHODS - USE THESE TO CREATE YOUR OWN CUSTOMIZATIONS
    # ============================================================================
    
    def update_file(self, file_path: Path, updates: Dict[str, str], delimiter: str = ':'):
        """
        Update a settings file with new values
        
        Args:
            file_path: Path to the file to update
            updates: Dictionary of {setting_name: new_value}
            delimiter: Character that separates setting from value (':' or '=')
        
        Example:
            self.update_file(base_dir / "MyFIR/Settings/Screen.txt", {
                'm_ScreenNumber': '1',
                'm_MetarListX': '1500'
            })
        """
        if not file_path.exists():
            return
        
        try:
            with open(file_path, 'r', encoding='iso-8859-1') as f:
                content = f.read()
            
            for setting, value in updates.items():
                pattern = rf'^{re.escape(setting)}{re.escape(delimiter)}.+$'
                replacement = f'{setting}{delimiter}{value}'
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            
            with open(file_path, 'w', encoding='iso-8859-1') as f:
                f.write(content)
                
            print(f"      ✓ Updated {len(updates)} settings in {file_path.name}")
                
        except Exception as e:
            print(f"      ⚠️  Error updating {file_path.name}: {e}")
    
    def update_profiles(self, base_dir: Path, pattern: str, updates: Dict[str, str]):
        """
        Update profile files (.prf) with new settings
        
        Args:
            base_dir: Base directory to search in
            pattern: File pattern to match (e.g., "*.prf", "*TWR*.prf", "EDGG_*.prf")
            updates: Dictionary of {setting_name: new_value}
        
        Example:
            self.update_profiles(base_dir, "*TWR*.prf", {
                'TsVccsMiniControlX': '1327'
            })
        """
        files_updated = 0
        for prf_file in base_dir.rglob(pattern):
            for setting, value in updates.items():
                self.replace_in_file(prf_file, rf'{re.escape(setting)}\t.+', f'{setting}\t{value}')
            files_updated += 1
        
        if files_updated > 0:
            print(f"      ✓ Updated {len(updates)} settings in {files_updated} profile files")
    
    def update_all_profiles(self, base_dir: Path, updates: Dict[str, str]):
        """Update all .prf files with settings - convenience method"""
        self.update_profiles(base_dir, "*.prf", updates)
    
    def replace_in_profiles(self, base_dir: Path, pattern: str, replacements: List[Tuple[str, str]]):
        """
        Apply regex replacements to profile files
        
        Args:
            base_dir: Base directory to search in  
            pattern: File pattern to match
            replacements: List of (regex_pattern, replacement) tuples
        
        Example:
            self.replace_in_profiles(base_dir, "EDGG_*.prf", [
                (r'&atistype=.{3}&', '&'),
                (r'&depfreq=', '&atistype=&depfreq=')
            ])
        """
        files_updated = 0
        for prf_file in base_dir.rglob(pattern):
            for regex_pattern, replacement in replacements:
                self.replace_in_file(prf_file, regex_pattern, replacement)
            files_updated += 1
        
        if files_updated > 0:
            print(f"      ✓ Applied {len(replacements)} replacements to {files_updated} profile files")
    
    def replace_in_file(self, file_path: Path, pattern: str, replacement: str):
        """
        Apply a regex replacement to any file
        
        Args:
            file_path: Path to the file
            pattern: Regex pattern to find
            replacement: Text to replace with
        
        Example:
            self.replace_in_file(my_file, r'old_text', 'new_text')
        """
        if not file_path.exists():
            return
        
        try:
            with open(file_path, 'r', encoding='iso-8859-1') as f:
                content = f.read()
            
            new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            
            if new_content != content:
                with open(file_path, 'w', encoding='iso-8859-1') as f:
                    f.write(new_content)
                    
        except Exception as e:
            print(f"      ⚠️  Error updating {file_path.name}: {e}")
    
    def copy_file(self, source: Path, target: Path):
        """Copy a file - useful for custom file operations"""
        try:
            import shutil
            shutil.copy2(source, target)
            print(f"      ✓ Copied {source.name} to {target}")
        except Exception as e:
            print(f"      ⚠️  Error copying {source.name}: {e}")
    
    def _get_base_dir(self, package_info: Dict[str, str]) -> Path:
        """Get base directory for the package"""
        base_dir = self.config.euroscope_docs
        
        if self.config.use_subdirs:
            base_dir = base_dir / package_info['fir']
        
        return base_dir


# ================================================================================
# ADDING YOUR OWN CUSTOMIZATIONS
# ================================================================================
"""
To add custom settings for a new FIR or modify existing ones:

1. Add a new method like _apply_myfir_settings(self, base_dir)
2. Call it from apply_all_settings() 
3. Use the helper methods to make changes

Example for a new FIR:

def _apply_myfir_settings(self, base_dir: Path):
    # Update screen settings
    self.update_file(base_dir / "MYFIR/Settings/Screen.txt", {
        'm_ScreenNumber': '1',
        'm_ScreenPosition': '6'
    })
    
    # Update all profiles
    self.update_all_profiles(base_dir, {
        'TsVccsMiniControlX': '1600'
    })
    
    # Custom regex replacements
    self.replace_in_profiles(base_dir, "MYFIR_*.prf", [
        (r'old_pattern', 'new_text')
    ])
    
    # Copy custom files
    custom_file = Path("my_custom_file.txt")
    if custom_file.exists():
        self.copy_file(custom_file, base_dir / "MYFIR/MyFile.txt")

Then add to apply_all_settings():
elif fir_code == 'MYFIR':
    self._apply_myfir_settings(base_dir)

HELPER METHODS SUMMARY:

update_file(file_path, updates, delimiter=':')
    - Update colon or equals delimited files
    - e.g., update_file(screen_file, {'m_ScreenNumber': '1'})

update_profiles(base_dir, pattern, updates)  
    - Update .prf files matching pattern
    - e.g., update_profiles(base_dir, "*TWR*.prf", {'Setting': 'Value'})

update_all_profiles(base_dir, updates)
    - Update all .prf files
    - e.g., update_all_profiles(base_dir, {'TsVccsMiniControlX': '1529'})

replace_in_profiles(base_dir, pattern, replacements)
    - Apply regex replacements to profiles
    - e.g., replace_in_profiles(base_dir, "*.prf", [('old', 'new')])

replace_in_file(file_path, pattern, replacement)
    - Apply regex replacement to any file
    - e.g., replace_in_file(my_file, r'pattern', 'replacement')

copy_file(source, target)
    - Copy files around
    - e.g., copy_file(custom_file, target_location)
"""