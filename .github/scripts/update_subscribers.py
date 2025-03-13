import os
import re
from pathlib import Path
from typing import Dict, List, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
CHANNELS = {
    'ChannelName1': 'CHANNEL_ID_1',
    'ChannelName2': 'CHANNEL_ID_2',
    # Add more channels here
}

def get_youtube_client() -> Optional[build]:
    """Create a YouTube API client."""
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: YOUTUBE_API_KEY environment variable not set")
        return None
    
    try:
        return build('youtube', 'v3', developerKey=api_key)
    except Exception as e:
        print(f"Error building YouTube client: {e}")
        return None

def extract_channel_ids(content: str) -> List[str]:
    """Extract YouTube channel IDs from markdown content."""
    # Match both @username and channel ID formats
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

def get_channel_stats(youtube: build, channel_ids: List[str]) -> Dict[str, int]:
    """Get subscriber counts for a list of channel IDs."""
    stats = {}
    
    for channel_id in channel_ids:
        try:
            # First try to get channel by custom URL
            request = youtube.channels().list(
                part="statistics",
                forUsername=channel_id
            )
            response = request.execute()
            
            # If no results, try searching by channel ID
            if not response.get('items'):
                request = youtube.search().list(
                    part="id",
                    q=f"@{channel_id}",
                    type="channel",
                    maxResults=1
                )
                search_response = request.execute()
                
                if search_response.get('items'):
                    channel_id = search_response['items'][0]['id']['channelId']
                    request = youtube.channels().list(
                        part="statistics",
                        id=channel_id
                    )
                    response = request.execute()
            
            if response.get('items'):
                stats[channel_id] = int(response['items'][0]['statistics']['subscriberCount'])
            else:
                print(f"Could not find stats for channel: {channel_id}")
                
        except HttpError as e:
            print(f"Error getting stats for {channel_id}: {e}")
            continue
    
    return stats

def update_markdown_file(file_path: str, stats: Dict[str, int]) -> None:
    """Update subscriber count badges in markdown files."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update subscriber badges
    for channel_id, count in stats.items():
        # Update both @username and channel ID format badges
        patterns = [
            f'youtube\.com/@{channel_id}.*?\n.*?!\[YouTube Channel Subscribers\].*?\)',
            f'youtube\.com/channel/{channel_id}.*?\n.*?!\[YouTube Channel Subscribers\].*?\)',
            f'youtube\.com/c/{channel_id}.*?\n.*?!\[YouTube Channel Subscribers\].*?\)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            if match:
                old_badge = match.group(0)
                new_badge = re.sub(
                    r'!\[YouTube Channel Subscribers\].*?\)',
                    f'![YouTube Channel Subscribers](https://img.shields.io/youtube/channel/subscribers/{channel_id}?style=social)',
                    old_badge
                )
                content = content.replace(old_badge, new_badge)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def get_subscriber_count(channel_id):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    request = youtube.channels().list(part='statistics', id=channel_id)
    response = request.execute()
    return response['items'][0]['statistics']['subscriberCount']

def update_readme():
    with open('README.md', 'r') as file:
        content = file.readlines()

    for i, line in enumerate(content):
        if '![YouTube Channel Subscribers]' in line:
            channel_name = line.split('[')[1].split(']')[0]
            if channel_name in CHANNELS:
                subscriber_count = get_subscriber_count(CHANNELS[channel_name])
                content[i] = f'![YouTube Channel Subscribers](https://img.shields.io/youtube/channel/subscribers/{CHANNELS[channel_name]}?style=social)\n\n'

    with open('README.md', 'w') as file:
        file.writelines(content)

def main():
    """Main function to update YouTube subscriber counts."""
    youtube = get_youtube_client()
    if not youtube:
        return
    
    # Process all markdown files in categories directory
    categories_dir = Path(__file__).parent.parent.parent / 'categories'
    for md_file in categories_dir.glob('*.md'):
        print(f"Processing {md_file}")
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        channel_ids = extract_channel_ids(content)
        if channel_ids:
            stats = get_channel_stats(youtube, channel_ids)
            update_markdown_file(str(md_file), stats)
            print(f"Updated {len(stats)} channels in {md_file}")

if __name__ == '__main__':
    main()
    update_readme()
