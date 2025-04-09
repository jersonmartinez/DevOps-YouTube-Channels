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

def get_youtube_channel_stats(channel_url: str) -> Dict:
    """Get subscriber count from a YouTube channel page."""
    headers = {
        'User-Agent': ua.random,
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    try:
        logger.info(f"Trying URL: {channel_url}")
        response = requests.get(channel_url, headers=headers, timeout=10)
        response.raise_for_status()  # Lanza una excepción para códigos de error HTTP
        time.sleep(random.uniform(5, 10))  # Retraso aleatorio

        soup = BeautifulSoup(response.text, 'html.parser')

        # Buscar el elemento que contiene el número de suscriptores.
        # Este selector puede necesitar ser ajustado si YouTube cambia su estructura.
        subscriber_element = soup.find('yt-formatted-string', {'id': 'subscriber-count', 'class': 'style-scope ytd-c4-tabbed-header-renderer'})
        if not subscriber_element:
            subscriber_element = soup.find('yt-formatted-string', {'id': 'owner-sub-count', 'class': 'style-scope ytd-video-owner-renderer'})

        if subscriber_element:
            subscriber_text = subscriber_element.get_text(strip=True)
            logger.info(f"Found subscriber text for {channel_url}: {subscriber_text}")
            subscribers = parse_subscriber_count(subscriber_text)
            return {
                'subscribers': str(subscribers),
                'views': 'N/A',  # No se extraen las vistas de esta página
                'videos': 'N/A', # No se extraen la cantidad de videos de esta página
                'handle': channel_url.split('/')[-1] if '@' in channel_url else channel_url.split('/')[-1]
            }
        else:
            logger.warning(f"Could not find subscriber count on {channel_url}")
            return {
                'subscribers': '0',
                'views': 'N/A',
                'videos': 'N/A',
                'handle': channel_url.split('/')[-1] if '@' in channel_url else channel_url.split('/')[-1]
            }

    except requests.exceptions.RequestException as e:
        logger.error(f"Request error for URL {channel_url}: {e}")
        return {
            'subscribers': '0',
            'views': 'N/A',
            'videos': 'N/A',
            'handle': channel_url.split('/')[-1] if '@' in channel_url else channel_url.split('/')[-1]
        }

def parse_subscriber_count(text: str) -> int:
    """Parse abbreviated subscriber counts (e.g., 1.2M)."""
    text = text.lower()
    multiplier = 1
    if 'k' in text:
        multiplier = 1000
        text = text.replace('k', '')
    elif 'm' in text:
        multiplier = 1000000
        text = text.replace('m', '')
    elif 'b' in text:
        multiplier = 1000000000
        text = text.replace('b', '')

    try:
        return int(float(text) * multiplier)
    except ValueError:
        return 0

def update_markdown_file(file_path: str, stats: Dict[str, Dict]) -> None:
    """Update channel statistics in markdown files."""
    print(f"Updating file: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    updated = False
    for channel_url, channel_stats in stats.items():
        channel_handle = channel_stats['handle']
        print(f"Processing channel: {channel_handle} ({channel_url})")

        # Buscar y reemplazar el badge de suscriptores
        patterns_subs = [
            fr'(?s){re.escape(channel_url)}.*?(!?\[YouTube Channel Subscribers\]\(.*?\))',
            fr'(?s)youtube\.com/(?:@|channel/|c/){re.escape(channel_handle)}.*?(!?\[YouTube Channel Subscribers\]\(.*?\))'
        ]
        new_badge_subs = f'![YouTube Channel Subscribers](https://img.shields.io/badge/subscribers-{channel_stats["subscribers"]}-red)'

        for pattern in patterns_subs:
            content, found_subs = re.subn(pattern, lambda m: m.group(0).replace(m.group(1), new_badge_subs) if m.group(1) else m.group(0) + new_badge_subs, content)
            if found_subs > 0:
                print(f"Updated subscriber badge for {channel_handle}: {channel_stats['subscribers']} subscribers")
                updated = True
                break # Pasar al siguiente canal

    if updated:
        print(f"Writing updates to {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    else:
        print(f"No updates needed for {file_path}")

def extract_channel_urls(content: str) -> List[str]:
    """Extract YouTube channel URLs from markdown content."""
    patterns = [
        r'(https?://(?:www\.)?youtube\.com/@[A-Za-z0-9_-]+)',
        r'(https?://(?:www\.)?youtube\.com/channel/[A-Za-z0-9_-]+)',
        r'(https?://(?:www\.)?youtube\.com/c/[A-Za-z0-9_-]+)'
    ]

    channel_urls = set()
    for pattern in patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            channel_urls.add(match.group(1))

    return list(channel_urls)

def main():
    """Main function to update channel statistics from YouTube."""
    categories_dir = Path(__file__).parent.parent.parent / 'categories'

    for md_file in categories_dir.glob('*.md'):
        if md_file.name == 'template.md':
            continue

        print(f"\nProcessing {md_file}")

        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        channel_urls = extract_channel_urls(content)
        if channel_urls:
            print(f"Found channel URLs: {', '.join(channel_urls)}")
            stats = {}
            for url in channel_urls:
                channel_stats = get_youtube_channel_stats(url)
                if channel_stats:
                    stats[url] = channel_stats
                    print(f"Retrieved stats for {channel_stats['handle']}: {channel_stats['subscribers']} subscribers")

            if stats:
                update_markdown_file(str(md_file), stats)
                print(f"Updated {len(stats)} channels in {md_file}")

if __name__ == '__main__':
    main()