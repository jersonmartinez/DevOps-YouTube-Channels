# 🚀 DevOps YouTube Channels

A curated collection of YouTube channels focused on DevOps, Platform Engineering, Cloud Computing, and related technologies. This repository organizes channels by category and language.

## 📋 Categories

- [Platform Engineering](categories/platform-engineering.md)
- [DevSecOps & Security](categories/devsecops.md)
- [Containers & Orchestration](categories/containers.md)
- [Cloud Infrastructure](categories/cloud.md)
- [HomeLab & Self-Hosting](categories/homelab.md)
- [Automation & IaC](categories/automation.md)

## 🌐 Language Collections

- [Spanish Channels](Spanish-Channels.md)
- [English Channels](English-Channels.md)

## 📊 YouTube Metrics Update Workflow

This repository includes a GitHub Actions workflow that automatically updates the metrics of the YouTube channels listed. Instead of using the YouTube API, the workflow scrapes data from [Social Blade](https://socialblade.com) to gather metrics such as subscriber count, total views, and channel growth. This approach ensures that we can retrieve data without relying on API quotas or keys.

### How It Works

1. **Scraping Script**: A custom script scrapes channel metrics from Social Blade.
2. **GitHub Actions**: The script is executed periodically via a scheduled GitHub Actions workflow.
3. **Data Integration**: The scraped data is formatted and updated in the repository files (e.g., JSON or Markdown).

### Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/DevOps-YouTube-Channels.git
   cd DevOps-YouTube-Channels
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the scraping script locally:
   ```bash
   python .github/scripts/update_subscribers.py
   ```

4. Verify the updates in the `categories` folder.

### Future Enhancements for Scraping

- [ ] Improve the scraping script to handle changes in Social Blade's HTML structure.
- [ ] Add error handling for unavailable or blocked pages.
- [ ] Cache results to minimize repeated requests to Social Blade.
- [ ] Include additional metrics like estimated earnings or video counts.

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/new-channel`)
3. Add your changes following our format
4. Commit your changes (`git commit -m 'Add new channel'`)
5. Push to the branch (`git push origin feature/new-channel`)
6. Open a Pull Request

## 🎯 Future Improvements

- [ ] Add channel thumbnails and featured video recommendations
- [ ] Implement a robust tagging system
- [ ] Create a tag-based navigation page
- [ ] Add more international channels
- [ ] Include playlists and course recommendations
- [ ] Improve the contribution guidelines for clarity
- [ ] Set up a GitHub Actions workflow to update YouTube metrics

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*This repository is maintained with ❤️ by the DevOps community. Last updated: April 2025*
