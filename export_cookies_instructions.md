# How to Export Instagram Cookies (Windows Fix)

## Problem
Windows encrypts Chrome cookies with DPAPI, preventing yt-dlp from reading them.

## Solution: Export Cookies Manually

This is a **one-time setup** that works 100% reliably.

### Step 1: Install Browser Extension

**For Chrome:**
1. Go to: https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc
2. Click "Add to Chrome"

**For Firefox:**
1. Go to: https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/
2. Click "Add to Firefox"

**For Edge:**
1. Go to: https://microsoftedge.microsoft.com/addons/detail/get-cookiestxt-locally/kkdlmpiopnjghnepcbakongjghdgihgk
2. Click "Get"

### Step 2: Export Instagram Cookies

1. **Login to Instagram** in your browser (instagram.com)
2. **Click the extension icon** in your browser toolbar
3. **Click "Export"** or "Get cookies.txt"
4. **Save the file** as `instagram_cookies.txt`
5. **Move the file** to your insta-insights folder (same folder as main.py)

### Step 3: Use in the App

The app will automatically detect and use `instagram_cookies.txt` if it exists in the project folder.

**File location:**
```
insta-insights/
├── instagram_cookies.txt  ← Put it here!
├── main.py
├── requirements.txt
└── ...
```

### Step 4: Run the App

That's it! The app will now use your exported cookies automatically.

---

## Why This Works

- Bypasses Windows DPAPI encryption entirely
- Cookies are already decrypted in the .txt file
- Works on any operating system
- 100% reliable, no compatibility issues

## How Often to Update

Cookies expire after ~90 days. If downloads start failing:
1. Re-export cookies from your browser
2. Replace `instagram_cookies.txt`
3. Done!

## Security Note

The `instagram_cookies.txt` file contains your Instagram session. Keep it private:
- ✅ DO: Keep it in your project folder
- ❌ DON'T: Share it with anyone
- ❌ DON'T: Commit it to git (already in .gitignore)
