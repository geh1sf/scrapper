# 🏠 Sofia Property Scraper

Automated apartment hunting in Sofia, Bulgaria using GitHub Actions and Pages.

## 🌐 Live Results

**View live property results:** [Your GitHub Pages URL will be here]

## ✨ Features

- 🔄 **Automated Daily Scraping** - Runs every day at 8:00 AM UTC
- 🏠 **Sofia Apartments** - Searches alo.bg for apartments
- 🎯 **Smart Filtering** - Customizable criteria (price, area, type)
- 📱 **Mobile Friendly** - Responsive web interface
- 📊 **History Tracking** - See trends over time
- 🚫 **Duplicate Detection** - Only shows new properties
- 🆓 **Completely Free** - Powered by GitHub Actions

## 🚀 How It Works

1. **GitHub Actions** runs the scraper daily
2. **Scrapes alo.bg** for Sofia apartments
3. **Filters results** based on your criteria
4. **Generates website** with new properties
5. **Deploys to GitHub Pages** automatically
6. **Tracks history** and prevents duplicates

## ⚙️ Configuration

Edit `config/filters.yaml` to customize your search:

```yaml
location:
  city: "София"  # Sofia

property_type:
  - "Двустаен"    # 2-room apartment
  - "Тристаен"    # 3-room apartment

price_range:
  min: 100000  # BGN
  max: 300000  # BGN

features:
  min_area: 60     # square meters
  max_area: 120    # square meters
  min_floor: 1
  max_floor: 10
```

## 🛠️ Setup

1. **Fork this repository**
2. **Enable GitHub Actions** in repository settings
3. **Enable GitHub Pages** (Settings → Pages → Source: GitHub Actions)
4. **Customize filters** in `config/filters.yaml`
5. **Trigger first run** (Actions → Property Scraper → Run workflow)

Your website will be available at: `https://yourusername.github.io/property-scraper`

## 📅 Schedule

- **Daily**: 8:00 AM UTC (adjust in `.github/workflows/scrape-properties.yml`)
- **Manual**: Can trigger anytime from GitHub Actions tab

## 🔧 Manual Testing

```bash
# Test locally
python github_scraper.py
python generate_website.py

# Open generated website
open docs/index.html
```

## 📊 What You'll See

- **New properties** found since last run
- **Property details**: price, location, area, floor
- **Direct links** to alo.bg listings
- **Statistics** and history charts
- **Mobile-friendly** interface

## 🤖 Automation

Everything runs automatically:
- ✅ **No server needed** - GitHub Actions provides compute
- ✅ **No database needed** - JSON files track state
- ✅ **No email needed** - Web interface for results
- ✅ **No maintenance** - Runs indefinitely for free

## 🆓 GitHub Actions Free Tier

- ✅ **2,000 minutes/month** (plenty for daily 5-minute runs)
- ✅ **500MB storage** (more than enough for property data)
- ✅ **Unlimited public repositories**

Perfect for this use case!

## 🔍 Troubleshooting

**No properties showing?**
- Check `config/filters.yaml` - criteria might be too strict
- View GitHub Actions logs for errors

**Website not updating?**
- Check Actions tab for failed runs
- GitHub Pages takes 5-10 minutes to update

**Want different schedule?**
- Edit `.github/workflows/scrape-properties.yml`
- Use [crontab.guru](https://crontab.guru) for schedule syntax

---

🏠 **Happy apartment hunting!** 🇧🇬