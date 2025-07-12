#!/usr/bin/env python3
"""
EuroScope AIRAC Update Script - Main Entry Point
"""

import argparse
import sys
from pathlib import Path

from config_manager import ConfigManager
from downloader import PackageDownloader
from extractor import PackageExtractor
from profile_updater import ProfileUpdater
from custom_settings import CustomSettings


def main():
    parser = argparse.ArgumentParser(
        prog="euroscope-updater",
        description="EuroScope AIRAC Update Tool"
    )
    parser.add_argument(
        "package",
        help="Package name (ZIP file) or FIR code for auto-download"
    )
    parser.add_argument(
        "-c", "--config",
        type=Path,
        default=Path("config.ini"),
        help="Configuration file path (default: config.ini)"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip backup creation"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = ConfigManager(args.config)
        
        # Initialize components
        downloader = PackageDownloader(config)
        extractor = PackageExtractor(config)
        profile_updater = ProfileUpdater(config)
        custom_settings = CustomSettings(config)
        
        print(f"EuroScope AIRAC Updater")
        print(f"Package: {args.package}")
        print(f"Config: {args.config}")
        print("-" * 50)
        
        # Step 1: Download or locate package
        package_path = downloader.get_package(args.package)
        package_info = downloader.extract_package_info(package_path)
        
        print(f"Package: {package_info['name']}")
        print(f"FIR: {package_info['fir']}")
        print(f"AIRAC: {package_info['airac']}")
        
        if args.dry_run:
            print("DRY RUN - No changes will be made")
            return 0
            
        # Step 2: Backup existing installation
        if not args.no_backup:
            extractor.create_backup(package_info['fir'])
            
        # Step 3: Extract new package
        extractor.extract_package(package_path, package_info)
        
        # Step 4: Update profiles
        profile_updater.update_all_profiles(package_info)
        
        # Step 5: Apply custom settings
        custom_settings.apply_all_settings(package_info)
        
        # Step 6: Copy additional files
        extractor.copy_additional_files(package_info)
        
        print("-" * 50)
        print("✓ Update completed successfully!")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n✗ Update cancelled by user")
        return 1
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())