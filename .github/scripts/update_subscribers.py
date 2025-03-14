import re
import time
import random
import requests
from pathlib import Path
from typing import Dict, List
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

def extract_channel_ids(content: str) -> List[str]:
    """Extract YouTube channel IDs from markdown content."""
    patterns = [
        r'youtube\.com/@([A-Za-z0-9_-]+)',  # @username format
        r'youtube\.com/channel/([A-Za-z0-9_-]+)',  # channel ID format
        r'youtube\.com/c/([A-Za-z0-9_-]+)'  # custom URL format
    ]
    
    channel_ids = []
    for pattern in patterns:
        matches = re.finditer(pattern, content)
        channel_ids.extend(match.group(1) for match in matches)
    
    return channel_ids

def get_channel_stats(channel_id: str) -> Dict:
    """Get channel statistics from Social Blade."""
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        url = f'https://socialblade.com/youtube/channel/{channel_id}'
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        stats = {
            'subscribers': '0',
            'views': '0',
            'videos': '0',
            'handle': channel_id
        }
        
        stats_elements = soup.find_all('div', {'class': 'stats'})
        for element in stats_elements:
            if 'subscribers' in element.text.lower():
                stats['subscribers'] = element.find('span').text.strip()
            elif 'views' in element.text.lower():
                stats['views'] = element.find('span').text.strip()
            
        time.sleep(random.uniform(2, 5))
        return stats
        
    except Exception as e:
        print(f"Error getting stats for {channel_id}: {e}")
        return None

def update_markdown_file(file_path: str, stats: Dict[str, Dict]) -> None:
    """Update channel statistics in markdown files."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for channel_id, channel_stats in stats.items():
        # Update statistics section using raw strings for patterns
        stats_pattern = r'### 📊 Channel Statistics\n(.*?)###'
        stats_replacement = f'''### 📊 Channel Statistics
- **Subscribers:** {channel_stats["subscribers"]}
- **Total Views:** {channel_stats["views"]}
- **Videos:** {channel_stats["videos"]}
- **Started:** {channel_stats.get("started", "N/A")}
- **Last Video:** {channel_stats.get("last_video", "N/A")}

###'''
        content = re.sub(stats_pattern, stats_replacement, content, flags=re.DOTALL)
        
        # Update badges using raw strings for patterns
        patterns = [
            fr'youtube\.com/@{channel_id}.*?\n.*?!\[YouTube Channel Subscribers\].*?\)',
            fr'youtube\.com/channel/{channel_id}.*?\n.*?!\[YouTube Channel Subscribers\].*?\)',
            fr'youtube\.com/c/{channel_id}.*?\n.*?!\[YouTube Channel Subscribers\].*?\)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            if match:
                old_badge = match.group(0)
                new_badge = re.sub(
                    r'!\[YouTube Channel Subscribers\].*?\)',
                    f'![YouTube Channel Subscribers](https://img.shields.io/badge/subscribers-{channel_stats["subscribers"]}-red)',
                    old_badge
                )
                content = content.replace(old_badge, new_badge)
        
        # Update view count badge
        view_pattern = r'!\[YouTube Channel Views\].*?\)'
        view_replacement = f'![YouTube Channel Views](https://img.shields.io/badge/views-{channel_stats["views"]}-blue)'
        content = re.sub(view_pattern, view_replacement, content)
        
        # Update last updated date
        date_pattern = r'Last updated: .*$'
        date_replacement = f'Last updated: {time.strftime("%Y-%m-%d")}'
        content = re.sub(date_pattern, date_replacement, content, flags=re.MULTILINE)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    """Main function to update channel statistics."""
    categories_dir = Path(__file__).parent.parent.parent / 'categories'
    
    for md_file in categories_dir.glob('*.md'):
        if md_file.name == 'template.md':
            continue
            
        print(f"Processing {md_file}")
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        channel_ids = extract_channel_ids(content)
        if channel_ids:
            stats = {}
            for channel_id in channel_ids:
                channel_stats = get_channel_stats(channel_id)
                if channel_stats:
                    stats[channel_id] = channel_stats
            
            if stats:
                update_markdown_file(str(md_file), stats)
                print(f"Updated {len(stats)} channels in {md_file}")

if __name__ == '__main__':
    main()