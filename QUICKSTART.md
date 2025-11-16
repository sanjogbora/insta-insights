# Quick Start Guide

Get up and running with Instagram Reel Transcriber in 5 minutes!

## Step 1: Install FFmpeg

**This is required!** Whisper needs FFmpeg to process audio.

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

## Step 2: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Note**: First installation may take 5-10 minutes as it downloads PyTorch and other large packages.

## Step 3: Verify Installation

```bash
python verify_installation.py
```

You should see all checks passing (✓). GPU check is optional.

## Step 4: Prepare Your Excel File

Create an Excel file (`.xlsx`) with Instagram URLs:

| Instagram URL | Reel Title |
|--------------|------------|
| https://www.instagram.com/reel/ABC123/ | My First Reel |
| https://www.instagram.com/reel/DEF456/ | My Second Reel |

**Important**: Start with just 2-3 URLs to test!

## Step 5: Run the Application

```bash
python main.py
```

## Step 6: Process Your Reels

1. Click **"Select Excel File"** and choose your file
2. Verify the URL column name (default: "Instagram URL")
3. Choose Whisper model:
   - **tiny**: Fastest, for testing
   - **base**: Recommended for most users
   - **small**: Better accuracy, slower
4. Click **"Start Processing"**
5. Wait for completion (first run downloads the Whisper model)

## Step 7: Get Your Results

- Transcriptions are automatically saved to your Excel file
- A new column "Transcription" contains the results
- Failed items are logged in `output/failed_items.txt`

## Troubleshooting

### "FFmpeg not found"
- Make sure FFmpeg is installed and in your PATH
- Restart terminal after installing FFmpeg
- Test: `ffmpeg -version` should work

### "Out of memory"
- Use a smaller model (tiny or base)
- Close other applications
- Process fewer reels at once

### Downloads fail
- Check if URLs are correct and public
- Try enabling Instagram login for private content
- Increase delay in `config/settings.py` (DOWNLOAD_DELAY_SECONDS = 5)

### Very slow transcription
- This is normal on CPU
- Expect ~1-2 minutes per video with "base" model
- Use "tiny" model for faster results
- Use GPU for 10x speedup

## Tips for Large Batches

Processing 5000 reels:
1. Start with 10-20 reels to test
2. Use "base" model (good balance)
3. Process overnight (will take several hours on CPU)
4. Enable "Continue on Error" (default: on)
5. Check `output/failed_items.txt` for failures
6. Re-run failed items separately if needed

## Expected Processing Times

**Per video** (approximate):
- **tiny** model: 20-40 seconds (CPU) / 5-10 seconds (GPU)
- **base** model: 1-2 minutes (CPU) / 15-30 seconds (GPU)  ← Recommended
- **small** model: 2-4 minutes (CPU) / 30-60 seconds (GPU)
- **medium** model: 5-10 minutes (CPU) / 1-2 minutes (GPU)

**For 5000 videos** (with base model):
- CPU: ~100-150 hours (4-6 days)
- GPU: ~20-40 hours (1-2 days)

**Recommendation**: Process in batches of 200-500 for easier monitoring.

## Getting Help

1. Check `logs/app.log` for detailed error messages
2. Review the full [README.md](README.md) for advanced options
3. Open an issue on GitHub with:
   - Error message
   - Python version (`python --version`)
   - OS version
   - Steps to reproduce

---

**That's it! Happy transcribing! 🎉**
