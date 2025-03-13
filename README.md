# 🚀 DevOps YouTube Channels

A curated collection of YouTube channels focused on DevOps, Platform Engineering, Cloud Computing, and related technologies. This repository organizes channels by category and language, making it easy to find the content you're looking for.

## 📋 Categories

- [Platform Engineering](categories/platform-engineering.md) - Platform architecture and best practices
- [DevSecOps & Security](categories/devsecops.md) - Security practices and vulnerability analysis
- [Containers & Orchestration](categories/containers.md) - Docker, Kubernetes, and container technologies
- [Cloud Infrastructure](categories/cloud.md) - AWS, Azure, GCP, and cloud services
- [HomeLab & Self-Hosting](categories/homelab.md) - Home servers, virtualization, and self-hosted solutions
- [Automation & IaC](categories/automation.md) - Infrastructure as Code and process automation

## 🌐 Language Collections

- [Spanish Channels](Spanish-Channels.md) - Canales en Español
- [English Channels](English-Channels.md) - English-speaking channels

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/new-channel`)
3. Add your changes following our format
4. Commit your changes (`git commit -m 'Add new channel'`)
5. Push to the branch (`git push origin feature/new-channel`)
6. Open a Pull Request

### 📝 Channel Format

```markdown
### Channel Name
![YouTube Channel Subscribers](https://img.shields.io/youtube/channel/subscribers/CHANNEL_ID?style=social)

**Channel**: https://www.youtube.com/@ChannelName
**LinkedIn**: [Author Name](https://www.linkedin.com/in/author-profile/)
**Role**: Professional Role
**Tags**: `#tag1` `#tag2` `#tag3` `#tag4`

#### 🎯 Featured Content
- Topic 1
- Topic 2
- Topic 3
- Topic 4
```

## 🔄 Automatic Updates

This repository uses GitHub Actions to maintain data quality and freshness:

### 📊 Subscriber Count Updates
- Updates YouTube subscriber counts daily
- Uses YouTube Data API for accurate statistics
- Automatically commits changes to the repository

### 🔍 Link Validation
- Validates all YouTube and LinkedIn links daily
- Checks for broken or invalid links
- Creates issues for any problems found
- Runs on all Pull Requests to prevent invalid links

### Setting up Local Development

1. Get API Keys:
   - YouTube Data API key from [Google Cloud Console](https://console.cloud.google.com/)
   - LinkedIn API token (optional, for link validation)

2. Create a `.env` file in the root directory:
   ```env
   YOUTUBE_API_KEY=your_api_key_here
   LINKEDIN_TOKEN=your_token_here
   ```

3. Install dependencies:
   ```bash
   pip install google-api-python-client python-dotenv requests
   ```

4. Run the scripts:
   ```bash
   # Update subscriber counts
   python .github/scripts/update_subscribers.py
   
   # Validate links
   python .github/scripts/validate_links.py
   ```

## 🎯 Future Improvements

- [ ] Add channel thumbnails and featured video recommendations
- [ ] Implement a robust tagging system
- [ ] Create a tag-based navigation page
- [ ] Add more international channels
- [ ] Include playlists and course recommendations

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*This repository is maintained with ❤️ by the DevOps community. Last updated: March 2025*
