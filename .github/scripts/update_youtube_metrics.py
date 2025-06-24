#!/usr/bin/env python3
"""
Update YouTube channel metrics using web scraping only.
No API keys required - uses multiple sources for reliability.
"""

import os
import re
import time
import random
import logging
from pathlib import Path
from typing import Dict, Optional, List, Tuple
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize UserAgent for rotating user agents
ua = UserAgent()


class YouTubeMetricsScraper:
    """Scrape YouTube channel metrics from various sources."""
    
    def __init__(self):
        self.session = requests.Session()
        self.metrics_cache = {}
        self.failed_channels = set()
        
    def get_headers(self) -> Dict[str, str]:
        """Get randomized headers for requests."""
        return {
            'User-Agent': ua.random,
            'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def extract_subscriber_count(self, text: str) -> Optional[int]:
        """Extract subscriber count from various text formats."""
        if not text:
            return None
            
        # Clean the text
        text = text.strip().upper().replace(',', '').replace(' ', '')
        
        # Try to find patterns like "1.5M", "500K", "1,234"
        patterns = [
            (r'(\d+\.?\d*)M', 1000000),
            (r'(\d+\.?\d*)K', 1000),
            (r'(\d+)', 1)
        ]
        
        for pattern, multiplier in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    number = float(match.group(1))
                    return int(number * multiplier)
                except:
                    continue
                    
        return None
    
    def scrape_socialblade(self, channel_id: str) -> Optional[Dict]:
        """Scrape metrics from Social Blade."""
        urls_to_try = [
            f'https://socialblade.com/youtube/c/{channel_id}',
            f'https://socialblade.com/youtube/channel/{channel_id}',
            f'https://socialblade.com/youtube/user/{channel_id}',
            f'https://socialblade.com/youtube/@{channel_id}'
        ]
        
        for url in urls_to_try:
            try:
                logger.info(f"Trying Social Blade: {url}")
                response = self.session.get(url, headers=self.get_headers(), timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Try multiple selectors for subscriber count
                    selectors = [
                        '#youtube-stats-header-subs',
                        '#YouTubeUserTopInfoBlock span[style*="font-size: 1.4em"]',
                        '#socialblade-user-content span[style*="font-weight: bold"]',
                        '.YouTubeUserTopInfo span'
                    ]
                    
                    for selector in selectors:
                        element = soup.select_one(selector)
                        if element:
                            count = self.extract_subscriber_count(element.get_text())
                            if count and count > 0:
                                logger.info(f"Found {count:,} subscribers for {channel_id} on Social Blade")
                                return {'subscribers': count, 'source': 'socialblade'}
                                
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                logger.debug(f"Error scraping Social Blade for {channel_id}: {e}")
                continue
                
        return None
    
    def scrape_youtube_direct(self, channel_id: str) -> Optional[Dict]:
        """Try to scrape directly from YouTube (lightweight approach)."""
        urls_to_try = [
            f'https://www.youtube.com/@{channel_id}/about',
            f'https://www.youtube.com/c/{channel_id}/about',
            f'https://www.youtube.com/channel/{channel_id}/about'
        ]
        
        for url in urls_to_try:
            try:
                logger.info(f"Trying YouTube direct: {url}")
                response = self.session.get(url, headers=self.get_headers(), timeout=10)
                
                if response.status_code == 200:
                    # Look for subscriber count in the page
                    patterns = [
                        r'"subscriberCountText":\s*{\s*"simpleText":\s*"([^"]+)"',
                        r'"subscriberCount":\s*"([^"]+)"',
                        r'subscriber-count"[^>]*>([^<]+)<',
                        r'"text":"([\d.]+[KMk]?\s*subscribers?)"'
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, response.text)
                        if match:
                            count = self.extract_subscriber_count(match.group(1))
                            if count and count > 0:
                                logger.info(f"Found {count:,} subscribers for {channel_id} on YouTube")
                                return {'subscribers': count, 'source': 'youtube'}
                                
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                logger.debug(f"Error scraping YouTube for {channel_id}: {e}")
                continue
                
        return None
    
    def scrape_vidiq(self, channel_id: str) -> Optional[Dict]:
        """Scrape from VidIQ (alternative source)."""
        try:
            url = f'https://vidiq.com/youtube-stats/channel/{channel_id}/'
            logger.info(f"Trying VidIQ: {url}")
            
            response = self.session.get(url, headers=self.get_headers(), timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for subscriber count
                sub_element = soup.find('div', class_='channel-stats-item', string=re.compile('Subscribers'))
                if sub_element:
                    count_element = sub_element.find_next('div', class_='channel-stats-value')
                    if count_element:
                        count = self.extract_subscriber_count(count_element.get_text())
                        if count and count > 0:
                            logger.info(f"Found {count:,} subscribers for {channel_id} on VidIQ")
                            return {'subscribers': count, 'source': 'vidiq'}
                            
            time.sleep(random.uniform(1, 3))
            
        except Exception as e:
            logger.debug(f"Error scraping VidIQ for {channel_id}: {e}")
            
        return None
    
    def get_channel_metrics(self, channel_id: str) -> Dict:
        """Get channel metrics using multiple scraping sources."""
        # Check cache first
        if channel_id in self.metrics_cache:
            return self.metrics_cache[channel_id]
            
        # Skip if previously failed
        if channel_id in self.failed_channels:
            return {'subscribers': 0, 'source': 'failed'}
            
        # Try different sources in order of reliability
        sources = [
            ('Social Blade', self.scrape_socialblade),
            ('YouTube Direct', self.scrape_youtube_direct),
            ('VidIQ', self.scrape_vidiq)
        ]
        
        for source_name, scrape_func in sources:
            try:
                result = scrape_func(channel_id)
                if result and result.get('subscribers', 0) > 0:
                    self.metrics_cache[channel_id] = result
                    return result
            except Exception as e:
                logger.error(f"Error with {source_name} for {channel_id}: {e}")
                continue
                
        # If all sources fail, mark as failed
        self.failed_channels.add(channel_id)
        logger.warning(f"Could not get metrics for {channel_id} from any source")
        
        return {'subscribers': 0, 'source': 'none'}
    
    def extract_channel_ids(self, content: str) -> List[Tuple[str, str]]:
        """Extract YouTube channel IDs and their context from markdown content."""
        # Pattern to match YouTube URLs and capture surrounding context
        pattern = r'(https?://(?:www\.)?youtube\.com/[@/]([A-Za-z0-9_-]+))'
        
        channel_data = []
        for match in re.finditer(pattern, content):
            url = match.group(1)
            channel_id = match.group(2)
            
            # Get context around the URL (for finding where to update)
            start = max(0, match.start() - 200)
            end = min(len(content), match.end() + 200)
            context = content[start:end]
            
            channel_data.append((channel_id, context))
            
        # Remove duplicates while preserving order
        seen = set()
        unique_channels = []
        for channel_id, context in channel_data:
            if channel_id not in seen:
                seen.add(channel_id)
                unique_channels.append((channel_id, context))
                
        return unique_channels
    
    def format_subscriber_count(self, count: int) -> str:
        """Format subscriber count for display."""
        if count >= 1000000:
            return f"{count / 1000000:.1f}M".rstrip('0').rstrip('.')
        elif count >= 1000:
            return f"{count / 1000:.1f}K".rstrip('0').rstrip('.')
        else:
            return str(count)
    
    def update_markdown_file(self, file_path: Path) -> bool:
        """Update subscriber counts in a markdown file."""
        logger.info(f"Processing {file_path}")
        
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # Extract channel IDs with context
            channels = self.extract_channel_ids(content)
            if not channels:
                logger.info(f"No channels found in {file_path}")
                return False
                
            logger.info(f"Found {len(channels)} unique channels in {file_path}")
            
            # Update each channel
            updates_made = 0
            for channel_id, _ in channels:
                metrics = self.get_channel_metrics(channel_id)
                
                if metrics['subscribers'] > 0:
                    formatted_count = self.format_subscriber_count(metrics['subscribers'])
                    new_badge = f'![YouTube Channel Subscribers](https://img.shields.io/badge/subscribers-{formatted_count}-red)'
                    
                    # Pattern to find and replace existing badges near this channel
                    patterns = [
                        # Existing badge pattern
                        (rf'(youtube\.com/[@/]{re.escape(channel_id)}.*?\n?)!\[YouTube Channel Subscribers\]\(https://img\.shields\.io/badge/subscribers-[^)]+\)', rf'\1{new_badge}'),
                        # Shield.io YouTube badge
                        (rf'(youtube\.com/[@/]{re.escape(channel_id)}.*?\n?)!\[[^\]]*\]\(https://img\.shields\.io/youtube/channel/subscribers/[^)]+\)', rf'\1{new_badge}'),
                        # Generic subscriber badge
                        (rf'(youtube\.com/[@/]{re.escape(channel_id)}.*?\n?)!\[[^\]]*subscribers[^\]]*\]\([^)]+\)', rf'\1{new_badge}'),
                    ]
                    
                    replaced = False
                    for pattern, replacement in patterns:
                        if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE | re.DOTALL)
                            logger.info(f"Updated {channel_id}: {formatted_count} subscribers (source: {metrics.get('source', 'unknown')})")
                            updates_made += 1
                            replaced = True
                            break
                    
                    # If no badge exists, try to add one after the channel URL
                    if not replaced:
                        channel_pattern = rf'(https://(?:www\.)?youtube\.com/[@/]{re.escape(channel_id)})'
                        if re.search(channel_pattern, content):
                            # Add badge on a new line after the URL
                            replacement = rf'\1\n{new_badge}'
                            content = re.sub(channel_pattern, replacement, content, count=1)
                            logger.info(f"Added badge for {channel_id}: {formatted_count} subscribers")
                            updates_made += 1
            
            # Write back if changed
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                logger.info(f"Updated {file_path} - {updates_made} channels modified")
                return True
            else:
                logger.info(f"No changes needed for {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating {file_path}: {e}")
            return False
    
    def update_all_files(self):
        """Update all markdown files with channel metrics."""
        root_dir = Path(__file__).parent.parent.parent
        files_updated = 0
        total_channels_updated = 0
        
        # Update category files
        categories_dir = root_dir / 'categories'
        for md_file in categories_dir.glob('*.md'):
            if md_file.name != 'template.md':
                if self.update_markdown_file(md_file):
                    files_updated += 1
        
        # Update root files
        for file_name in ['Spanish-Channels.md', 'English-Channels.md']:
            file_path = root_dir / file_name
            if file_path.exists():
                if self.update_markdown_file(file_path):
                    files_updated += 1
        
        # Summary
        logger.info(f"\n{'='*50}")
        logger.info(f"SUMMARY:")
        logger.info(f"Files updated: {files_updated}")
        logger.info(f"Channels processed: {len(self.metrics_cache)}")
        logger.info(f"Successful scrapes: {len([m for m in self.metrics_cache.values() if m.get('subscribers', 0) > 0])}")
        logger.info(f"Failed channels: {len(self.failed_channels)}")
        
        if self.failed_channels:
            logger.info(f"\nFailed channels: {', '.join(sorted(self.failed_channels))}")


def main():
    """Main function to update YouTube metrics via scraping."""
    logger.info("Starting YouTube metrics update (web scraping mode)")
    logger.info("No API keys required - using public web data")
    
    scraper = YouTubeMetricsScraper()
    scraper.update_all_files()
    
    logger.info("\nUpdate complete!")


if __name__ == '__main__':
    main() 