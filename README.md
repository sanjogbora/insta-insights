# Instagram Reel Bulk Downloader & Transcriber

A powerful desktop application for bulk downloading Instagram reels and transcribing them using OpenAI Whisper.

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- **Bulk Download**: Download multiple Instagram reels from Excel spreadsheet
- **AI Transcription**: Automatic transcription using OpenAI Whisper
- **Modern GUI**: Beautiful interface built with CustomTkinter
- **Progress Tracking**: Real-time progress bars and status updates
- **Error Handling**: Continues processing even if some items fail
- **Excel Integration**: Read URLs from Excel and write transcriptions back
- **No Authentication Required**: Uses browser cookies automatically (like Chrome extensions!)
- **Multiple Whisper Models**: Choose from tiny to large models based on your needs
- **🚀 Universal GPU Support**: Automatically detects and uses available GPU acceleration

## GPU Support

The application **automatically detects and uses the best available compute device** without requiring manual configuration:

### Supported Devices (Auto-Detected)

| Device Type | Platform | Performance | Notes |
|------------|----------|-------------|-------|
| **NVIDIA GPU (CUDA)** | Windows, Linux | 🔥 Very Fast (5-10x) | Most common, best supported |
| **Apple Silicon (MPS)** | macOS M1/M2/M3 | 🔥 Very Fast (5-10x) | Native Apple GPU acceleration |
| **AMD GPU (ROCm)** | Linux only | 🔥 Fast | Requires ROCm PyTorch build |
| **CPU** | All platforms | ✅ Works (slower) | Universal fallback |

### How It Works

1. **Automatic Detection**: When you start the app, it automatically detects what GPU/device you have
2. **Smart Selection**: Uses the fastest available device (CUDA → MPS → ROCm → CPU)
3. **No Configuration Needed**: Works with whatever PyTorch version you already have installed
4. **Visual Feedback**: Shows which device is being used in the GUI

### What You'll See

The GUI displays your detected device:
```
Compute Device: NVIDIA GeForce RTX 3060 (CUDA)  Speed: Very Fast (Modern GPU)
```

Or for Apple Silicon:
```
Compute Device: Apple Silicon GPU (MPS)  Speed: Fast (Apple Silicon)
```

### Performance Comparison

**Per video transcription (base model):**
- GPU (CUDA/MPS): ~15-30 seconds ⚡
- CPU: ~1-2 minutes 🐌

**For 5000 videos:**
- GPU: ~20-40 hours (1-2 days)
- CPU: ~100-150 hours (4-6 days)

### Troubleshooting GPU Issues

If you have a GPU but it's not detected:

```bash
# Run the diagnostic tool
python diagnose_gpu.py
```

This will:
- Detect your GPU type
- Check PyTorch installation
- Provide specific fix instructions

**Common issue**: PyTorch installed without CUDA/MPS support
**Solution**: The diagnostic tool will show you exactly how to fix it

### Installation Notes

**The app works with your existing PyTorch installation** - you don't need to reinstall anything unless you want GPU support.

If you want GPU acceleration:

**NVIDIA GPU (Windows/Linux):**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**Apple Silicon (macOS):**
```bash
pip install torch torchvision torchaudio
# MPS support is included by default on macOS
```

**AMD GPU (Linux only):**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.6
```

## Screenshots

```
┌─────────────────────────────────────────────────────┐
│  Instagram Reel Bulk Downloader & Transcriber       │
├─────────────────────────────────────────────────────┤
│  Excel File: [sample_reels.xlsx]    [Select File]  │
│  URL Column: [Instagram URL]                        │
│  Download Folder: [./downloads]     [Select Folder] │
├─────────────────────────────────────────────────────┤
│  Settings                                           │
│  Whisper Model: [base ▼] Balanced - Recommended    │
│  ☐ Login to Instagram (for private content)        │
├─────────────────────────────────────────────────────┤
│  Progress                                           │
│  Overall: [████████████────────] 12/20 items        │
│  Current: Transcribing video 12/20...               │
│  Status Log: [Download successful...]              │
├─────────────────────────────────────────────────────┤
│  [Start Processing]  [Stop]      [Export Results]  │
├─────────────────────────────────────────────────────┤
│  Summary                                            │
│  Downloaded: 12/20  Transcribed: 11/20  Failed: 1  │
└─────────────────────────────────────────────────────┘
```

## Requirements

### System Requirements

- **Python**: 3.8 or higher
- **FFmpeg**: Required by Whisper for audio processing
- **RAM**: Minimum 4GB (8GB+ recommended for larger models)
- **GPU**: Optional (CUDA-compatible GPU for faster transcription)

### Installing FFmpeg

**Windows:**
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract and add to PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd insta-insights
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: The first time you run the application, Whisper will download the selected model (500MB - 3GB depending on model size).

## Usage

### Quick Start

1. **Launch the application:**
   ```bash
   python main.py
   ```

2. **Prepare your Excel file** with Instagram URLs:

   | Instagram URL | Reel Title |
   |--------------|------------|
   | https://www.instagram.com/reel/ABC123/ | Sample Reel 1 |
   | https://www.instagram.com/reel/DEF456/ | Sample Reel 2 |

3. **In the application:**
   - Click "Select Excel File" and choose your file
   - Verify the URL column name (default: "Instagram URL")
   - Choose download folder (optional)
   - Select Whisper model (recommended: "base")
   - Click "Start Processing"

4. **Wait for completion** - transcriptions will be saved to your Excel file in a new "Transcription" column

### Excel File Format

Your Excel file should have at least one column containing Instagram reel URLs. The application will:
- Read URLs from the specified column (default: "Instagram URL")
- Add a new column "Transcription" with the results
- Preserve all other data in your Excel file

**Supported URL formats:**
- `https://www.instagram.com/reel/SHORTCODE/`
- `https://instagram.com/reel/SHORTCODE/`
- `https://www.instagram.com/p/SHORTCODE/`
- `https://instagram.com/tv/SHORTCODE/`

### Whisper Model Selection

Choose based on your needs:

| Model | Speed | Accuracy | RAM Usage | Use Case |
|-------|-------|----------|-----------|----------|
| **tiny** | Fastest | Basic | ~1 GB | Testing, quick drafts |
| **base** | Fast | Good | ~1.5 GB | **Recommended for most users** |
| **small** | Medium | Better | ~2.5 GB | Higher accuracy needed |
| **medium** | Slow | High | ~5 GB | Professional work |
| **large** | Very Slow | Best | ~10 GB | Maximum accuracy (GPU recommended) |

### How Downloading Works (No Login Required!)

The application uses **yt-dlp** to download Instagram reels, automatically extracting cookies from your browser:

1. **Just stay logged into Instagram** in Firefox (recommended), Edge, Safari, or Chrome
2. The app automatically uses your browser cookies (like Chrome extensions do!)
3. **No manual authentication needed** - works out of the box for public content

**Recommended:** Use **Firefox** for the best experience (it handles concurrent access better than Chrome)

**Chrome users:** If you see a "cookie database locked" error, either close Chrome or use Firefox instead.

**For detailed information**, see [YT_DLP_USAGE_GUIDE.md](YT_DLP_USAGE_GUIDE.md)

**How it works:**
- The app reads cookies from your browser's local database
- Uses those cookies to download reels (exactly like browser extensions)
- No data is sent to external servers - all downloads are direct from Instagram

## Configuration

Edit `config/settings.py` to customize:

```python
# Default paths
DEFAULT_DOWNLOAD_FOLDER = "./downloads"
DEFAULT_EXCEL_COLUMN = "Instagram URL"
DEFAULT_TRANSCRIPTION_COLUMN = "Transcription"

# Whisper settings
DEFAULT_WHISPER_MODEL = "base"

# Download settings
DOWNLOAD_DELAY_SECONDS = 3  # Delay between downloads
MAX_RETRIES = 3

# GUI settings
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 750
THEME = "dark"  # "dark" or "light"
```

## Project Structure

```
instagram-reel-transcriber/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── gui/
│   ├── __init__.py
│   └── app_gui.py         # GUI implementation
├── modules/
│   ├── __init__.py
│   ├── downloader.py      # Instagram download logic
│   ├── transcriber.py     # Whisper transcription
│   └── excel_handler.py   # Excel operations
├── config/
│   ├── __init__.py
│   └── settings.py        # Configuration
├── downloads/             # Downloaded videos (created automatically)
├── output/               # Output files (created automatically)
└── logs/                 # Application logs (created automatically)
```

## Troubleshooting

### 403 Forbidden Error (Instagram Blocking Requests)

If you see errors like `403 Forbidden`:

**Quick Fix:** Make sure you're logged into Instagram in Chrome, Firefox, Edge, or Safari.

**For detailed solutions, see [YT_DLP_USAGE_GUIDE.md](YT_DLP_USAGE_GUIDE.md)**

### Common Issues

**1. "403 Forbidden" errors**
- **Solution**: Login to Instagram in your browser (Chrome, Firefox, Edge, or Safari)
- **How it works**: The app automatically uses your browser cookies
- **See**: [YT_DLP_USAGE_GUIDE.md](YT_DLP_USAGE_GUIDE.md) for complete guide

**2. "No browser cookies found" warning**
- **Solution**: Make sure you're logged into Instagram in one of the supported browsers
- **Supported**: Chrome, Firefox, Edge, Safari

**3. "FFmpeg not found" error**
- Solution: Install FFmpeg and add to PATH (see Requirements section)

**4. "Out of memory" error**
- Solution: Use a smaller Whisper model (tiny or base)

**5. Download fails with rate limiting**
- Solution: Increase `DOWNLOAD_DELAY_SECONDS` in settings.py
- Solution: Enable Instagram login

**6. Transcription is very slow**
- Solution: Use smaller model (tiny or base)
- Solution: Use GPU if available (install CUDA for nvidia GPUs)

### Performance Tips

1. **For large batches (1000+ reels)**:
   - Use the "base" model (good balance of speed/accuracy)
   - Enable GPU acceleration if available
   - Process in smaller batches (200-300 at a time)
   - Estimated time: ~2-3 minutes per video on CPU, ~30 seconds on GPU

2. **For maximum speed**:
   - Use "tiny" model
   - Disable Instagram login
   - Ensure good internet connection

3. **For maximum accuracy**:
   - Use "medium" or "large" model
   - GPU highly recommended
   - Allow more processing time

## Advanced Usage

### Using as a Python Module

```python
from modules import ExcelHandler, InstagramDownloader, WhisperTranscriber

# Download a single reel
downloader = InstagramDownloader()
success, video_path, error = downloader.download_reel(
    "https://www.instagram.com/reel/ABC123/"
)

# Transcribe a video
transcriber = WhisperTranscriber(model_size="base")
success, transcription, full_result, error = transcriber.transcribe_video(video_path)

print(transcription)
```

### Batch Processing Script

```python
from modules import ExcelHandler, InstagramDownloader, WhisperTranscriber

# Read URLs
handler = ExcelHandler("my_reels.xlsx")
urls = handler.read_links_from_excel()

# Download
downloader = InstagramDownloader()
download_results = downloader.batch_download(urls)

# Transcribe
transcriber = WhisperTranscriber("base")
video_paths = [path for url, path in download_results['successful']]
transcription_results = transcriber.batch_transcribe(video_paths)

# Save results
transcriptions = {
    url: trans
    for (url, _), (_, trans) in zip(
        download_results['successful'],
        transcription_results['successful']
    )
}
handler.write_transcriptions_to_excel(transcriptions)
```

## Legal & Ethical Considerations

**Important**: Please respect Instagram's Terms of Service and content creators' rights:

- Only download content you have permission to download
- Respect copyright and intellectual property
- Be mindful of rate limiting (don't spam requests)
- Use responsibly and ethically

This tool is intended for:
- Personal backups
- Content analysis with permission
- Research purposes
- Accessibility (creating transcriptions)

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - see LICENSE file for details

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition model
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Universal media downloader
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern GUI framework

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**Made with ❤️ by Claude Code**
