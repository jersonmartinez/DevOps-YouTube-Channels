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

# Lista de proxies (puedes obtener listas gratuitas online, pero ten cuidado con su fiabilidad)
# Considera usar un servicio de proxies de pago para mayor fiabilidad.
PROXY_LIST = [
    # Ejemplo de formato: 'http://usuario:contraseña@ip:puerto' o 'http://ip:puerto'
    # "http://10.10.1.10:3128",
    # "http://user:pass@10.10.1.11:8080",
]

def get_random_proxy():
    if PROXY_LIST:
        return {'http': random.choice(PROXY_LIST), 'https': random.choice(PROXY_LIST)}
    return {'http': None, 'https': None}

def get_channel_stats(channel_id: str) -> Dict:
    """Get channel statistics from Social Blade."""
    headers = {
        'User-Agent': ua.random,  # Rotar User-Agent
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    proxies = get_random_proxy()
    if proxies['http']:
        logger.info(f"Using proxy: {proxies['http']}")

    url = f'https://socialblade.com/youtube/handle/{channel_id.strip()}'

    try:
        logger.info(f"Trying URL: {url}")
        response = requests.get(url, headers=headers, proxies=proxies, timeout=15)  # Aumentar el timeout
        time.sleep(random.uniform(5, 10))  # Aumentar el retraso aleatorio
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            sub_element = soup.find('span', {'id': 'youtube-stats-header-subs'})
            views_element = soup.find('div', {'id': 'youtube-stats-header-views'})
            videos_element = soup.find('div', {'id': 'youtube-stats-header-uploads'})

            subscribers = sub_element.get_text(strip=True) if sub_element else '0'
            views = views_element.get_text(strip=True).split(' ')[0].replace(',', '') if views_element else '0'
            videos = videos_element.get_text(strip=True).replace(',', '') if videos_element else '0'

            logger.info(f"Found stats for {channel_id} on {url}: Subscribers={subscribers}, Views={views}, Videos={videos}")
            return {
                'subscribers': subscribers,
                'views': views,
                'videos': videos,
                'handle': channel_id
            }
        elif response.status_code == 403:
            logger.warning(f"Access denied for {url} using proxy {proxies}. Consider using more proxies or a VPN.")
        else:
            logger.warning(f"Failed to fetch {url}, status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error for URL {url} with proxy {proxies}: {e}")

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

        # Try to find the channel section and update the subscriber badge
        patterns_subs = [
            fr'(?s)youtube\.com/@{re.escape(channel_id)}.*?(!?\[YouTube Channel Subscribers\]\(.*?\))',
            fr'(?s)youtube\.com/channel/{re.escape(channel_id)}.*?(!?\[YouTube Channel Subscribers\]\(.*?\))',
            fr'(?s)youtube\.com/c/{re.escape(channel_id)}.*?(!?\[YouTube Channel Subscribers\]\(.*?\))'
        ]
        new_badge_subs = f'![YouTube Channel Subscribers](https://img.shields.io/badge/subscribers-{channel_stats["subscribers"]}-red)'

        for pattern in patterns_subs:
            content, found_subs = re.subn(pattern, lambda m: m.group(0).replace(m.group(1), new_badge_subs) if m.group(1) else m.group(0) + new_badge_subs, content)
            if found_subs > 0:
                print(f"Updated subscriber badge for {channel_id}: {channel_stats['subscribers']} subscribers")
                updated = True
                break # Move to the next channel after updating

        # Try to find and update the views badge
        patterns_views = [
            fr'(?s)youtube\.com/@{re.escape(channel_id)}.*?(!?\[YouTube Channel Views\]\(.*?\))',
            fr'(?s)youtube\.com/channel/{re.escape(channel_id)}.*?(!?\[YouTube Channel Views\]\(.*?\))',
            fr'(?s)youtube\.com/c/{re.escape(channel_id)}.*?(!?\[YouTube Channel Views\]\(.*?\))'
        ]
        new_badge_views = f'![YouTube Channel Views](https://img.shields.io/badge/views-{channel_stats["views"]}-blue)'

        for pattern in patterns_views:
            content, found_views = re.subn(pattern, lambda m: m.group(0).replace(m.group(1), new_badge_views) if m.group(1) else m.group(0) + new_badge_views, content)
            if found_views > 0:
                print(f"Updated views badge for {channel_id}: {channel_stats['views']} views")
                updated = True
                break

        # Try to find and update the videos badge
        patterns_videos = [
            fr'(?s)youtube\.com/@{re.escape(channel_id)}.*?(!?\[YouTube Channel Videos\]\(.*?\))',
            fr'(?s)youtube\.com/channel/{re.escape(channel_id)}.*?(!?\[YouTube Channel Videos\]\(.*?\))',
            fr'(?s)youtube\.com/c/{re.escape(channel_id)}.*?(!?\[YouTube Channel Videos\]\(.*?\))'
        ]
        new_badge_videos = f'![YouTube Channel Videos](https://img.shields.io/badge/videos-{channel_stats["videos"]}-green)'

        for pattern in patterns_videos:
            content, found_videos = re.subn(pattern, lambda m: m.group(0).replace(m.group(1), new_badge_videos) if m.group(1) else m.group(0) + new_badge_videos, content)
            if found_videos > 0:
                print(f"Updated video badge for {channel_id}: {channel_stats['videos']} videos")
                updated = True
                break

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
        r'\[@([A-Za-z0-9_-]+)\]\(https://youtube\.com',  # markdown link format
        r'\[.*?\]\(https://www\.youtube\.com/channel/([A-Za-z0-9_-]+)\)', # Markdown link con /channel/
        r'\[.*?\]\(https://www\.youtube\.com/@([A-Za-z0-9_-]+)\)', # Markdown link con @
        r'\[.*?\]\(https://www\.youtube\.com/c/([A-Za-z0-9_-]+)\)' # Markdown link con /c/
    ]

    channel_ids = set() # Usar un conjunto para evitar duplicados
    for pattern in patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            channel_id = match.group(1)
            channel_ids.add(channel_id)

    return list(channel_ids)

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
                    print(f"Retrieved stats for {channel_id}: Subscribers={channel_stats['subscribers']}, Views={channel_stats['views']}, Videos={channel_stats['videos']}")

            if stats:
                update_markdown_file(str(md_file), stats)
                print(f"Updated {len(stats)} channels in {md_file}")

if __name__ == '__main__':
    main()