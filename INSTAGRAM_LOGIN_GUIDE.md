# Instagram Login Guide - 2FA & Troubleshooting

## Quick Solution for 2FA Users

If you have **two-factor authentication (2FA)** enabled on Instagram, follow these steps:

### Option 1: Create a Session File (Recommended)

This is the easiest way to handle 2FA:

```bash
python create_instagram_session.py
```

**What this does:**
1. Asks for your Instagram username and password
2. Prompts for your 2FA code when Instagram sends it
3. Creates a session file that the app can use
4. No need to login again each time!

**Follow the prompts:**
```
Instagram username: your_username
Instagram password: ********
Enter 2FA code: 123456
✓ Session saved!
```

**That's it!** The main app will automatically use this session.

---

## Detailed Instructions

### Step 1: Run the Session Creator

```bash
python create_instagram_session.py
```

### Step 2: Enter Your Credentials

- **Username**: Your Instagram username (without @)
- **Password**: Your Instagram password (input is hidden)

### Step 3: Handle 2FA

Instagram will send you a code via:
- SMS to your phone
- Authentication app (Google Authenticator, Authy, etc.)
- WhatsApp

Enter the 6-digit code when prompted.

### Step 4: Session Saved!

The script will save a session file at:
```
config/instagram_session_your_username
```

### Step 5: Use the Main App

Now when you run the main app:
```bash
python main.py
```

It will **automatically detect and use** your saved session. No need to enter credentials again!

---

## How to Verify It's Working

When you start processing in the GUI, check the status log. You should see:

```
✓ Using saved Instagram session (no login required)
```

Or:

```
Auto-loaded session from: config/instagram_session_yourusername
```

If you see these messages, you're good to go!

---

## Troubleshooting

### "Login failed: 2FA required"

**Solution**: Use the `create_instagram_session.py` script instead of the GUI login.

The GUI login doesn't support 2FA prompts (requires terminal input), so you need to create a session file first.

### "Session expired" or "Login required" errors

Sessions can expire after a few weeks/months.

**Solution**: Re-run the session creator:
```bash
python create_instagram_session.py
```

### "Two-factor authentication required" error persists

1. Make sure you're entering the correct 2FA code
2. Check if your 2FA code hasn't expired (codes usually last 30 seconds)
3. Try using a different 2FA method (SMS vs Auth App)

### I don't have 2FA enabled but still get errors

If you don't have 2FA, you can:
- **Option A**: Use the GUI login (check "Login to Instagram" box)
- **Option B**: Still create a session file for better reliability

### How to switch accounts?

1. Run `create_instagram_session.py` again with different username
2. The new session will be used automatically
3. Old sessions remain in the `config/` folder

To manually select a session:
- Delete old session files from `config/` folder
- Keep only the one you want to use

---

## Session File Management

### Where are sessions stored?

```
config/instagram_session_username
```

### How long do sessions last?

- Sessions can last **weeks to months**
- Instagram may invalidate them if:
  - You change your password
  - You login from a new device
  - Instagram detects unusual activity

### Can I copy session files between computers?

**Yes!** Session files are portable:

1. Copy from: `config/instagram_session_username`
2. Paste to: Same location on other computer
3. App will auto-detect it

### Should I commit session files to git?

**NO!** Session files contain your login tokens.

The `.gitignore` file already excludes them:
```
config/instagram_session*
config/*.json
```

---

## Alternative: No Login (Public Content Only)

If you only need to download **public reels**:

1. **Don't** check "Login to Instagram" in the GUI
2. **Don't** create a session file
3. Just start processing

**Limitations:**
- Can only download public content
- More likely to hit rate limits
- May encounter 403 errors (Instagram blocking)

**Recommendation:** Create a session file even for public content - it's more reliable.

---

## Security Notes

### Is it safe to enter my password?

**Yes**, with caveats:
- Password is sent directly to Instagram (not stored anywhere)
- Uses official `instaloader` library (open source, audited)
- Session file contains tokens, not your password
- Keep session files private (don't share/commit)

### What if Instagram blocks me?

Instagram's anti-bot systems may temporarily restrict your account if you:
- Download too many reels too quickly
- Use automation tools frequently

**Prevention:**
- Use reasonable download delays (3-5 seconds)
- Don't download thousands of reels per hour
- Login with a real account (not a bot account)

**If blocked:**
- Wait 24-48 hours
- Try logging in from Instagram app/website
- Reduce download speed in `config/settings.py`

---

## Quick Reference

| Problem | Solution |
|---------|----------|
| 2FA required | Run `create_instagram_session.py` |
| Session expired | Re-run session creator |
| 403 Forbidden | Create session file or enable login |
| Rate limiting | Increase delay in settings, use session |
| Don't have 2FA | Can use GUI login OR session file |
| Multiple accounts | Create separate session files |

---

## Need More Help?

1. Check main README.md for general troubleshooting
2. Run `python diagnose_gpu.py` for system diagnostics
3. Check logs in `logs/app.log`
4. Open an issue on GitHub

---

**TL;DR for 2FA users:**

```bash
python create_instagram_session.py
# Enter username, password, and 2FA code
# Then run the main app - it will auto-use the session!
```
