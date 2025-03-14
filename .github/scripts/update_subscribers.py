import re
import time
import random
import requests
from pathlib import Path
from typing import Dict, List
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

def get_channel_stats(channel_id: str) -> Dict:
    """Get channel statistics from Social Blade."""
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        # Try different URL formats for SocialBlade
        urls = [
            f'https://socialblade.com/youtube/user/{channel_id}',
            f'https://socialblade.com/youtube/channel/{channel_id}',
            f'https://socialblade.com/youtube/c/{channel_id}',
            f'https://socialblade.com/youtube/user/@{channel_id}'
        ]
        
        stats = None
        for url in urls:
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for subscriber count in different formats
                    sub_elements = soup.select('div[style*="font-weight: bold"]')
                    for element in sub_elements:
                        text = element.get_text(strip=True)
                        if 'subscribers' in text.lower():
                            stats = {
                                'subscribers': text.split()[0],
                                'views': '0',
                                'videos': '0',
                                'handle': channel_id
                            }
                            break
                    
                    if stats:
                        break
                        
            except Exception as e:
                print(f"Error trying URL {url}: {e}")
                continue
                
            time.sleep(random.uniform(2, 5))  # Delay between attempts
        
        return stats or {
            'subscribers': '0',
            'views': '0',
            'videos': '0',
            'handle': channel_id
        }
        
    except Exception as e:
        print(f"Error getting stats for {channel_id}: {e}")
        return None

def update_markdown_file(file_path: str, stats: Dict[str, Dict]) -> None:
    """Update channel statistics in markdown files."""
    print(f"Updating file: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    updated = False
    for channel_id, channel_stats in stats.items():
        print(f"Processing channel: {channel_id}")
        
        # Try to find the channel section
        channel_patterns = [
            fr'(?s)youtube\.com/@{channel_id}.*?(!?\[YouTube Channel Subscribers\].*?\))',
            fr'(?s)youtube\.com/channel/{channel_id}.*?(!?\[YouTube Channel Subscribers\].*?\))',
            fr'(?s)youtube\.com/c/{channel_id}.*?(!?\[YouTube Channel Subscribers\].*?\))'
        ]
        
        for pattern in channel_patterns:
            matches = list(re.finditer(pattern, content, re.MULTILINE))
            if matches:
                for match in matches:
                    old_badge = match.group(1)
                    new_badge = f'![YouTube Channel Subscribers](https://img.shields.io/badge/subscribers-{channel_stats["subscribers"]}-red)'
                    if old_badge != new_badge:
                        content = content.replace(old_badge, new_badge)
                        print(f"Updated badge for {channel_id}: {channel_stats['subscribers']} subscribers")
                        updated = True
    
    if updated:
        print(f"Writing updates to {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    else:
        print(f"No updates needed for {file_path}")

def extract_channel_ids(content: str) -> List[str]:
    """Extract YouTube channel IDs and handles from markdown content."""
    patterns = [
        r'youtube\.com/@([A-Za-z0-9_-]+)',  # @username format
        r'youtube\.com/channel/([A-Za-z0-9_-]+)',  # channel ID format
        r'youtube\.com/c/([A-Za-z0-9_-]+)',  # custom URL format
        r'\[@([A-Za-z0-9_-]+)\]\(https://youtube\.com'  # markdown link format
    ]
    
    channel_ids = []
    for pattern in patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            channel_id = match.group(1)
            if channel_id not in channel_ids:
                channel_ids.append(channel_id)
    
    return channel_ids

def main():
    """Main function to update channel statistics."""
    categories_dir = Path(__file__).parent.parent.parent / 'categories'
    
    for md_file in categories_dir.glob('*.md'):
        if md_file.name == 'template.md':
            continue
            
        print(f"\nProcessing {md_file}")
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        channel_ids = extract_channel_ids(content)
        if channel_ids:
            print(f"Found channels: {', '.join(channel_ids)}")
            stats = {}
            for channel_id in channel_ids:
                channel_stats = get_channel_stats(channel_id)
                if channel_stats:
                    stats[channel_id] = channel_stats
                    print(f"Retrieved stats for {channel_id}: {channel_stats['subscribers']} subscribers")
            
            if stats:
                update_markdown_file(str(md_file), stats)
                print(f"Updated {len(stats)} channels in {md_file}")

if __name__ == '__main__':
    main()