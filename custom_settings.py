"""
Custom Settings and Preferences for EuroScope Updater
This module handles FIR-specific customizations and can be easily extended.
"""

import re
from pathlib import Path
from typing import Dict, Callable, List, Tuple


class CustomSettings:
    def __init__(self, config):
        self.config = config
        
        # Register custom setting handlers for each FIR
        self.fir_handlers = {
            'EDGG': self._apply_edgg_settings,
            'EDMM': self._apply_edmm_settings,
            'EDWW': self._apply_edww_settings,
            'EDXX': self._apply_edxx_settings,
            'EXCXO': self._apply_excxo_settings,
            'BIRD': self._apply_bird_settings,
            'LPPO': self._apply_lppo_settings,
        }
    
    def apply_all_settings(self, package_info: Dict[str, str]):
        """Apply all custom settings for the package"""
        print("⚙️  Applying custom settings...")
        
        fir_code = package_info['fir']
        
        # Apply general settings first
        self._apply_general_settings(package_info)
        
        # Apply FIR-specific settings
        if fir_code in self.fir_handlers:
            self.fir_handlers[fir_code](package_info)
            print(f"   ✓ Applied {fir_code} specific settings")
        else:
            print(f"   ℹ️  No custom settings defined for {fir_code}")
    
    def _apply_general_settings(self, package_info: Dict[str, str]):
        """Apply general settings that work for all FIRs"""
        base_dir = self._get_base_dir(package_info)
        
        # Update VCCS Mini position for all profiles
        self._update_vccs_mini_position(base_dir)
        
        # Set active airports by owned sectors (if supported)
        self._set_active_airports_by_sectors(package_info, base_dir)
    
    def _apply_edgg_settings(self, package_info: Dict[str, str]):
        """Apply EDGG-specific custom settings"""
        base_dir = self._get_base_dir(package_info)
        
        # Update screen settings
        screen_settings = [
            ("EDGG/Settings/EDGG/EDGG_Screen.txt", {
                'm_ScreenNumber': '0',
                'm_ScreenPosition': '6',
                'm_ScreenMaximized': '0',
                'm_MetarListX': '1431',
                'm_MetarListY': '45',
                'm_ControllerListX': '1536',
                'm_ControllerListY': '232'
            }),
            ("EDGG/Settings/PHX/PHX_Screen.txt", {
                'm_ScreenNumber': '0',
                'm_ScreenPosition': '6',
                'm_ScreenMaximized': '0',
                'm_MetarListX': '1431',
                'm_MetarListY': '45',
                'm_ControllerListX': '1574',
                'm_ControllerListY': '45'
            })
        ]
        
        for file_path, settings in screen_settings:
            self._update_colon_delimited_file(base_dir / file_path, settings)
        
        # Update TopSky settings
        topsky_settings = [
            ("EDGG/Plugins/Topsky/EDGG/TopSkySettings.txt", {
                'Window_QNHTL': '3,1422,974',
                'Window_CARD': '3,1350,1180',
                'Window_LFUNCFP': '3,1536,45',
                'Window_CPDLC_Current': '1,0,650',
                'Window_CPDLC_Setting': '1,368,650'
            })
        ]
        
        for file_path, settings in topsky_settings:
            self._update_equals_delimited_file(base_dir / file_path, settings)
        
        # Update ATIS maker URL
        self._update_atis_url(base_dir, package_info['fir'])
    
    def _apply_edmm_settings(self, package_info: Dict[str, str]):
        """Apply EDMM-specific custom settings"""
        base_dir = self._get_base_dir(package_info)
        
        screen_settings = [
            ("EDMM/Settings/iCAS2/Screen.txt", {
                'm_ScreenNumber': '0',
                'm_ScreenPosition': '6',
                'm_ScreenMaximized': '0',
                'm_MetarListX': '1431',
                'm_MetarListY': '45',
                'm_ControllerListX': '1574',
                'm_ControllerListY': '45'
            })
        ]
        
        for file_path, settings in screen_settings:
            self._update_colon_delimited_file(base_dir / file_path, settings)
    
    def _apply_edww_settings(self, package_info: Dict[str, str]):
        """Apply EDWW-specific custom settings"""
        base_dir = self._get_base_dir(package_info)
        
        # EDWW has many screen files to update
        screen_files = [
            "EDWW/Settings/Settings EDWW/SCREEN.txt",
            "EDWW/Settings/Settings EDUU/SCREEN.txt",
            "EDWW/Settings/Settings EDYY/SCREEN.txt",
            "EDWW/Settings/Settings PHX/SCREEN.txt"
        ]
        
        for screen_file in screen_files:
            self._update_colon_delimited_file(base_dir / screen_file, {
                'm_ScreenNumber': '0',
                'm_ScreenPosition': '6',
                'm_ScreenMaximized': '0'
            })
    
    def _apply_edxx_settings(self, package_info: Dict[str, str]):
        """Apply EDXX (FIS)-specific custom settings"""
        base_dir = self._get_base_dir(package_info)
        
        # Update screen settings for FIS
        self._update_colon_delimited_file(base_dir / "EDXX/Settings/Screen.txt", {
            'm_ScreenNumber': '0',
            'm_ScreenPosition': '6',
            'm_ScreenMaximized': '0',
            'm_MetarListX': '1328',
            'm_MetarListY': '45',
            'm_ControllerListX': '2337',
            'm_ControllerListY': '45'
        })
        
        # Update airport name symbology
        self._update_colon_delimited_file(base_dir / "EDXX/Settings/Symbology.txt", {
            'Airports:name': '11053224:3.5:0:0:1'
        })
    
    def _apply_excxo_settings(self, package_info: Dict[str, str]):
        """Apply EXCXO-specific custom settings"""
        base_dir = self._get_base_dir(package_info)
        
        self._update_colon_delimited_file(base_dir / "EXCXO/Settings/Screen Layout.txt", {
            'm_ScreenNumber': '0',
            'm_ScreenPosition': '9',
            'm_ScreenMaximized': '0',
            'm_ControllerListX': '3281',
            'm_ControllerListY': '45'
        })
    
    def _apply_bird_settings(self, package_info: Dict[str, str]):
        """Apply BIRD-specific custom settings"""
        # BIRD typically uses default settings
        pass
    
    def _apply_lppo_settings(self, package_info: Dict[str, str]):
        """Apply LPPO-specific custom settings"""
        # LPPO typically uses default settings
        pass
    
    def _get_base_dir(self, package_info: Dict[str, str]) -> Path:
        """Get base directory for the package"""
        base_dir = self.config.euroscope_docs
        
        if self.config.use_subdirs:
            base_dir = base_dir / package_info['fir']
        
        return base_dir
    
    def _update_vccs_mini_position(self, base_dir: Path):
        """Update VCCS Mini control position in all profiles"""
        for prf_file in base_dir.rglob('*.prf'):
            replacements = [
                (r'TsVccsMiniControlX\t.+', 'TsVccsMiniControlX\t1529'),
                (r'TsVccsMiniControlY\t.+', 'TsVccsMiniControlY\t26')
            ]
            
            # Special position for TWR profiles
            if 'TWR' in prf_file.name:
                replacements[0] = (r'TsVccsMiniControlX\t.+', 'TsVccsMiniControlX\t1327')
            
            self._apply_regex_replacements(prf_file, replacements)
    
    def _set_active_airports_by_sectors(self, package_info: Dict[str, str], base_dir: Path):
        """Set active airports by owned sectors for supported FIRs"""
        if package_info['fir'] == 'EDGG':
            general_file = base_dir / "EDGG/Settings/EDGG_General.txt"
            if general_file.exists():
                self._update_colon_delimited_file(general_file, {
                    'SET_SetActiveAptBySectors': '1'
                })
    
    def _update_atis_url(self, base_dir: Path, fir_code: str):
        """Update ATIS maker URL for EDGG"""
        if fir_code != 'EDGG':
            return
        
        # Update profiles
        for prf_file in base_dir.glob(f"{fir_code}_*.prf"):
            replacements = [
                (r'&atistype=.{3}&', '&'),
                (r'&depfreq=', '&atistype=&depfreq=')
            ]
            self._apply_regex_replacements(prf_file, replacements)
        
        # Update general settings
        general_file = base_dir / "EDGG/Settings/EDGG_General.txt"
        if general_file.exists():
            self._apply_regex_replacements(general_file, [
                (r'&atistype=.{3}&', '&'),
                (r'&depfreq=', '&atistype=&depfreq=')
            ])
    
    def _update_colon_delimited_file(self, file_path: Path, updates: Dict[str, str]):
        """Update colon-delimited configuration file"""
        if not file_path.exists():
            return
        
        try:
            with open(file_path, 'r', encoding='iso-8859-1') as f:
                content = f.read()
            
            for key, value in updates.items():
                pattern = rf'^{re.escape(key)}:.+$'
                replacement = f'{key}:{value}'
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            
            with open(file_path, 'w', encoding='iso-8859-1') as f:
                f.write(content)
                
        except Exception as e:
            print(f"      ⚠️  Error updating {file_path.name}: {e}")
    
    def _update_equals_delimited_file(self, file_path: Path, updates: Dict[str, str]):
        """Update equals-delimited configuration file"""
        if not file_path.exists():
            return
        
        try:
            with open(file_path, 'r', encoding='iso-8859-1') as f:
                content = f.read()
            
            for key, value in updates.items():
                pattern = rf'^{re.escape(key)}=.+$'
                replacement = f'{key}={value}'
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            
            with open(file_path, 'w', encoding='iso-8859-1') as f:
                f.write(content)
                
        except Exception as e:
            print(f"      ⚠️  Error updating {file_path.name}: {e}")
    
    def _apply_regex_replacements(self, file_path: Path, replacements: List[Tuple[str, str]]):
        """Apply regex replacements to a file"""
        if not file_path.exists():
            return
        
        try:
            with open(file_path, 'r', encoding='iso-8859-1') as f:
                content = f.read()
            
            for pattern, replacement in replacements:
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            
            with open(file_path, 'w', encoding='iso-8859-1') as f:
                f.write(content)
                
        except Exception as e:
            print(f"      ⚠️  Error updating {file_path.name}: {e}")


# Easy extension interface for adding new custom settings
class CustomSettingsExtension:
    """
    Base class for extending custom settings.
    Create a new class inheriting from this to add custom settings for new FIRs.
    """
    
    def __init__(self, config):
        self.config = config
    
    def apply_settings(self, package_info: Dict[str, str], base_dir: Path):
        """Override this method to implement custom settings"""
        raise NotImplementedError
    
    def register_with(self, custom_settings: CustomSettings, fir_code: str):
        """Register this extension with the main CustomSettings instance"""
        custom_settings.fir_handlers[fir_code] = lambda pkg_info: self.apply_settings(
            pkg_info, custom_settings._get_base_dir(pkg_info)
        )


# Example of how to add custom settings for a new FIR:
"""
class MyCustomFIRSettings(CustomSettingsExtension):
    def apply_settings(self, package_info: Dict[str, str], base_dir: Path):
        # Your custom settings here
        print(f"Applying custom settings for {package_info['fir']}")
        
        # Example: Update a specific file
        my_file = base_dir / "MyFIR/Settings/MySettings.txt"
        if my_file.exists():
            self._update_colon_delimited_file(my_file, {
                'MySetting': 'MyValue'
            })

# To use the extension:
# my_extension = MyCustomFIRSettings(config)
# my_extension.register_with(custom_settings, 'MYFIR')
"""