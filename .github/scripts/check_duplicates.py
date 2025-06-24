#!/usr/bin/env python3
"""
Check for duplicate YouTube channels across all markdown files.
Used by GitHub Actions to ensure no duplicates are added.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DuplicateChecker:
    """Check for duplicate channels across files."""
    
    def __init__(self):
        self.channels_by_url = defaultdict(list)
        self.channels_by_name = defaultdict(list)
        self.all_channels = []
        
    def normalize_url(self, url: str) -> str:
        """Normalize YouTube URLs for comparison."""
        if not url:
            return ""
            
        # Remove trailing slashes and normalize format
        url = url.rstrip('/')
        
        # Convert different YouTube URL formats to a standard format
        patterns = [
            (r'https?://(?:www\.)?youtube\.com/@([\w-]+)', r'youtube.com/@\1'),
            (r'https?://(?:www\.)?youtube\.com/c/([\w-]+)', r'youtube.com/c/\1'),
            (r'https?://(?:www\.)?youtube\.com/channel/([\w-]+)', r'youtube.com/channel/\1'),
            (r'https?://(?:www\.)?youtube\.com/user/([\w-]+)', r'youtube.com/user/\1')
        ]
        
        for pattern, replacement in patterns:
            match = re.match(pattern, url, re.IGNORECASE)
            if match:
                return re.sub(pattern, replacement, url, flags=re.IGNORECASE)
                
        return url.lower()
    
    def normalize_name(self, name: str) -> str:
        """Normalize channel names for comparison."""
        if not name:
            return ""
            
        # Remove common prefixes/suffixes and normalize
        name = name.strip()
        
        # Remove badges and emojis
        name = re.sub(r'⭐.*?DESTACADO', '', name)
        name = re.sub(r'[⭐🌟✨🔥💡🚀📺🎯]', '', name)
        
        # Normalize whitespace
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name.lower()
    
    def extract_channels_from_file(self, file_path: Path) -> List[Dict]:
        """Extract channel information from a markdown file."""
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
                
                # Extract author name if possible
                author_match = re.search(r'\*\*([^*]+)\*\*', channel_content)
                author_name = author_match.group(1) if author_match else ""
                
                channel_info = {
                    'name': channel_name,
                    'original_name': channel_name,
                    'url': youtube_url,
                    'original_url': youtube_url,
                    'author': author_name,
                    'file': file_path.name,
                    'file_path': str(file_path)
                }
                
                channels.append(channel_info)
                
            return channels
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return []
    
    def load_all_channels(self, file_paths: List[Path]):
        """Load channels from all specified files."""
        self.all_channels = []
        
        for file_path in file_paths:
            logger.info(f"Loading channels from {file_path}")
            channels = self.extract_channels_from_file(file_path)
            self.all_channels.extend(channels)
            
            # Index by normalized URL and name
            for channel in channels:
                normalized_url = self.normalize_url(channel['url'])
                normalized_name = self.normalize_name(channel['name'])
                
                if normalized_url:
                    self.channels_by_url[normalized_url].append(channel)
                if normalized_name:
                    self.channels_by_name[normalized_name].append(channel)
    
    def find_url_duplicates(self) -> List[Dict]:
        """Find channels with duplicate URLs."""
        duplicates = []
        
        for normalized_url, channels in self.channels_by_url.items():
            if len(channels) > 1:
                duplicates.append({
                    'type': 'url',
                    'normalized_value': normalized_url,
                    'channels': channels,
                    'count': len(channels)
                })
                
        return duplicates
    
    def find_name_duplicates(self) -> List[Dict]:
        """Find channels with very similar names."""
        duplicates = []
        
        for normalized_name, channels in self.channels_by_name.items():
            if len(channels) > 1:
                # Check if they're actually different channels (different URLs)
                unique_urls = set(self.normalize_url(ch['url']) for ch in channels)
                if len(unique_urls) > 1:
                    duplicates.append({
                        'type': 'name',
                        'normalized_value': normalized_name,
                        'channels': channels,
                        'count': len(channels)
                    })
                    
        return duplicates
    
    def find_similar_channels(self) -> List[Dict]:
        """Find channels that might be the same creator with different names."""
        similar = []
        
        # Group by author name
        authors = defaultdict(list)
        for channel in self.all_channels:
            if channel['author']:
                normalized_author = channel['author'].lower().strip()
                authors[normalized_author].append(channel)
        
        for author, channels in authors.items():
            if len(channels) > 1:
                # Check if they have different URLs
                unique_urls = set(self.normalize_url(ch['url']) for ch in channels)
                if len(unique_urls) > 1:
                    similar.append({
                        'type': 'author',
                        'normalized_value': author,
                        'channels': channels,
                        'count': len(channels)
                    })
                    
        return similar
    
    def print_duplicate_report(self):
        """Print a comprehensive duplicate report."""
        url_duplicates = self.find_url_duplicates()
        name_duplicates = self.find_name_duplicates()
        similar_channels = self.find_similar_channels()
        
        total_issues = len(url_duplicates) + len(name_duplicates) + len(similar_channels)
        
        print(f"\n🔍 DUPLICATE CHECK REPORT")
        print(f"{'-'*60}")
        print(f"Total channels checked: {len(self.all_channels)}")
        print(f"Potential duplicate issues found: {total_issues}")
        
        # URL Duplicates (Critical)
        if url_duplicates:
            print(f"\n❌ CRITICAL: Exact URL Duplicates ({len(url_duplicates)})")
            print(f"{'-'*60}")
            for dup in url_duplicates:
                print(f"\n🔗 URL: {dup['channels'][0]['original_url']}")
                for channel in dup['channels']:
                    print(f"   📺 {channel['original_name']} (in {channel['file']})")
        
        # Name Duplicates (Warning)
        if name_duplicates:
            print(f"\n⚠️ WARNING: Similar Channel Names ({len(name_duplicates)})")
            print(f"{'-'*60}")
            for dup in name_duplicates:
                print(f"\n📝 Normalized name: {dup['normalized_value']}")
                for channel in dup['channels']:
                    print(f"   📺 {channel['original_name']} -> {channel['original_url']} (in {channel['file']})")
        
        # Similar Channels by Author (Info)
        if similar_channels:
            print(f"\n💡 INFO: Same Author, Different Channels ({len(similar_channels)})")
            print(f"{'-'*60}")
            for dup in similar_channels:
                print(f"\n👤 Author: {dup['normalized_value']}")
                for channel in dup['channels']:
                    print(f"   📺 {channel['original_name']} -> {channel['original_url']} (in {channel['file']})")
        
        if total_issues == 0:
            print(f"\n✅ No duplicates found! All channels are unique.")
        else:
            print(f"\n📋 Summary:")
            print(f"   🚨 Critical (URL duplicates): {len(url_duplicates)}")
            print(f"   ⚠️ Warnings (name duplicates): {len(name_duplicates)}")
            print(f"   💡 Info (same author): {len(similar_channels)}")
        
        return len(url_duplicates)  # Return critical issues count


def main():
    """Main function to check for duplicates."""
    root_dir = Path(__file__).parent.parent.parent
    
    # Files to check
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
        print("No markdown files found to check")
        sys.exit(0)
    
    # Check for duplicates
    checker = DuplicateChecker()
    checker.load_all_channels(existing_files)
    
    # Print report and get critical issues count
    critical_issues = checker.print_duplicate_report()
    
    # Exit with error code if there are critical duplicates
    if critical_issues > 0:
        print(f"\n🚨 Found {critical_issues} critical duplicate issues. Please review and fix.")
        sys.exit(1)
    else:
        print(f"\n🎉 No critical duplicates found!")
        sys.exit(0)


if __name__ == '__main__':
    main() 