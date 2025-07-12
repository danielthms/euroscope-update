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
        self.current_download_fir = None  # Track which FIR we're downloading
        self.download_rules = {
            'BIRD': {
                'url': 'https://files.aero-nav.com/SCA',
                'pattern': r'https://files\.aero-nav\.com/BIRD/Install-Pack_.*\.zip'
            },
            'EDGG': {
                'url': 'https://files.aero-nav.com/EDXX',
                'pattern': r'https://files\.aero-nav\.com/EDGG/.*Full.*Package.*\.zip'
            },
            'EDMM': {
                'url': 'https://files.aero-nav.com/EDXX',
                'pattern': r'https://files\.aero-nav\.com/EDMM/.*Full.*Package.*\.zip'
            },
            'EDWW': {
                'url': 'https://files.aero-nav.com/EDXX',
                'pattern': r'https://files\.aero-nav\.com/EDWW/.*Full.*Package.*\.zip'
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
        """Download package for given FIR code"""
        if fir_code not in self.download_rules:
            raise ValueError(f"Unsupported FIR for auto-download: {fir_code}")
        
        rule = self.download_rules[fir_code]
        
        print(f"🔍 Finding latest {fir_code} package...")
        
        # Create a session to maintain cookies and state
        session = requests.Session()
        
        # Set proper headers to mimic a real browser
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # First, get the download page to establish session and get proper referrer
        print(f"   Accessing {rule['url']}...")
        response = session.get(rule['url'], headers={'Referer': rule['url']})
        response.raise_for_status()
        
        # Parse HTML to find download links
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a', href=True)
        
        # Find matching download link
        package_url = None
        for link in links:
            href = link.get('href', '')
            if re.match(rule['pattern'], href):
                package_url = href
                break
        
        if not package_url:
            raise ValueError(f"Could not find download link for {fir_code}")
        
        # Extract filename from URL
        original_filename = package_url.split('/')[-1]
        
        # Prepend FIR code to filename for better organization
        filename = f"{fir_code}-{original_filename}"
        
        # Create unique filename if file already exists
        target_path = self._get_unique_filepath(self.config.download_dir / filename)
        
        print(f"📥 Downloading {filename}...")
        print(f"   URL: {package_url}")
        print(f"   Target: {target_path}")
        
        # Download the file using the same session with proper referrer
        download_headers = {
            'Referer': rule['url'],  # This is crucial!
            'Accept': 'application/zip,application/octet-stream,*/*'
        }
        
        print(f"   Using session with referrer: {rule['url']}")
        response = session.get(package_url, headers=download_headers, stream=True)
        response.raise_for_status()
        
        # Check if we got redirected (which would indicate the download failed)
        if response.url != package_url:
            raise ValueError(f"Download was redirected to {response.url} - this usually means the download link is protected")
        
        # Check content type
        content_type = response.headers.get('content-type', '')
        if 'text/html' in content_type:
            raise ValueError(f"Got HTML response instead of file - download link may be protected or expired")
        
        # Ensure download directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Download with progress indication
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        
        with open(target_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    
                    if total_size > 0:
                        progress = (downloaded_size / total_size) * 100
                        print(f"\r   Progress: {progress:.1f}%", end='', flush=True)
        
        print(f"\n✓ Downloaded successfully")
        
        # Verify the downloaded file is actually a ZIP
        if target_path.stat().st_size < 1000000:  # Less than 1MB is suspicious for AIRAC package
            print(f"⚠️  Warning: Downloaded file is only {target_path.stat().st_size} bytes - this may indicate a failed download")
        
        try:
            import zipfile
            with zipfile.ZipFile(target_path, 'r') as zip_test:
                zip_test.testzip()
            print(f"✓ ZIP file verification passed")
        except zipfile.BadZipFile:
            target_path.unlink()  # Delete the bad file
            raise ValueError(f"Downloaded file is not a valid ZIP archive - download may have failed due to website protection")
        
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
        
        # Initialize package info
        package_info = {
            'path': package_path,
            'name': filename,
            'fir': '',
            'airac': '',
            'version': ''
        }
        
        # Try to match different package naming patterns
        patterns = [
            # EDGG-Full-Package_20250613220519-241301-0016 format (with FIR prefix)
            r'^([A-Z]{4,5})-.*?(\d{4}).*?(\d+).*'
,
            # EXCXO-Install_2410 format (with FIR prefix)
            r'^([A-Z]{4,5})-.*?(\d{4}).*'
,
            # Full_Package_20250710205541-241301-17 format (without FIR prefix)
            r'^(?:Full_Package|Install|FIS).*?(\d{4}).*?(\d+).*'
,
            # Simple patterns
            r'^([A-Z]{4,5}).*?(\d{4})'

        ]
        
        for pattern in patterns:
            match = re.match(pattern, filename)
            if match:
                groups = match.groups()
                
                # For patterns with FIR code as first group
                if len(groups) >= 2 and groups[0].isalpha():
                    package_info['fir'] = groups[0]
                    package_info['airac'] = groups[1] if len(groups) >= 2 else ''
                    package_info['version'] = groups[2] if len(groups) >= 3 else ''
                # For patterns without FIR code (Full_Package format)
                elif len(groups) >= 1:
                    package_info['airac'] = groups[0]
                    package_info['version'] = groups[1] if len(groups) >= 2 else ''
                break
        
        # Handle special cases
        if package_info['fir'] and package_info['fir'].startswith('EXCXO'):
            package_info['fir'] = 'EXCXO'
        
        # If we couldn't extract AIRAC, try to get it from anywhere in filename
        if not package_info['airac']:
            airac_match = re.search(r'(\d{4})', filename)
            if airac_match:
                package_info['airac'] = airac_match.group(1)
        
        # If we still don't have FIR code, we have a problem
        if not package_info['fir']:
            raise ValueError(f"Could not determine FIR from filename: {filename}. "
                           f"Please ensure filename includes FIR code or use auto-download with FIR parameter.")
        
        return package_info