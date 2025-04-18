import re
import time
import random
import requests
from pathlib import Path
from typing import Dict, List
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import logging

# Configurar el registro para depuración
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Crear instancia de UserAgent para rotar User-Agent
ua = UserAgent()

def get_channel_stats(channel_id: str) -> Dict:
    """Get channel statistics from Social Blade."""
    headers = {
        'User-Agent': ua.random,  # Rotar User-Agent
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    proxies = {
        'http': None,
        'https': None
    }

    url = f'https://socialblade.com/youtube/handle/{channel_id.strip()}'

    try:
        logger.info(f"Trying URL: {url}")
        response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
        time.sleep(random.uniform(3, 6))  # Agregar un retraso aleatorio entre 3 y 6 segundos para evitar bloqueos
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            sub_element = soup.find('span', {'id': 'youtube-stats-header-subs'})
            if sub_element:
                subscribers = sub_element.get_text(strip=True)
                logger.info(f"Found stats for {channel_id} on {url}: {subscribers} subscribers")
                return {
                    'subscribers': subscribers,
                    'views': '0',
                    'videos': '0',
                    'handle': channel_id
                }
        elif response.status_code == 403:
            logger.warning(f"Access denied for {url}. Consider using a proxy or VPN.")
        else:
            logger.warning(f"Failed to fetch {url}, status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error for URL {url}: {e}")

    logger.warning(f"No stats found for {channel_id} after trying the URL.")
    return {
        'subscribers': '0',
        'views': '0',
        'videos': '0',
        'handle': channel_id
    }

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