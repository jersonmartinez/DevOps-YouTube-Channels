import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LinkValidator:
    def __init__(self):
        self.youtube = self._get_youtube_client()
        self.invalid_links: Dict[str, List[str]] = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def _get_youtube_client(self) -> build:
        """Create a YouTube API client."""
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            logger.error("YOUTUBE_API_KEY not set")
            return None
        
        try:
            return build('youtube', 'v3', developerKey=api_key)
        except Exception as e:
            logger.error(f"Error building YouTube client: {e}")
            return None

    def extract_links(self, content: str) -> Tuple[Set[str], Set[str]]:
        """Extract YouTube and LinkedIn links from content."""
        youtube_patterns = [
            r'youtube\.com/@([A-Za-z0-9_-]+)',
            r'youtube\.com/channel/([A-Za-z0-9_-]+)',
            r'youtube\.com/c/([A-Za-z0-9_-]+)'
        ]
        
        linkedin_pattern = r'linkedin\.com/in/([A-Za-z0-9_-]+)'
        
        youtube_links = set()
        for pattern in youtube_patterns:
            youtube_links.update(re.findall(pattern, content))
        
        linkedin_links = set(re.findall(linkedin_pattern, content))
        
        return youtube_links, linkedin_links

    def validate_youtube_channel(self, channel_id: str) -> bool:
        """Validate if a YouTube channel exists."""
        if not self.youtube:
            return True  # Skip validation if no API client
            
        try:
            # Try username first
            request = self.youtube.channels().list(
                part="id",
                forUsername=channel_id
            )
            response = request.execute()
            
            # If not found, try channel search
            if not response.get('items'):
                request = self.youtube.search().list(
                    part="id",
                    q=f"@{channel_id}",
                    type="channel",
                    maxResults=1
                )
                response = request.execute()
            
            return bool(response.get('items'))
            
        except HttpError as e:
            logger.error(f"Error validating YouTube channel {channel_id}: {e}")
            return False

    def validate_linkedin_profile(self, profile_id: str) -> bool:
        """Validate if a LinkedIn profile exists."""
        url = f"https://www.linkedin.com/in/{profile_id}"
        try:
            response = self.session.head(url, allow_redirects=True)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error validating LinkedIn profile {profile_id}: {e}")
            return False

    def validate_file(self, file_path: Path) -> None:
        """Validate all links in a file."""
        logger.info(f"Validating links in {file_path}")
        
        try:
            content = file_path.read_text(encoding='utf-8')
            youtube_links, linkedin_links = self.extract_links(content)
            
            invalid_links = []
            
            # Validate YouTube channels
            for channel in youtube_links:
                if not self.validate_youtube_channel(channel):
                    invalid_links.append(f"YouTube: {channel}")
            
            # Validate LinkedIn profiles
            for profile in linkedin_links:
                if not self.validate_linkedin_profile(profile):
                    invalid_links.append(f"LinkedIn: {profile}")
            
            if invalid_links:
                self.invalid_links[str(file_path)] = invalid_links
                
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")

    def validate_repository(self, repo_path: Path) -> None:
        """Validate all markdown files in the repository."""
        categories_dir = repo_path / 'categories'
        
        # Validate category files
        for md_file in categories_dir.glob('*.md'):
            self.validate_file(md_file)
        
        # Validate root markdown files
        for md_file in repo_path.glob('*.md'):
            if md_file.name.lower() in ['readme.md', 'spanish-channels.md', 'english-channels.md']:
                self.validate_file(md_file)
        
        # Save results
        if self.invalid_links:
            output_file = repo_path / 'invalid_links.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.invalid_links, f, indent=2)
            raise Exception("Invalid links found. Check invalid_links.json for details.")

def main():
    """Main function to validate links."""
    repo_path = Path(__file__).parent.parent.parent
    validator = LinkValidator()
    validator.validate_repository(repo_path)

if __name__ == '__main__':
    main()
