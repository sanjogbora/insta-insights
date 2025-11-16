# Playwright Instagram Downloader - Usage Guide

## Overview

This application uses **Playwright browser automation** to download Instagram reels. This is the **easiest and most reliable method** - **ZERO authentication required!**

## How It Works

### Browser Automation (Zero Auth!)

The downloader launches a headless browser (invisible Chrome) that visits Instagram just like you would in a normal browser:

1. Opens Instagram reel URL
2. Waits for video to load
3. Captures the video URL from network requests
4. Downloads the video directly

**No login needed! No cookies! No authentication!**

## Installation

### Step 1: Install Python Packages

```bash
pip install -r requirements.txt
```

This installs Playwright and all other dependencies.

### Step 2: Install Browser (One-Time Setup)

After installing Python packages, run:

```bash
python install_browser.py
```

Or manually:

```bash
playwright install chromium
```

This downloads Chromium (~300MB) - you only need to do this **once**.

### Step 3: You're Done!

That's it! No login, no cookies, no authentication setup required.

## Usage

### Running the Application

```bash
python main.py
```

The app will:
- Launch a headless browser for each download
- Visit the Instagram reel page
- Download the video automatically
- No authentication needed at any step!

### What You'll See

When downloading, you'll see messages like:

```
Downloading reel: DNgJb4Hs5FZ
Launching browser automation... (attempt 1/3)
Loading Instagram page...
Found video URL, downloading...
✓ Successfully downloaded: DNgJb4Hs5FZ
```

## Advantages Over Other Methods

| Feature | Playwright (Current) | yt-dlp | instaloader |
|---------|---------------------|---------|-------------|
| Authentication | **None needed** | Browser cookies required | Login + 2FA required |
| Setup complexity | **Low (install browser once)** | Medium (manage cookies) | High (sessions, 2FA) |
| Reliability | **Very High** | Medium (cookie issues) | Medium (blocked as bot) |
| Works like | **Real browser** | Command-line tool | API scraper |
| Instagram sees it as | **Normal visitor** | Tool/bot | Bot |
| Cookie management | **None** | Required | Required |
| Session management | **None** | None | Required |
| 2FA handling | **Not needed** | Not needed | Required |
| Public reels | **✓ Works perfectly** | ✓ (with cookies) | ✓ (with login) |
| Private reels | ✗ (needs auth) | ✗ (needs cookies) | ✓ (with login) |
| Rate limiting | Low (acts human) | Medium | High |
| Browser needed | Chromium (auto-installed) | Optional | No |

## Why Playwright is Better

### 1. Zero Authentication
- **No login required**
- **No browser cookies to manage**
- **No session files**
- **No 2FA codes**
- Just install and run!

### 2. Acts Like a Real Browser
- Instagram sees it as a normal visitor
- Less likely to be blocked or rate-limited
- Handles JavaScript-heavy pages perfectly
- Works exactly like you visiting Instagram

### 3. More Reliable
- No cookie database locking issues
- No browser compatibility problems
- No "403 Forbidden" errors
- Consistent behavior across all platforms

### 4. Simple Setup
```bash
# That's all you need!
pip install -r requirements.txt
python install_browser.py
python main.py
```

## Troubleshooting

### Problem: "Playwright browsers not installed"

**Error:**
```
✗ Playwright browsers (not installed)
```

**Solution:**
```bash
python install_browser.py
```

Or manually:
```bash
playwright install chromium
```

### Problem: "Timeout while loading Instagram page"

**Cause:** Slow internet or Instagram is slow

**Solution:**
1. Check your internet connection
2. Try again - the app will retry 3 times automatically
3. Increase timeout if needed (edit `downloader.py`, line 199)

### Problem: "Could not capture video URL from network requests"

**Cause:** Instagram changed their page structure

**Solution:**
1. This is rare but can happen
2. The app will retry 3 times
3. If it keeps failing, the reel might be private or deleted

### Problem: "This reel is private"

**Cause:** The reel requires authentication to view

**Solution:**
- Playwright (current version) only works for **public** reels
- For private content, you'd need to implement login (not included)
- Most Instagram reels are public, so this rarely happens

### Problem: Download is slow

**Cause:** Playwright launches a full browser for each download

**Performance:**
- ~5-10 seconds per reel (including browser launch)
- Slower than yt-dlp but more reliable
- For bulk downloads, the delay between downloads helps avoid rate limiting

**This is normal and expected!** The trade-off for zero authentication.

## Performance Tips

1. **Be patient**: Browser automation is slower but more reliable
   - Each download takes ~5-10 seconds
   - For 100 reels: ~10-15 minutes
   - For 1000 reels: ~2-3 hours

2. **Use delay between downloads**: Default is 3 seconds (recommended)
   - Helps avoid rate limiting
   - Makes the app appear more human

3. **Process in batches**: For very large lists (1000+)
   - Download 100-200 at a time
   - Take breaks between batches
   - Reduces chance of Instagram rate limiting

4. **GPU for transcription**: Make sure GPU is detected for fast transcription
   - Run `python diagnose_gpu.py` to check
   - Transcription is much slower than downloading
   - GPU can speed up transcription 10-20x

## Supported URL Formats

The downloader supports these Instagram URL formats:
- `https://www.instagram.com/reel/ABC123/`
- `https://instagram.com/reel/ABC123/`
- `https://www.instagram.com/p/ABC123/` (posts)
- `https://instagram.com/tv/ABC123/` (IGTV)

URLs with tracking parameters also work:
- `https://www.instagram.com/reel/ABC123/?utm_source=ig_web_copy_link`

## Privacy & Security

**Is this safe?**
- Yes! Playwright is an official Microsoft project
- Used by thousands of developers for testing and automation
- All downloads happen locally on your machine
- No data is sent to third parties

**What Instagram sees:**
- A normal browser visit to the reel page
- Just like you opening the URL in Chrome
- No indication it's automated (stealthy browser settings)

**No authentication means:**
- No passwords stored or transmitted
- No session cookies to manage
- No personal information involved
- Works only with publicly accessible content

## FAQ

### Q: Why is it slower than yt-dlp?
**A:** Playwright launches a full browser for each download, which takes ~3-5 seconds. But it's more reliable and needs zero authentication!

### Q: Do I need to be logged into Instagram?
**A:** Nope! That's the whole point - **zero authentication required**.

### Q: Will this work for private reels?
**A:** No, only public reels. Private content requires authentication (which defeats the "zero auth" advantage).

### Q: Can Instagram detect this?
**A:** Instagram sees it as a normal browser visit. It's very hard to detect because it IS a real browser (Chromium).

### Q: How much disk space does Chromium need?
**A:** About 300MB for the browser. Plus whatever space your downloaded videos need.

### Q: Can I use this for thousands of reels?
**A:** Yes! Just be respectful:
  - Use the default 3-second delay between downloads
  - Process in batches of 100-200
  - Don't spam requests

### Q: What if Instagram blocks me?
**A:** Very unlikely with Playwright because it acts like a real browser. If it happens:
  - Wait a few hours
  - Increase delay between downloads
  - Download in smaller batches

### Q: Can I make it faster?
**A:** Not really - the browser launch time is necessary for reliability. But you can:
  - Run multiple instances in parallel (advanced)
  - Focus on faster transcription with GPU

## Comparison with Chrome Extensions

This application works exactly like Instagram downloader Chrome extensions:

| Feature | This App | Chrome Extensions |
|---------|----------|-------------------|
| Uses browser automation | ✓ | ✓ |
| No authentication | ✓ | ✓ |
| Bulk download | ✓ | ✗ (most don't) |
| Transcription | ✓ | ✗ |
| Excel integration | ✓ | ✗ |
| Open source | ✓ | ✗ (most aren't) |
| Command line | ✓ | ✗ |
| Headless (no UI) | ✓ | ✗ |

## Technical Details

For developers interested in how it works:

1. **Launches Chromium** with stealth settings
2. **Creates browser context** with realistic user agent and headers
3. **Navigates to reel URL** and waits for network idle
4. **Intercepts network requests** looking for video files
5. **Captures video URL** from Instagram CDN (cdninstagram.com or fbcdn.net)
6. **Downloads video** using requests library with proper headers
7. **Closes browser** and returns the video file path

All of this happens automatically in the background!

## Need Help?

1. Check this guide first
2. Run `python verify_installation.py` to check setup
3. Check the main README.md for general info
4. Check console output for detailed error messages

---

**Bottom line:** Install once, run forever. Zero authentication. Works like magic!
