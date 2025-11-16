# yt-dlp Instagram Downloader - Usage Guide

## Overview

This application now uses **yt-dlp** instead of instaloader for downloading Instagram reels. This approach is much simpler and mimics how Chrome extensions work - **no manual login required!**

## How It Works

### Browser Cookie Method (Recommended)

The downloader automatically extracts cookies from your browser (Chrome, Firefox, Edge, or Safari) to authenticate with Instagram. This works exactly like Instagram downloader Chrome extensions!

**Requirements:**
1. You must be **logged into Instagram** in your browser
2. Keep your browser installed (Chrome, Firefox, Edge, or Safari)
3. That's it! No manual authentication needed

### Supported Browsers

The application tries browsers in this order:
1. Chrome
2. Firefox
3. Edge
4. Safari

It will automatically use the first browser where it finds Instagram cookies.

## Setup Instructions

### Step 1: Login to Instagram in Your Browser

1. Open your preferred browser (Chrome, Firefox, Edge, or Safari)
2. Go to https://instagram.com
3. Login to your Instagram account
4. **Keep the browser session active** (don't logout)

### Step 2: Run the Application

```bash
python main.py
```

The application will:
- Automatically detect your browser
- Extract Instagram cookies from the browser
- Use those cookies to download reels (just like browser extensions!)

### Step 3: Download Reels

1. Prepare your Excel file with Instagram URLs in column A
2. Load the Excel file in the app
3. Click "Download Reels"
4. The app will show which browser's cookies it's using

## How to Verify It's Working

When you start downloading, you should see messages like:
```
Using Chrome cookies
Downloading reel: DNgJb4Hs5FZ
Successfully downloaded: DNgJb4Hs5FZ
```

If you see:
```
No browser cookies found - may encounter 403 errors
```

This means:
- You're not logged into Instagram in any supported browser, OR
- The browser's cookie database is locked/inaccessible

**Solution:** Make sure you're logged into Instagram in Chrome, Firefox, Edge, or Safari.

## Advantages Over Previous Method

| Feature | yt-dlp (Current) | instaloader (Old) |
|---------|------------------|-------------------|
| Authentication | Browser cookies (automatic) | Manual login + 2FA |
| Session management | None needed | Complex session files |
| 2FA handling | Not needed | Required separate script |
| Rate limiting | Better handling | Frequent blocks |
| Reliability | High (mimics browsers) | Medium (flagged as bot) |
| Setup complexity | Low (just login in browser) | High (scripts, sessions) |

## Troubleshooting

### Problem: "No browser cookies found"

**Cause:** Not logged into Instagram in any supported browser

**Solution:**
1. Open Chrome/Firefox/Edge/Safari
2. Go to instagram.com
3. Login to your account
4. Try downloading again

### Problem: "HTTP Error 403: Forbidden"

**Cause:** Instagram is blocking the request (rate limiting or no valid cookies)

**Solutions:**
1. Make sure you're logged into Instagram in your browser
2. Wait a few minutes and try again (rate limiting)
3. Try logging out and back into Instagram in your browser
4. Clear your browser cookies and login fresh

### Problem: Slow downloads

**Cause:** Rate limiting or network issues

**Solution:**
1. Increase delay between downloads in settings (default: 3 seconds)
2. Download in smaller batches
3. Try at different times of day

### Problem: "could not find chrome cookies database"

**Cause:** Running in environment without a browser (Docker, server, etc.)

**Solution:**
1. Run the application on your local machine where you have a browser installed
2. Or manually provide cookies using a cookies.txt file (advanced - see yt-dlp documentation)

## Advanced: Manual Cookie File (Optional)

If browser cookie extraction doesn't work, you can manually export cookies:

1. Install a browser extension like "Get cookies.txt" for Chrome
2. Visit instagram.com while logged in
3. Export cookies to a file named `instagram_cookies.txt`
4. Place it in the project root directory
5. Modify `modules/downloader.py` to use: `'cookiefile': 'instagram_cookies.txt'`

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
- Yes! The app only reads cookies locally from your browser
- Cookies are not stored or transmitted anywhere
- This is exactly how browser extensions work

**Browser access:**
- The app reads cookies from your browser's local database
- No data is sent to external servers
- All downloads happen directly from Instagram to your computer

## Performance Tips

1. **GPU Acceleration:** The app auto-detects your GPU for faster transcription
   - NVIDIA GPU: ~10-20 seconds per video
   - CPU only: ~1-2 minutes per video

2. **Batch Size:** Download 10-50 reels at a time for optimal performance

3. **Delay Between Downloads:** Keep at 3-5 seconds to avoid rate limiting

4. **Network:** Use a stable internet connection for best results

## Comparison with Chrome Extensions

This application works exactly like popular Instagram downloader Chrome extensions:

| Feature | This App | Chrome Extensions |
|---------|----------|-------------------|
| Uses browser cookies | ✓ | ✓ |
| No manual login | ✓ | ✓ |
| Bulk download | ✓ | ✗ (most don't) |
| Transcription | ✓ | ✗ |
| Excel integration | ✓ | ✗ |
| Open source | ✓ | ✗ (most aren't) |

## Need Help?

1. Check the main README.md for general setup
2. Run `python diagnose_gpu.py` to check GPU setup
3. Check the console output for detailed error messages
4. Make sure you're logged into Instagram in your browser

## Alternative: Public Reels Without Login

For **public** reels, yt-dlp can sometimes work without cookies, but it's less reliable and more likely to hit 403 errors. The browser cookie method is strongly recommended.

---

**Bottom line:** Just stay logged into Instagram in your browser, and the app will handle everything automatically - no complex authentication needed!
