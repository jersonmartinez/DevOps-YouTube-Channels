#!/usr/bin/env python3
"""
Update YouTube channel metrics using web scraping only.
Enhanced to get more relevant information like latest video date and channel description.
No API keys required - uses multiple sources for reliability.
"""

import os
import re
import time
import random
import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
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
    """Scrape YouTube channel metrics and additional information from various sources."""
    
    def __init__(self):
        self.session = requests.Session()
        self.metrics_cache = {}
        self.failed_channels = set()
        self.enhanced_data = {}  # Store additional channel data
        
    def get_headers(self) -> Dict[str, str]:
        """Get randomized headers for requests."""
        return {
            'User-Agent': ua.random,
            'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
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
    
    def parse_relative_date(self, date_text: str) -> Optional[str]:
        """Parse relative dates like '2 days ago' into ISO format."""
        try:
            date_text = date_text.lower().strip()
            now = datetime.now()
            
            # Patterns for relative dates
            patterns = {
                r'(\d+)\s*second': lambda x: now - timedelta(seconds=int(x)),
                r'(\d+)\s*minute': lambda x: now - timedelta(minutes=int(x)),
                r'(\d+)\s*hour': lambda x: now - timedelta(hours=int(x)),
                r'(\d+)\s*day': lambda x: now - timedelta(days=int(x)),
                r'(\d+)\s*week': lambda x: now - timedelta(weeks=int(x)),
                r'(\d+)\s*month': lambda x: now - timedelta(days=int(x)*30),
                r'(\d+)\s*year': lambda x: now - timedelta(days=int(x)*365),
            }
            
            for pattern, calc_func in patterns.items():
                match = re.search(pattern, date_text)
                if match:
                    date = calc_func(match.group(1))
                    return date.strftime('%Y-%m-%d')
                    
            return None
        except:
            return None
    
    def scrape_socialblade(self, channel_id: str) -> Optional[Dict]:
        """Scrape metrics from Social Blade with enhanced data."""
        urls_to_try = [
            f'https://socialblade.com/youtube/c/{channel_id}',
            f'https://socialblade.com/youtube/channel/{channel_id}',
            f'https://socialblade.com/youtube/user/{channel_id}',
            f'https://socialblade.com/youtube/@{channel_id}'
        ]
        
        for url in urls_to_try:
            try:
                logger.info(f"Trying Social Blade: {url}")
                response = self.session.get(url, headers=self.get_headers(), timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    result = {'source': 'socialblade'}
                    
                    # Try multiple selectors for subscriber count
                    sub_selectors = [
                        '#youtube-stats-header-subs',
                        '#YouTubeUserTopInfoBlock span[style*="font-size: 1.4em"]',
                        'span#youtube-stats-header-subs',
                        'div#YouTubeUserTopInfoBlock span[style*="font-size"]'
                    ]
                    
                    for selector in sub_selectors:
                        element = soup.select_one(selector)
                        if element:
                            count = self.extract_subscriber_count(element.get_text())
                            if count and count > 0:
                                result['subscribers'] = count
                                break
                    
                    # Try to get total views
                    views_element = soup.select_one('#youtube-stats-header-views')
                    if views_element:
                        views_count = self.extract_subscriber_count(views_element.get_text())
                        if views_count:
                            result['total_views'] = views_count
                    
                    # Try to get video count
                    videos_element = soup.select_one('#youtube-stats-header-uploads')
                    if videos_element:
                        videos_count = self.extract_subscriber_count(videos_element.get_text())
                        if videos_count:
                            result['video_count'] = videos_count
                    
                    # Try to get channel creation date
                    creation_element = soup.select_one('#youtube-stats-header-channeltype')
                    if creation_element:
                        creation_text = creation_element.get_text()
                        date_match = re.search(r'(\w+\s+\d+,\s+\d{4})', creation_text)
                        if date_match:
                            result['created_date'] = date_match.group(1)
                    
                    if result.get('subscribers', 0) > 0:
                        logger.info(f"Found data for {channel_id} on Social Blade: {result}")
                        return result
                                
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                logger.debug(f"Error scraping Social Blade for {channel_id}: {e}")
                continue
                
        return None
    
    def scrape_youtube_direct(self, channel_id: str) -> Optional[Dict]:
        """Try to scrape directly from YouTube with enhanced data extraction."""
        urls_to_try = [
            f'https://www.youtube.com/@{channel_id}',
            f'https://www.youtube.com/c/{channel_id}',
            f'https://www.youtube.com/channel/{channel_id}'
        ]
        
        for url in urls_to_try:
            try:
                logger.info(f"Trying YouTube direct: {url}")
                response = self.session.get(url, headers=self.get_headers(), timeout=15)
                
                if response.status_code == 200:
                    result = {'source': 'youtube'}
                    
                    # Look for subscriber count in various patterns
                    sub_patterns = [
                        r'"subscriberCountText":\s*{\s*"simpleText":\s*"([^"]+)"',
                        r'"subscriberCount":\s*"([^"]+)"',
                        r'subscriber-count"[^>]*>([^<]+)<',
                        r'"text":"([\d.]+[KMk]?\s*subscribers?)"',
                        r'"subscriberCountText":\{"accessibility":\{"accessibilityData":\{"label":"([^"]+)"\}\}'
                    ]
                    
                    for pattern in sub_patterns:
                        match = re.search(pattern, response.text)
                        if match:
                            count = self.extract_subscriber_count(match.group(1))
                            if count and count > 0:
                                result['subscribers'] = count
                                break
                    
                    # Try to get channel description
                    desc_patterns = [
                        r'"description":\s*"([^"]+)"',
                        r'"descriptionSnippet":\{"simpleText":"([^"]+)"',
                        r'<meta name="description" content="([^"]+)"'
                    ]
                    
                    for pattern in desc_patterns:
                        match = re.search(pattern, response.text)
                        if match:
                            description = match.group(1)[:200]  # Limit to 200 chars
                            result['description'] = description.replace('\\n', ' ').strip()
                            break
                    
                    # Try to get latest video info
                    video_patterns = [
                        r'"title":\{"runs":\[\{"text":"([^"]+)"\}\],"accessibility"',
                        r'"videoTitle":"([^"]+)"',
                        r'{"videoId":"([^"]+)","thumbnail".*?"title":\{"runs":\[\{"text":"([^"]+)"'
                    ]
                    
                    for pattern in video_patterns:
                        match = re.search(pattern, response.text)
                        if match:
                            if len(match.groups()) > 1:
                                result['latest_video_title'] = match.group(2)[:100]
                                result['latest_video_id'] = match.group(1)
                            else:
                                result['latest_video_title'] = match.group(1)[:100]
                            break
                    
                    # Try to get upload date of latest video
                    date_patterns = [
                        r'"publishedTimeText":\{"simpleText":"([^"]+)"',
                        r'"dateText":\{"simpleText":"([^"]+)"'
                    ]
                    
                    for pattern in date_patterns:
                        match = re.search(pattern, response.text)
                        if match:
                            date_text = match.group(1)
                            parsed_date = self.parse_relative_date(date_text)
                            if parsed_date:
                                result['latest_video_date'] = parsed_date
                            break
                    
                    if result.get('subscribers', 0) > 0:
                        logger.info(f"Found data for {channel_id} on YouTube: {result}")
                        return result
                                
                time.sleep(random.uniform(3, 6))
                
            except Exception as e:
                logger.debug(f"Error scraping YouTube for {channel_id}: {e}")
                continue
                
        return None
    
    def scrape_noxinfluencer(self, channel_id: str) -> Optional[Dict]:
        """Scrape from NoxInfluencer (alternative source with good data)."""
        try:
            url = f'https://www.noxinfluencer.com/youtube/channel/{channel_id}'
            logger.info(f"Trying NoxInfluencer: {url}")
            
            response = self.session.get(url, headers=self.get_headers(), timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                result = {'source': 'noxinfluencer'}
                
                # Look for subscriber count
                sub_element = soup.select_one('.channel-info-item:contains("Subscribers") .info-value')
                if sub_element:
                    count = self.extract_subscriber_count(sub_element.get_text())
                    if count and count > 0:
                        result['subscribers'] = count
                
                # Try to get average views
                views_element = soup.select_one('.channel-info-item:contains("Avg.Views") .info-value')
                if views_element:
                    avg_views = self.extract_subscriber_count(views_element.get_text())
                    if avg_views:
                        result['avg_views'] = avg_views
                
                # Try to get channel rank
                rank_element = soup.select_one('.channel-rank-item .rank-value')
                if rank_element:
                    result['channel_rank'] = rank_element.get_text().strip()
                
                if result.get('subscribers', 0) > 0:
                    logger.info(f"Found data for {channel_id} on NoxInfluencer: {result}")
                    return result
                            
            time.sleep(random.uniform(2, 4))
            
        except Exception as e:
            logger.debug(f"Error scraping NoxInfluencer for {channel_id}: {e}")
            
        return None
    
    def get_channel_metrics(self, channel_id: str) -> Dict:
        """Get comprehensive channel metrics using multiple scraping sources."""
        # Check cache first
        if channel_id in self.metrics_cache:
            return self.metrics_cache[channel_id]
            
        # Skip if previously failed
        if channel_id in self.failed_channels:
            return {'subscribers': 0, 'source': 'failed'}
            
        # Try different sources in order of reliability and data quality
        sources = [
            ('YouTube Direct', self.scrape_youtube_direct),
            ('Social Blade', self.scrape_socialblade),
            ('NoxInfluencer', self.scrape_noxinfluencer)
        ]
        
        combined_result = {
            'subscribers': 0,
            'source': 'none',
            'last_updated': datetime.now().isoformat()
        }
        
        for source_name, scrape_func in sources:
            try:
                result = scrape_func(channel_id)
                if result:
                    # Merge results, preferring non-zero values
                    for key, value in result.items():
                        if value and (key not in combined_result or not combined_result.get(key)):
                            combined_result[key] = value
                    
                    # If we have subscribers, update source
                    if result.get('subscribers', 0) > 0:
                        combined_result['subscribers'] = result['subscribers']
                        if combined_result['source'] == 'none':
                            combined_result['source'] = result.get('source', source_name.lower())
                        
            except Exception as e:
                logger.error(f"Error with {source_name} for {channel_id}: {e}")
                continue
        
        # Store enhanced data separately
        if channel_id not in self.enhanced_data:
            self.enhanced_data[channel_id] = {}
        
        # Extract enhanced data from combined result
        enhanced_fields = ['description', 'latest_video_title', 'latest_video_id', 
                          'latest_video_date', 'total_views', 'video_count', 
                          'avg_views', 'channel_rank', 'created_date']
        
        for field in enhanced_fields:
            if field in combined_result:
                self.enhanced_data[channel_id][field] = combined_result[field]
        
        # Cache the result
        if combined_result['subscribers'] > 0:
            self.metrics_cache[channel_id] = combined_result
            logger.info(f"Successfully scraped {channel_id}: {combined_result['subscribers']:,} subscribers")
        else:
            self.failed_channels.add(channel_id)
            logger.warning(f"Could not get metrics for {channel_id} from any source")
        
        return combined_result
    
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
        """Update subscriber counts and enhanced data in a markdown file."""
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
                    
                    # Create enhanced badge with last update info
                    update_date = datetime.now().strftime('%Y-%m-%d')
                    new_badge = f'![YouTube Channel Subscribers](https://img.shields.io/badge/subscribers-{formatted_count}-red) ![Last Update](https://img.shields.io/badge/updated-{update_date}-blue)'
                    
                    # Pattern to find and replace existing badges near this channel
                    patterns = [
                        # Existing badge pattern
                        (rf'(youtube\.com/[@/]{re.escape(channel_id)}.*?\n?)!\[YouTube Channel Subscribers\]\(https://img\.shields\.io/badge/subscribers-[^)]+\)(\s*!\[Last Update\]\([^)]+\))?', rf'\1{new_badge}'),
                        # Shield.io YouTube badge
                        (rf'(youtube\.com/[@/]{re.escape(channel_id)}.*?\n?)!\[[^\]]*\]\(https://img\.shields\.io/youtube/channel/subscribers/[^)]+\)', rf'\1{new_badge}'),
                        # Generic subscriber badge
                        (rf'(youtube\.com/[@/]{re.escape(channel_id)}.*?\n?)!\[[^\]]*subscribers[^\]]*\]\([^)]+\)', rf'\1{new_badge}'),
                    ]
                    
                    replaced = False
                    for pattern, replacement in patterns:
                        if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE | re.DOTALL)
                            logger.info(f"Updated {channel_id}: {formatted_count} subscribers")
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
                    
                    # Add enhanced data as a comment (won't be visible in rendered markdown)
                    enhanced_data = self.enhanced_data.get(channel_id, {})
                    if enhanced_data and 'latest_video_date' in enhanced_data:
                        comment = f"\n<!-- Enhanced data for {channel_id}: {json.dumps(enhanced_data, ensure_ascii=False)} -->\n"
                        # Add after the channel section
                        channel_section_pattern = rf'(### [^\n]*{re.escape(channel_id)}[^\n]*\n(?:.*?\n)*?)(?=###|\Z)'
                        if re.search(channel_section_pattern, content, re.DOTALL):
                            content = re.sub(channel_section_pattern, rf'\1{comment}', content, flags=re.DOTALL)
            
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
    
    def save_enhanced_data(self):
        """Save enhanced channel data to a JSON file."""
        if self.enhanced_data:
            output_file = Path(__file__).parent.parent.parent / 'data' / 'enhanced_channel_data.json'
            output_file.parent.mkdir(exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.enhanced_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved enhanced data for {len(self.enhanced_data)} channels to {output_file}")
    
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
        
        # Save enhanced data
        self.save_enhanced_data()
        
        # Summary
        logger.info(f"\n{'='*50}")
        logger.info(f"SUMMARY:")
        logger.info(f"Files updated: {files_updated}")
        logger.info(f"Channels processed: {len(self.metrics_cache)}")
        logger.info(f"Successful scrapes: {len([m for m in self.metrics_cache.values() if m.get('subscribers', 0) > 0])}")
        logger.info(f"Failed channels: {len(self.failed_channels)}")
        logger.info(f"Channels with enhanced data: {len(self.enhanced_data)}")
        
        if self.failed_channels:
            logger.info(f"\nFailed channels: {', '.join(sorted(self.failed_channels))}")
        
        # Show sample of enhanced data
        if self.enhanced_data:
            logger.info("\nSample enhanced data:")
            for channel_id, data in list(self.enhanced_data.items())[:3]:
                if 'latest_video_title' in data:
                    logger.info(f"  {channel_id}: Latest video - {data['latest_video_title'][:50]}...")


def main():
    """Main function to update YouTube metrics via scraping."""
    logger.info("Starting YouTube metrics update (enhanced web scraping mode)")
    logger.info("No API keys required - using public web data")
    logger.info("Will collect: subscriber counts, latest videos, descriptions, and more")
    
    scraper = YouTubeMetricsScraper()
    scraper.update_all_files()
    
    logger.info("\nUpdate complete! Check data/enhanced_channel_data.json for additional information.")


if __name__ == '__main__':
    main() 