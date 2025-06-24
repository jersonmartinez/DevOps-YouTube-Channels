#!/usr/bin/env python3
"""
Validate YouTube channel URLs and basic information.
Used by GitHub Actions to ensure quality of contributions.
"""

import re
import sys
import requests
import validators
from pathlib import Path
from typing import List, Dict, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ChannelValidator:
    """Validate YouTube channels for quality and correctness."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.validation_results = []
        
    def validate_url(self, url: str) -> Tuple[bool, str]:
        """Validate if URL is a valid YouTube channel URL."""
        if not validators.url(url):
            return False, "Invalid URL format"
            
        # Check if it's a YouTube URL
        youtube_patterns = [
            r'https?://(?:www\.)?youtube\.com/@[\w-]+',
            r'https?://(?:www\.)?youtube\.com/c/[\w-]+',
            r'https?://(?:www\.)?youtube\.com/channel/[\w-]+',
            r'https?://(?:www\.)?youtube\.com/user/[\w-]+'
        ]
        
        if not any(re.match(pattern, url) for pattern in youtube_patterns):
            return False, "Not a valid YouTube channel URL"
            
        return True, "Valid YouTube URL format"
    
    def check_url_accessibility(self, url: str) -> Tuple[bool, str]:
        """Check if the URL is accessible and returns a valid response."""
        try:
            response = self.session.get(url, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                # Check if it's actually a YouTube channel page
                if 'youtube.com' in response.url and any(keyword in response.text.lower() for keyword in ['channel', 'subscribe', 'videos']):
                    return True, f"Accessible (Status: {response.status_code})"
                else:
                    return False, "URL doesn't appear to be a valid YouTube channel"
            elif response.status_code == 404:
                return False, "Channel not found (404)"
            else:
                return False, f"HTTP Error: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, "Connection timeout"
        except requests.exceptions.ConnectionError:
            return False, "Connection error"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def validate_linkedin_url(self, url: str) -> Tuple[bool, str]:
        """Validate LinkedIn profile URL."""
        if not url or url.strip() == "":
            return True, "No LinkedIn URL provided (optional)"
            
        if not validators.url(url):
            return False, "Invalid LinkedIn URL format"
            
        linkedin_pattern = r'https?://(?:www\.)?linkedin\.com/in/[\w-]+'
        if not re.match(linkedin_pattern, url):
            return False, "Not a valid LinkedIn profile URL"
            
        return True, "Valid LinkedIn URL format"
    
    def extract_channels_from_file(self, file_path: Path) -> List[Dict]:
        """Extract channel information from markdown files."""
        try:
            content = file_path.read_text(encoding='utf-8')
            channels = []
            
            # Pattern to match channel sections
            channel_pattern = r'### (.+?)\n(.*?)(?=###|\Z)'
            
            for match in re.finditer(channel_pattern, content, re.DOTALL):
                channel_name = match.group(1).strip()
                channel_content = match.group(2).strip()
                
                # Extract YouTube URL
                youtube_match = re.search(r'https?://(?:www\.)?youtube\.com/[@/]([A-Za-z0-9_-]+)', channel_content)
                if not youtube_match:
                    continue
                    
                youtube_url = youtube_match.group(0)
                
                # Extract LinkedIn URL (optional)
                linkedin_match = re.search(r'https?://(?:www\.)?linkedin\.com/in/[\w-]+', channel_content)
                linkedin_url = linkedin_match.group(0) if linkedin_match else ""
                
                channels.append({
                    'name': channel_name,
                    'youtube_url': youtube_url,
                    'linkedin_url': linkedin_url,
                    'file': file_path.name
                })
                
            return channels
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return []
    
    def validate_channel(self, channel: Dict) -> Dict:
        """Validate a single channel."""
        results = {
            'name': channel['name'],
            'file': channel['file'],
            'youtube_url': channel['youtube_url'],
            'linkedin_url': channel['linkedin_url'],
            'validations': {}
        }
        
        # Validate YouTube URL format
        is_valid_format, format_msg = self.validate_url(channel['youtube_url'])
        results['validations']['url_format'] = {'valid': is_valid_format, 'message': format_msg}
        
        # Check YouTube URL accessibility
        if is_valid_format:
            is_accessible, access_msg = self.check_url_accessibility(channel['youtube_url'])
            results['validations']['url_accessibility'] = {'valid': is_accessible, 'message': access_msg}
        else:
            results['validations']['url_accessibility'] = {'valid': False, 'message': 'Skipped due to invalid format'}
        
        # Validate LinkedIn URL if provided
        is_valid_linkedin, linkedin_msg = self.validate_linkedin_url(channel['linkedin_url'])
        results['validations']['linkedin_format'] = {'valid': is_valid_linkedin, 'message': linkedin_msg}
        
        # Overall validation
        all_critical_valid = (
            results['validations']['url_format']['valid'] and
            results['validations']['url_accessibility']['valid'] and
            results['validations']['linkedin_format']['valid']
        )
        
        results['overall_valid'] = all_critical_valid
        
        return results
    
    def validate_files(self, file_paths: List[Path]) -> List[Dict]:
        """Validate channels in multiple files."""
        all_results = []
        
        for file_path in file_paths:
            logger.info(f"Validating channels in {file_path}")
            channels = self.extract_channels_from_file(file_path)
            
            for channel in channels:
                result = self.validate_channel(channel)
                all_results.append(result)
                
        return all_results
    
    def print_validation_report(self, results: List[Dict]):
        """Print a detailed validation report."""
        total_channels = len(results)
        valid_channels = sum(1 for r in results if r['overall_valid'])
        invalid_channels = total_channels - valid_channels
        
        print(f"\n🔍 VALIDATION REPORT")
        print(f"{'='*50}")
        print(f"Total channels validated: {total_channels}")
        print(f"✅ Valid channels: {valid_channels}")
        print(f"❌ Invalid channels: {invalid_channels}")
        print(f"Success rate: {(valid_channels/total_channels*100):.1f}%" if total_channels > 0 else "No channels found")
        
        if invalid_channels > 0:
            print(f"\n❌ ISSUES FOUND:")
            print(f"{'-'*50}")
            
            for result in results:
                if not result['overall_valid']:
                    print(f"\n📺 {result['name']} (in {result['file']})")
                    for validation_type, validation_result in result['validations'].items():
                        if not validation_result['valid']:
                            print(f"   ❌ {validation_type}: {validation_result['message']}")
        
        if valid_channels > 0:
            print(f"\n✅ VALID CHANNELS:")
            print(f"{'-'*50}")
            
            for result in results:
                if result['overall_valid']:
                    print(f"✅ {result['name']} (in {result['file']})")


def main():
    """Main function to validate channels."""
    root_dir = Path(__file__).parent.parent.parent
    
    # Files to validate
    files_to_check = [
        root_dir / 'categories' / 'automation.md',
        root_dir / 'categories' / 'cloud.md',
        root_dir / 'categories' / 'containers.md',
        root_dir / 'categories' / 'devsecops.md',
        root_dir / 'categories' / 'homelab.md',
        root_dir / 'categories' / 'platform-engineering.md',
        root_dir / 'Spanish-Channels.md',
        root_dir / 'English-Channels.md'
    ]
    
    # Only check files that exist
    existing_files = [f for f in files_to_check if f.exists()]
    
    if not existing_files:
        print("No markdown files found to validate")
        sys.exit(0)
    
    # Validate channels
    validator = ChannelValidator()
    results = validator.validate_files(existing_files)
    
    # Print report
    validator.print_validation_report(results)
    
    # Exit with error code if there are invalid channels
    invalid_count = sum(1 for r in results if not r['overall_valid'])
    if invalid_count > 0:
        print(f"\n⚠️ Found {invalid_count} invalid channels. Please review and fix.")
        sys.exit(1)
    else:
        print(f"\n🎉 All channels are valid!")
        sys.exit(0)


if __name__ == '__main__':
    main() 