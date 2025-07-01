#!/usr/bin/env python3
"""
Generate channels data for the web interface by parsing markdown files.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ChannelExtractor:
    """Extract channel information from markdown files."""
    
    def __init__(self):
        self.channels = []
        self.categories = {
            'platform-engineering': 'Platform Engineering',
            'devsecops': 'DevSecOps & Security',
            'containers': 'Containers & Orchestration',
            'cloud': 'Cloud & Infrastructure',
            'automation': 'Automation & IaC',
            'homelab': 'HomeLab & Self-Hosting'
        }
    
    def extract_channel_info(self, content: str, category: str, language: str) -> List[Dict]:
        """Extract channel information from markdown content."""
        channels = []
        
        # Split content into channel sections
        # Look for patterns like ### Channel Name or ** Channel Name
        channel_sections = re.split(r'(?=^###\s+|\*\*Canal\*\*:|\*\*Channel\*\*:)', content, flags=re.MULTILINE)
        
        for section in channel_sections:
            if not section.strip():
                continue
                
            channel_data = self.parse_channel_section(section, category, language)
            if channel_data:
                channels.append(channel_data)
        
        return channels
    
    def parse_channel_section(self, section: str, category: str, language: str) -> Optional[Dict]:
        """Parse a single channel section."""
        # Extract channel name - improved regex
        name_match = re.search(r'###\s+(.+?)(?:\n|$)', section)
        if not name_match:
            return None
        
        name = name_match.group(1).strip()
        if not name:
            return None
        
        # Extract YouTube URL
        youtube_match = re.search(r'https://(?:www\.)?youtube\.com/[@/]([A-Za-z0-9_-]+)', section)
        if not youtube_match:
            return None
        
        youtube_url = youtube_match.group(0)
        channel_id = youtube_match.group(1)
        
        # Extract LinkedIn URL - improved
        linkedin_match = re.search(r'https://(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+', section)
        linkedin_url = linkedin_match.group(0) if linkedin_match else None
        
        # Extract author name from LinkedIn line
        author_match = re.search(r'\*\*LinkedIn\*\*:\s*\[([^\]]+)\]', section)
        if not author_match:
            # Fallback: look for any bold text that might be an author
            author_match = re.search(r'\*\*Canal\*\*:.*?\n\*\*LinkedIn\*\*:.*?\n\*\*([^*]+)\*\*', section, re.DOTALL)
        
        author = author_match.group(1) if author_match else name
        
        # Extract role - improved
        role_match = re.search(r'\*\*(?:Rol|Role)\*\*:\s*(.+?)(?:\n|$)', section)
        role = role_match.group(1).strip() if role_match else ''
        
        # Extract tags - improved
        tags_match = re.search(r'\*\*(?:Etiquetas|Tags)\*\*:\s*(.+?)(?:\n|$)', section)
        tags = []
        if tags_match:
            tags_text = tags_match.group(1)
            tags = [tag.strip('#').strip('`').strip() for tag in re.findall(r'`#?([^`]+)`', tags_text)]
        
        # Extract description from featured content - improved
        description_lines = []
        content_section = re.search(r'####\s*🎯\s*(?:Contenido Destacado|Featured Content)\s*\n((?:[-•]\s*.+(?:\n|$))+)', section, re.MULTILINE)
        if content_section:
            content_items = re.findall(r'[-•]\s*(.+)', content_section.group(1))
            description_lines = [item.strip() for item in content_items[:3]]  # Take first 3 items
        
        description = ' | '.join(description_lines) if description_lines else f"Canal DevOps enfocado en {', '.join(tags[:3])}" if tags else "Canal de contenido DevOps"
        
        # Extract subscriber count from badge if present
        subscribers_match = re.search(r'subscribers/([A-Za-z0-9_-]+)\?', section)
        subscribers = None
        if subscribers_match:
            # This is the channel ID from the badge, we'll use it for consistency
            pass
        
        return {
            'name': name,
            'author': author,
            'role': role,
            'youtube': youtube_url,
            'channelId': channel_id,
            'linkedin': linkedin_url,
            'category': category,
            'language': language,
            'tags': tags,
            'description': description,
            'subscribers': subscribers
        }
    
    def process_category_file(self, file_path: Path) -> List[Dict]:
        """Process a single category file."""
        logger.info(f"Processing {file_path.name}")
        
        category = file_path.stem  # Get filename without extension
        if category == 'template':
            return []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            channels = []
            
            # Split by language sections
            spanish_section = re.search(r'##\s*📺\s*Spanish Channels.*?(?=##\s*📺\s*English Channels|$)', content, re.DOTALL)
            english_section = re.search(r'##\s*📺\s*English Channels.*?(?=$)', content, re.DOTALL)
            
            if spanish_section:
                spanish_channels = self.extract_channel_info(spanish_section.group(0), category, 'es')
                channels.extend(spanish_channels)
            
            if english_section:
                english_channels = self.extract_channel_info(english_section.group(0), category, 'en')
                channels.extend(english_channels)
            
            # If no language sections found, try to detect language from content
            if not spanish_section and not english_section:
                # Simple heuristic: if "Canal" appears more than "Channel", it's Spanish
                if content.count('Canal') > content.count('Channel'):
                    channels = self.extract_channel_info(content, category, 'es')
                else:
                    channels = self.extract_channel_info(content, category, 'en')
            
            logger.info(f"Found {len(channels)} channels in {file_path.name}")
            return channels
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return []
    
    def process_language_files(self) -> List[Dict]:
        """Process Spanish-Channels.md and English-Channels.md files."""
        channels = []
        root_dir = Path(__file__).parent.parent.parent
        
        # Process Spanish channels
        spanish_file = root_dir / 'Spanish-Channels.md'
        if spanish_file.exists():
            logger.info("Processing Spanish-Channels.md")
            try:
                content = spanish_file.read_text(encoding='utf-8')
                # Extract channels and try to determine their category
                spanish_channels = self.extract_channel_info(content, 'general', 'es')
                
                # Try to categorize based on tags
                for channel in spanish_channels:
                    channel['category'] = self.infer_category(channel['tags'])
                
                channels.extend(spanish_channels)
            except Exception as e:
                logger.error(f"Error processing Spanish-Channels.md: {e}")
        
        # Process English channels
        english_file = root_dir / 'English-Channels.md'
        if english_file.exists():
            logger.info("Processing English-Channels.md")
            try:
                content = english_file.read_text(encoding='utf-8')
                english_channels = self.extract_channel_info(content, 'general', 'en')
                
                # Try to categorize based on tags
                for channel in english_channels:
                    channel['category'] = self.infer_category(channel['tags'])
                
                channels.extend(english_channels)
            except Exception as e:
                logger.error(f"Error processing English-Channels.md: {e}")
        
        return channels
    
    def infer_category(self, tags: List[str]) -> str:
        """Infer category from tags."""
        tag_lower = [tag.lower() for tag in tags]
        
        if any(tag in tag_lower for tag in ['docker', 'kubernetes', 'k8s', 'containers']):
            return 'containers'
        elif any(tag in tag_lower for tag in ['devsecops', 'security', 'seguridad', 'hacking']):
            return 'devsecops'
        elif any(tag in tag_lower for tag in ['aws', 'azure', 'gcp', 'cloud']):
            return 'cloud'
        elif any(tag in tag_lower for tag in ['terraform', 'ansible', 'automation', 'cicd']):
            return 'automation'
        elif any(tag in tag_lower for tag in ['homelab', 'self-hosting', 'proxmox']):
            return 'homelab'
        elif any(tag in tag_lower for tag in ['devops', 'platform-engineering']):
            return 'platform-engineering'
        else:
            return 'platform-engineering'  # Default category
    
    def generate_data(self):
        """Generate channel data from all markdown files."""
        root_dir = Path(__file__).parent.parent.parent
        categories_dir = root_dir / 'categories'
        
        # Process category files
        for md_file in categories_dir.glob('*.md'):
            channels = self.process_category_file(md_file)
            self.channels.extend(channels)
        
        # Process language-specific files
        language_channels = self.process_language_files()
        
        # Merge channels, avoiding duplicates
        existing_ids = {ch['channelId'] for ch in self.channels}
        for channel in language_channels:
            if channel['channelId'] not in existing_ids:
                self.channels.append(channel)
        
        logger.info(f"Total channels extracted: {len(self.channels)}")
        
        # Sort channels by name
        self.channels.sort(key=lambda x: x['name'].lower())
        
        return self.channels
    
    def save_as_javascript(self, output_path: Path):
        """Save channels data as JavaScript file."""
        js_content = f"""// Auto-generated channels data
// Generated on: {__import__('datetime').datetime.now().isoformat()}

const channelsData = {json.dumps(self.channels, indent=2, ensure_ascii=False)};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = channelsData;
}}
"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(js_content, encoding='utf-8')
        logger.info(f"Saved JavaScript data to {output_path}")
    
    def save_as_json(self, output_path: Path):
        """Save channels data as JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.channels, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved JSON data to {output_path}")


def main():
    """Main function to generate channels data."""
    extractor = ChannelExtractor()
    channels = extractor.generate_data()
    
    # Save data in multiple formats
    root_dir = Path(__file__).parent.parent.parent
    
    # JavaScript format for web interface
    js_output = root_dir / 'js' / 'channels-data.js'
    extractor.save_as_javascript(js_output)
    
    # JSON format as backup
    json_output = root_dir / 'data' / 'channels.json'
    extractor.save_as_json(json_output)
    
    # Print summary
    print(f"\n📊 Summary:")
    print(f"Total channels: {len(channels)}")
    print(f"Spanish channels: {len([c for c in channels if c['language'] == 'es'])}")
    print(f"English channels: {len([c for c in channels if c['language'] == 'en'])}")
    print(f"\nChannels by category:")
    for category in extractor.categories:
        count = len([c for c in channels if c['category'] == category])
        print(f"  {extractor.categories[category]}: {count}")


if __name__ == '__main__':
    main() 