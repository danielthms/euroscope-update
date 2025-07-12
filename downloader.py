"""
Package Download Handler for EuroScope Updater
"""

import re
import requests
from pathlib import Path
from typing import Dict, Optional
from bs4 import BeautifulSoup


class PackageDownloader:
    def __init__(self, config):
        self.config = config
        # Download rules matching PowerShell script exactly
        self.download_rules = {
            'BIRD': {
                'url': 'https://files.aero-nav.com/SCA',
                'pattern': r'https://files\.aero-nav\.com/BIRD/Install-Pack_.*\.zip'
            },
            'EDGG': {
                'url': 'https://files.aero-nav.com/EDXX',  # Note: goes to /EDXX but looks for /EDGG/ links
                'pattern': r'https://files\.aero-nav\.com/EDGG/Full.*Package_.*\.zip'
            },
            'EDMM': {
                'url': 'https://files.aero-nav.com/EDXX',
                'pattern': r'https://files\.aero-nav\.com/EDMM/Full.*Package_.*\.zip'
            },
            'EDWW': {
                'url': 'https://files.aero-nav.com/EDXX',
                'pattern': r'https://files\.aero-nav\.com/EDWW/Full.*Package_.*\.zip'
            },
            'EDXX': {
                'url': 'https://files.aero-nav.com/EDXX',
                'pattern': r'https://files\.aero-nav\.com/EDXX/FIS_.*\.zip'
            },
            'EXCXO': {
                'url': 'https://files.aero-nav.com/EXCXO',
                'pattern': r'https://files\.aero-nav\.com/EXCXO/EXCXO-Install_.*\.zip'
            },
            'LPPO': {
                'url': 'https://files.aero-nav.com/LPPO',
                'pattern': r'https://files\.aero-nav\.com/LPPO/Install-Package_.*\.zip'
            }
        }
    
    def get_package(self, package_input: str) -> Path:
        """Get package path - either download or locate existing file"""
        # Check if it's a FIR code (3-5 characters) for auto-download
        if len(package_input) in [4, 5] and package_input.upper() in self.download_rules:
            return self.download_package(package_input.upper())
        
        # Otherwise, treat as filename
        package_path = self.config.download_dir / f"{package_input}"
        if not package_path.suffix:
            package_path = package_path.with_suffix('.zip')
        
        if not package_path.exists():
            raise FileNotFoundError(f"Package not found: {package_path}")
        
        return package_path
    
    def download_package(self, fir_code: str) -> Path:
        """Download package for given FIR code - matches PowerShell approach"""
        if fir_code not in self.download_rules:
            raise ValueError(f"Unsupported FIR for auto-download: {fir_code}")
        
        rule = self.download_rules[fir_code]
        
        print(f"🔍 Finding latest {fir_code} package...")
        
        # Create session exactly like PowerShell script
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Get the page with proper referer (like PowerShell -Headers @{"Referer"="$aeronavpage"})
        aeronavpage = rule['url']
        print(f"   Accessing: {aeronavpage}")
        
        response = session.get(aeronavpage, headers={'Referer': aeronavpage})
        response.raise_for_status()
        
        print(f"   Page size: {len(response.content)} bytes")
        
        # Parse HTML to find download links
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a', href=True)
        
        print(f"   Found {len(links)} total links")
        
        # Find matching download link using exact PowerShell pattern
        package_url = None
        all_hrefs = [link.get('href') for link in links]
        zip_links = [href for href in all_hrefs if '.zip' in href.lower()]
        
        print(f"   Found {len(zip_links)} ZIP links:")
        for i, link in enumerate(zip_links, 1):
            print(f"     {i:2d}. {link}")
            
            # Match exact PowerShell pattern
            if re.match(rule['pattern'], link):
                package_url = link
                print(f"   ✓ Pattern match: {link}")
                break
        
        if not package_url:
            raise ValueError(f"Could not find download link for {fir_code} matching pattern: {rule['pattern']}")
        
        # Extract filename and create unique local filename
        filename = package_url.split('/')[-1]
        target_path = self._get_unique_filepath(self.config.download_dir / filename)
        
        print(f"📥 Downloading {filename}...")
        print(f"   URL: {package_url}")
        print(f"   Target: {target_path}")
        
        # Download using the same session (like PowerShell -WebSession $session)
        download_response = session.get(package_url, stream=True)
        download_response.raise_for_status()
        
        # Check response headers
        content_type = download_response.headers.get('content-type', '')
        content_length = download_response.headers.get('content-length', '0')
        
        print(f"   Content-Type: {content_type}")
        print(f"   Content-Length: {content_length}")
        
        # Validate we're getting the right content
        if 'text/html' in content_type.lower():
            raise ValueError("Server returned HTML instead of ZIP file - authentication may be required")
        
        # Ensure download directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Download with validation
        total_size = int(content_length) if content_length.isdigit() else 0
        downloaded_size = 0
        
        with open(target_path, 'wb') as f:
            for chunk in download_response.iter_content(chunk_size=8192):
                if chunk:
                    # Validate first chunk is ZIP format
                    if downloaded_size == 0 and not chunk.startswith(b'PK'):
                        if b'<html' in chunk.lower() or b'<!doctype' in chunk.lower():
                            raise ValueError("Downloaded content is HTML, not ZIP file")
                        print(f"   ⚠️  Warning: File doesn't start with ZIP signature")
                    
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    
                    if total_size > 0:
                        progress = (downloaded_size / total_size) * 100
                        print(f"\r   Progress: {progress:.1f}%", end='', flush=True)
                    else:
                        print(f"\r   Downloaded: {downloaded_size//1024}KB", end='', flush=True)
        
        print(f"\n✓ Downloaded successfully ({downloaded_size//1024}KB)")
        
        # Validate final file size
        if downloaded_size < 1024 * 1024:  # Less than 1MB is suspicious for AIRAC
            print(f"   ⚠️  Warning: Small file size ({downloaded_size//1024}KB) for AIRAC package")
        
        return target_path
    
    def _get_unique_filepath(self, filepath: Path) -> Path:
        """Get unique filepath by adding suffix if file exists"""
        if not filepath.exists():
            return filepath
        
        base = filepath.stem
        suffix = filepath.suffix
        parent = filepath.parent
        
        counter = 2
        while True:
            new_path = parent / f"{base}-{counter}{suffix}"
            if not new_path.exists():
                return new_path
            counter += 1
    
    def extract_package_info(self, package_path: Path) -> Dict[str, str]:
        """Extract package information from filename"""
        filename = package_path.stem  # Remove .zip extension
        
        # Try to match different package naming patterns
        patterns = [
            # EDGG-Full-Package_20250613220519-241301-0016 format
            r'^([A-Z]{4,5}).*?(\d{4}).*?(\d{4}).*$',
            # EXCXO-Install_2410 format  
            r'^([A-Z]{4,5}).*?(\d{4}).*$',
            # Simple FIR_AIRAC format
            r'^([A-Z]{4,5}).*?(\d{4})$'
        ]
        
        package_info = {
            'path': package_path,
            'name': filename,
            'fir': '',
            'airac': '',
            'version': ''
        }
        
        for pattern in patterns:
            match = re.match(pattern, filename)
            if match:
                package_info['fir'] = match.group(1)
                package_info['airac'] = match.group(2) if len(match.groups()) >= 2 else ''
                if len(match.groups()) >= 3:
                    package_info['version'] = match.group(3)
                break
        
        # Handle special cases
        if package_info['fir'].startswith('EXCXO'):
            package_info['fir'] = 'EXCXO'
        
        # If we couldn't extract AIRAC, try to get it from the end of filename
        if not package_info['airac']:
            airac_match = re.search(r'(\d{4})(?!.*\d{4})', filename)
            if airac_match:
                package_info['airac'] = airac_match.group(1)
        
        if not package_info['fir']:
            raise ValueError(f"Could not determine FIR from filename: {filename}")
        
        return package_info