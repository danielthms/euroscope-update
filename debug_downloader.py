#!/usr/bin/env python3
"""
Debug tool for investigating download issues with aero-nav.com
"""

import requests
from bs4 import BeautifulSoup
import re
import sys

def debug_site(fir_code='EDGG'):
    """Debug the aero-nav.com site to understand its structure"""
    
    # Updated to match PowerShell script exactly
    urls = {
        'EDGG': 'https://files.aero-nav.com/EDXX',  # PowerShell goes to /EDXX for EDGG!
        'EDMM': 'https://files.aero-nav.com/EDXX', 
        'EDWW': 'https://files.aero-nav.com/EDXX',
        'EDXX': 'https://files.aero-nav.com/EDXX',
        'EXCXO': 'https://files.aero-nav.com/EXCXO',
        'BIRD': 'https://files.aero-nav.com/SCA',
        'LPPO': 'https://files.aero-nav.com/LPPO'
    }
    
    # PowerShell patterns
    patterns = {
        'EDGG': r'https://files\.aero-nav\.com/EDGG/Full.*Package_.*\.zip',
        'EDMM': r'https://files\.aero-nav\.com/EDMM/Full.*Package_.*\.zip',
        'EDWW': r'https://files\.aero-nav\.com/EDWW/Full.*Package_.*\.zip',
        'EDXX': r'https://files\.aero-nav\.com/EDXX/FIS_.*\.zip',
        'EXCXO': r'https://files\.aero-nav\.com/EXCXO/EXCXO-Install_.*\.zip',
        'BIRD': r'https://files\.aero-nav\.com/BIRD/Install-Pack_.*\.zip',
        'LPPO': r'https://files\.aero-nav\.com/LPPO/Install-Package_.*\.zip'
    }
    
    if fir_code not in urls:
        print(f"Unknown FIR: {fir_code}")
        return
    
    url = urls[fir_code]
    pattern = patterns.get(fir_code, r'.*\.zip')
    
    print(f"🔍 Debugging {fir_code} downloads from {url}")
    print(f"📋 PowerShell pattern: {pattern}")
    print("=" * 80)
    
    # Create session with proper headers like PowerShell
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    try:
        # Get the page with referer (like PowerShell)
        print("📡 Fetching page with session and referer...")
        response = session.get(url, headers={'Referer': url})
        response.raise_for_status()
        
        print(f"✓ Response: {response.status_code}")
        print(f"✓ Content-Type: {response.headers.get('content-type', 'unknown')}")
        print(f"✓ Content-Length: {len(response.content)} bytes")
        print(f"✓ Set-Cookie: {response.headers.get('set-cookie', 'none')}")
        print()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all links
        all_links = soup.find_all('a', href=True)
        all_hrefs = [link.get('href') for link in all_links]
        
        print(f"🔗 Found {len(all_links)} total links")
        
        # Filter ZIP links
        zip_links = [href for href in all_hrefs if '.zip' in href.lower()]
        print(f"📦 Found {len(zip_links)} ZIP links:")
        
        for i, link in enumerate(zip_links, 1):
            print(f"   {i:2d}. {link}")
        
        print()
        
        # Test PowerShell pattern
        print(f"🧪 Testing PowerShell pattern: {pattern}")
        matches = []
        for link in zip_links:
            if re.match(pattern, link):
                matches.append(link)
        
        print(f"   Found {len(matches)} pattern matches:")
        for i, match in enumerate(matches, 1):
            print(f"     {i}. {match}")
            
            # Test download for first match
            if i == 1:
                print(f"\n🧪 Testing download for: {match}")
                test_download_with_session(session, match)
        
        print()
        
        # Look for specific FIR links
        fir_links = [link for link in zip_links if fir_code.lower() in link.lower()]
        print(f"🎯 Found {len(fir_links)} {fir_code}-specific links:")
        
        for i, link in enumerate(fir_links, 1):
            print(f"   {i:2d}. {link}")
        
        # Show raw page content sample
        print("\n🌐 Raw page content (first 2000 chars):")
        print("-" * 80)
        print(response.text[:2000])
        print("-" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_download_with_session(session, url):
    """Test downloading with the same session"""
    try:
        # Test HEAD request
        print(f"     📡 HEAD request...")
        head_response = session.head(url)
        print(f"        Status: {head_response.status_code}")
        print(f"        Content-Type: {head_response.headers.get('content-type', 'unknown')}")
        print(f"        Content-Length: {head_response.headers.get('content-length', 'unknown')}")
        
        # Test partial GET request
        print(f"     📡 Partial GET request...")
        response = session.get(url, stream=True)
        first_chunk = next(response.iter_content(chunk_size=1024), b'')
        
        print(f"        Status: {response.status_code}")
        print(f"        Content-Type: {response.headers.get('content-type', 'unknown')}")
        print(f"        First 50 bytes: {first_chunk[:50]}")
        
        if first_chunk.startswith(b'PK'):
            print(f"        ✓ Valid ZIP file signature!")
        elif b'<html' in first_chunk.lower():
            print(f"        ❌ HTML content (error page)")
        else:
            print(f"        ⚠️  Unknown content type")
            
    except Exception as e:
        print(f"        ❌ Error: {e}")

def test_download(url):
    """Test downloading a specific URL with session"""
    print(f"\n🧪 Testing download: {url}")
    print("=" * 80)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    })
    
    test_download_with_session(session, url)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1].startswith('http'):
            test_download(sys.argv[1])
        else:
            debug_site(sys.argv[1])
    else:
        print("Usage:")
        print("  python debug_downloader.py EDGG          # Debug FIR downloads")
        print("  python debug_downloader.py https://...   # Test specific URL")
        print("\nSupported FIRs: EDGG, EDMM, EDWW, EDXX, EXCXO, BIRD, LPPO")