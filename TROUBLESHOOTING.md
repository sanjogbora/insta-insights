# Troubleshooting 403 Forbidden Errors

If you're experiencing 403 Forbidden errors when downloading Instagram reels, this guide will help you resolve them.

## Understanding the Error

The `403 Forbidden` error occurs when Instagram's servers detect and block automated requests. This is Instagram's anti-bot protection system at work.

Error message example:
```
JSON Query to graphql/query: 403 Forbidden when accessing https://www.instagram.com/graphql/query
```

## Solutions

### Solution 1: Login with Instagram Credentials (Recommended)

The easiest and most reliable solution is to login with your Instagram credentials:

1. Open the application
2. Check the "Login to Instagram" checkbox
3. Enter your Instagram username and password
4. Start processing

**Benefits:**
- Most reliable method
- Works for public and private content
- Session can be saved for future use

**Note:** Your credentials are sent directly to Instagram and are not stored or logged by this application.

### Solution 2: Import Browser Session Cookies

If you're already logged into Instagram in your browser, you can import those cookies:

#### Step 1: Install browser_cookie3

```bash
pip install browser_cookie3
```

#### Step 2: Use the browser session import

You have two options:

**Option A: Through the GUI (if implemented)**
- Check "Import session from browser"
- Application will automatically use your browser cookies

**Option B: Through Python code**
```python
from modules import InstagramDownloader

downloader = InstagramDownloader()
downloader.setup_instaloader()

# Import session from Chrome (replace with your Instagram username)
downloader.load_session_from_browser('your_instagram_username')

# Now download reels
success, video_path, error = downloader.download_reel('https://www.instagram.com/reel/ABC123/')
```

**Supported browsers:**
- Chrome
- Firefox
- Edge
- Safari (macOS only)

### Solution 3: Wait and Retry

If you've been making many requests, Instagram may have temporarily rate-limited you:

1. **Wait 10-30 minutes** before trying again
2. **Reduce download frequency** - increase delay between downloads
3. **Process in smaller batches** - try 10-20 reels at a time instead of hundreds

### Solution 4: Update Configuration

The application now includes improved anti-detection measures. Make sure you're using the latest version:

1. Pull the latest code:
   ```bash
   git pull origin main
   ```

2. Update dependencies:
   ```bash
   pip install -r requirements.txt --upgrade
   ```

## What Was Fixed

Recent updates include:

1. **Better User-Agent**: Requests now appear more like a real browser
2. **Rate limiting**: Automatic delays between requests (2-4 seconds randomized)
3. **Session management**: Improved handling of authentication sessions
4. **Error messages**: Clearer guidance when errors occur

## Prevention Tips

To avoid 403 errors in the future:

1. **Always use authentication** when downloading multiple reels
2. **Don't rush** - use reasonable delays between downloads (3-5 seconds)
3. **Process in batches** - don't try to download thousands of reels at once
4. **Save your session** - reuse authenticated sessions instead of logging in repeatedly
5. **Use browser cookies** - if you're logged in on your browser, import those cookies

## Still Having Issues?

If none of these solutions work:

1. **Check Instagram's status**: Sometimes Instagram's API has issues
2. **Try a different network**: Switch from WiFi to mobile data or vice versa
3. **Use a VPN**: Sometimes IP addresses get blocked temporarily
4. **Wait longer**: If you've been heavily using the tool, wait several hours

## Technical Details

The 403 error occurs because Instagram's GraphQL API uses several anti-bot measures:

- **Request fingerprinting**: Analyzing headers, user agents, and request patterns
- **Rate limiting**: Blocking too many requests from the same IP/session
- **Session validation**: Checking for valid authentication cookies
- **Behavior analysis**: Detecting non-human request patterns

Our fixes address these by:
- Using realistic browser headers
- Adding random delays between requests
- Supporting authenticated sessions
- Mimicking human behavior patterns

## Contact

If you continue to experience issues after trying all solutions, please open an issue on GitHub with:
- Error message (full stack trace)
- Steps you've tried
- Your configuration (Python version, OS, etc.)
