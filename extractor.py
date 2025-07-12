"""
Package Extraction and File Operations for EuroScope Updater
"""

import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict


class PackageExtractor:
    def __init__(self, config):
        self.config = config
    
    def create_backup(self, fir_code: str):
        """Create backup of existing package"""
        print("💾 Creating backup...")
        
        backup_dir = self.config.backup_dir
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Create timestamped backup directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_target = backup_dir / f"{fir_code}_{timestamp}"
        
        if self.config.use_subdirs:
            # Backup entire subdirectory
            source_dir = self.config.euroscope_docs / fir_code
            if source_dir.exists():
                shutil.copytree(source_dir, backup_target)
                print(f"✓ Backed up {source_dir} to {backup_target}")
        else:
            # Backup all files/folders matching FIR pattern
            backup_target.mkdir(exist_ok=True)
            
            for item in self.config.euroscope_docs.glob(f"{fir_code}*"):
                target_item = backup_target / item.name
                
                if item.is_dir():
                    shutil.copytree(item, target_item)
                else:
                    shutil.copy2(item, target_item)
                
                print(f"✓ Backed up {item.name}")
    
    def extract_package(self, package_path: Path, package_info: Dict[str, str]):
        """Extract package to EuroScope directory"""
        print("📦 Extracting package...")
        
        fir_code = package_info['fir']
        extraction_target = self.config.euroscope_docs
        
        if self.config.use_subdirs:
            extraction_target = extraction_target / fir_code
            extraction_target.mkdir(parents=True, exist_ok=True)
        
        # Remove existing files
        self._remove_existing_files(fir_code)
        
        # Extract ZIP file
        with zipfile.ZipFile(package_path, 'r') as zip_ref:
            zip_ref.extractall(extraction_target)
        
        print(f"✓ Extracted to {extraction_target}")
        
        # Rename profile files if needed
        self._rename_profile_files(package_info, extraction_target)
    
    def _remove_existing_files(self, fir_code: str):
        """Remove existing package files"""
        print(f"🗑️  Removing old {fir_code} files...")
        
        if self.config.use_subdirs:
            target_dir = self.config.euroscope_docs / fir_code
            if target_dir.exists():
                shutil.rmtree(target_dir)
        else:
            for item in self.config.euroscope_docs.glob(f"{fir_code}*"):
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
    
    def _rename_profile_files(self, package_info: Dict[str, str], extraction_target: Path):
        """Rename profile files to include FIR prefix"""
        if self.config.use_subdirs:
            return  # Don't rename when using subdirectories
        
        fir_code = package_info['fir']
        
        rename_rules = {
            'BIRD': {
                'BIRD_TopSky.prf': 'BIRD FIR - OCA.prf'
            },
            'EDMM': {
                'iCAS2.prf': 'EDMM FIR - Muenchen iCAS2.prf',
                'TWR_PHX_DAY.prf': 'EDMM FIR - TWR PHX Day.prf',
                'TWR_PHX_NIGHT.prf': 'EDMM FIR - TWR PHX Night.prf'
            },
            'EDXX': {
                'FIS.prf': 'EDXX FIS.prf'
            },
            'EXCXO': {
                'OCA TopSky.prf': 'EXCXO FSS - OCA.prf'
            },
            'LPPO': {
                'LPPO.prf': 'LPPO FIR.prf',
                'LPPO_TS.prf': 'LPPO FIR - OCA.prf'
            }
        }
        
        if fir_code in rename_rules:
            print("🏷️  Renaming profile files...")
            
            for old_name, new_name in rename_rules[fir_code].items():
                old_file = extraction_target / old_name
                new_file = extraction_target / new_name
                
                if old_file.exists():
                    old_file.rename(new_file)
                    print(f"   {old_name} → {new_name}")
    
    def copy_additional_files(self, package_info: Dict[str, str]):
        """Copy NavData and custom files"""
        self._copy_navdata(package_info)
        self._copy_custom_files(package_info)
        
        # Clean up package if requested
        if self.config.delete_package:
            print("🗑️  Removing downloaded package...")
            package_info['path'].unlink()
    
    def _copy_navdata(self, package_info: Dict[str, str]):
        """Copy NavData files if available"""
        navdata_dir = self.config.navdata_dir
        
        if not navdata_dir.exists():
            return
        
        # Check if NavData is current
        cycle_file = navdata_dir / "cycle_info.txt"
        if not cycle_file.exists():
            print("⚠️  NavData cycle info not found, skipping NavData copy")
            return
        
        # Validate NavData currency (simplified check)
        try:
            with open(cycle_file, 'r') as f:
                content = f.read()
                if "Valid" not in content:
                    print("⚠️  NavData appears outdated, skipping copy")
                    return
        except Exception as e:
            print(f"⚠️  Could not validate NavData: {e}")
            return
        
        # Copy NavData files
        fir_code = package_info['fir']
        target_dir = self.config.euroscope_docs
        
        if self.config.use_subdirs:
            target_dir = target_dir / fir_code
        
        navdata_target = target_dir / fir_code / "NavData"
        
        if navdata_target.exists():
            print("📊 Copying NavData files...")
            
            for filename in ['AIRWAY.txt', 'ISEC.txt']:
                source_file = navdata_dir / filename
                target_file = navdata_target / filename.lower()
                
                if source_file.exists():
                    shutil.copy2(source_file, target_file)
                    print(f"   ✓ {filename}")
    
    def _copy_custom_files(self, package_info: Dict[str, str]):
        """Copy custom files if enabled"""
        if not self.config.use_custom_files:
            return
        
        custom_dir = self.config.custom_files_dir
        if not custom_dir.exists():
            print("⚠️  Custom files directory not found")
            return
        
        print("📁 Copying custom files...")
        
        target_dir = self.config.euroscope_docs
        if self.config.use_subdirs:
            target_dir = target_dir / package_info['fir']
        
        # Copy all files from custom directory
        for item in custom_dir.rglob('*'):
            if item.is_file():
                relative_path = item.relative_to(custom_dir)
                target_path = target_dir / relative_path
                
                # Create target directory if needed
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                shutil.copy2(item, target_path)
                print(f"   ✓ {relative_path}")