"""
GUI Application for Instagram Reel Transcriber.
Built with CustomTkinter for a modern look.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
from typing import Optional
import sys

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.excel_handler import ExcelHandler
from modules.downloader import InstagramDownloader
from modules.transcriber import WhisperTranscriber
from modules.device_manager import DeviceManager
from config import settings


class InstagramTranscriberApp(ctk.CTk):
    """Main GUI application for Instagram Reel Transcriber."""

    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Instagram Reel Bulk Downloader & Transcriber")
        self.geometry(f"{settings.WINDOW_WIDTH}x{settings.WINDOW_HEIGHT}")

        # Set theme
        ctk.set_appearance_mode(settings.THEME)
        ctk.set_default_color_theme(settings.COLOR_THEME)

        # Initialize variables
        self.excel_file_path = None
        self.download_folder = settings.DEFAULT_DOWNLOAD_FOLDER
        self.is_processing = False
        self.should_stop = False

        # Processing components
        self.excel_handler = None
        self.downloader = None
        self.transcriber = None

        # URLs and results
        self.urls = []
        self.transcriptions = {}
        self.failed_items = []

        # Statistics
        self.total_items = 0
        self.downloaded_count = 0
        self.transcribed_count = 0
        self.failed_count = 0

        # Detect compute device (GPU/CPU)
        self.device_manager = DeviceManager()
        self.device_manager.detect_best_device()

        # Create UI
        self.create_widgets()

    def create_widgets(self):
        """Create all UI widgets."""
        # Main container with padding
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            main_container,
            text="Instagram Reel Bulk Downloader & Transcriber",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 20))

        # File Selection Section
        self.create_file_selection_section(main_container)

        # Settings Section
        self.create_settings_section(main_container)

        # Progress Section
        self.create_progress_section(main_container)

        # Control Buttons
        self.create_control_buttons(main_container)

        # Results Summary
        self.create_results_section(main_container)

    def create_file_selection_section(self, parent):
        """Create file and folder selection widgets."""
        file_frame = ctk.CTkFrame(parent)
        file_frame.pack(fill="x", pady=(0, 15))

        # Excel file selection
        excel_label = ctk.CTkLabel(file_frame, text="Excel File:", font=ctk.CTkFont(weight="bold"))
        excel_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.excel_path_label = ctk.CTkLabel(
            file_frame,
            text="No file selected",
            text_color="gray"
        )
        self.excel_path_label.grid(row=0, column=1, sticky="w", padx=10, pady=5)

        excel_button = ctk.CTkButton(
            file_frame,
            text="Select Excel File",
            command=self.select_excel_file,
            width=150
        )
        excel_button.grid(row=0, column=2, padx=10, pady=5)

        # Column name entry
        column_label = ctk.CTkLabel(file_frame, text="URL Column:")
        column_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)

        self.column_entry = ctk.CTkEntry(file_frame, width=200)
        self.column_entry.insert(0, settings.DEFAULT_EXCEL_COLUMN)
        self.column_entry.grid(row=1, column=1, sticky="w", padx=10, pady=5)

        # Download folder selection
        folder_label = ctk.CTkLabel(file_frame, text="Download Folder:", font=ctk.CTkFont(weight="bold"))
        folder_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)

        self.folder_path_label = ctk.CTkLabel(
            file_frame,
            text=self.download_folder,
            text_color="gray"
        )
        self.folder_path_label.grid(row=2, column=1, sticky="w", padx=10, pady=5)

        folder_button = ctk.CTkButton(
            file_frame,
            text="Select Folder",
            command=self.select_download_folder,
            width=150
        )
        folder_button.grid(row=2, column=2, padx=10, pady=5)

        file_frame.columnconfigure(1, weight=1)

    def create_settings_section(self, parent):
        """Create settings widgets."""
        settings_frame = ctk.CTkFrame(parent)
        settings_frame.pack(fill="x", pady=(0, 15))

        settings_title = ctk.CTkLabel(
            settings_frame,
            text="Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        settings_title.pack(pady=(10, 10))

        # Whisper model selection
        model_frame = ctk.CTkFrame(settings_frame)
        model_frame.pack(fill="x", padx=10, pady=5)

        model_label = ctk.CTkLabel(model_frame, text="Whisper Model:")
        model_label.pack(side="left", padx=10)

        self.model_var = ctk.StringVar(value=settings.DEFAULT_WHISPER_MODEL)
        self.model_dropdown = ctk.CTkOptionMenu(
            model_frame,
            values=settings.WHISPER_MODELS,
            variable=self.model_var,
            command=self.on_model_changed
        )
        self.model_dropdown.pack(side="left", padx=10)

        self.model_desc_label = ctk.CTkLabel(
            model_frame,
            text=settings.WHISPER_MODEL_DESCRIPTIONS[settings.DEFAULT_WHISPER_MODEL],
            text_color="gray"
        )
        self.model_desc_label.pack(side="left", padx=10)

        # Device info display
        device_frame = ctk.CTkFrame(settings_frame)
        device_frame.pack(fill="x", padx=10, pady=5)

        device_label = ctk.CTkLabel(device_frame, text="Compute Device:", font=ctk.CTkFont(weight="bold"))
        device_label.pack(side="left", padx=10)

        # Get device info
        device_name = self.device_manager.get_friendly_name()
        device_type = self.device_manager.device_type.upper()
        speed_estimate = self.device_manager.get_speed_estimate()

        # Color code based on device type
        if self.device_manager.device_type == "cuda":
            device_color = "green"
        elif self.device_manager.device_type == "mps":
            device_color = "blue"
        elif self.device_manager.device_type == "rocm":
            device_color = "orange"
        else:
            device_color = "gray"

        self.device_info_label = ctk.CTkLabel(
            device_frame,
            text=f"{device_name} ({device_type})",
            text_color=device_color,
            font=ctk.CTkFont(weight="bold")
        )
        self.device_info_label.pack(side="left", padx=10)

        self.device_speed_label = ctk.CTkLabel(
            device_frame,
            text=f"Speed: {speed_estimate}",
            text_color="gray"
        )
        self.device_speed_label.pack(side="left", padx=10)

        # Browser Session Import
        browser_frame = ctk.CTkFrame(settings_frame)
        browser_frame.pack(fill="x", padx=10, pady=5)

        browser_label = ctk.CTkLabel(browser_frame, text="Browser Session:", font=ctk.CTkFont(weight="bold"))
        browser_label.pack(side="left", padx=10)

        self.browser_var = ctk.StringVar(value="auto")
        self.browser_dropdown = ctk.CTkOptionMenu(
            browser_frame,
            values=["auto", "chrome", "firefox", "edge", "safari"],
            variable=self.browser_var,
            command=self.on_browser_changed,
            width=120
        )
        self.browser_dropdown.pack(side="left", padx=5)

        self.import_browser_button = ctk.CTkButton(
            browser_frame,
            text="Import Browser Session",
            command=self.import_browser_session,
            width=180
        )
        self.import_browser_button.pack(side="left", padx=5)

        self.browser_status_label = ctk.CTkLabel(
            browser_frame,
            text="Auto-detect from open browsers",
            text_color="gray"
        )
        self.browser_status_label.pack(side="left", padx=10)

        # Instagram login option
        login_frame = ctk.CTkFrame(settings_frame)
        login_frame.pack(fill="x", padx=10, pady=5)

        self.login_var = ctk.BooleanVar(value=False)
        self.login_checkbox = ctk.CTkCheckBox(
            login_frame,
            text="Login to Instagram (for private content)",
            variable=self.login_var,
            command=self.toggle_login_fields
        )
        self.login_checkbox.pack(side="left", padx=10)

        # Login credentials (hidden by default)
        self.credentials_frame = ctk.CTkFrame(settings_frame)

        username_label = ctk.CTkLabel(self.credentials_frame, text="Username:")
        username_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.username_entry = ctk.CTkEntry(self.credentials_frame, width=200)
        self.username_entry.grid(row=0, column=1, padx=10, pady=5)

        password_label = ctk.CTkLabel(self.credentials_frame, text="Password:")
        password_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.password_entry = ctk.CTkEntry(self.credentials_frame, width=200, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)

    def create_progress_section(self, parent):
        """Create progress tracking widgets."""
        progress_frame = ctk.CTkFrame(parent)
        progress_frame.pack(fill="both", expand=True, pady=(0, 15))

        progress_title = ctk.CTkLabel(
            progress_frame,
            text="Progress",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        progress_title.pack(pady=(10, 10))

        # Overall progress
        overall_label = ctk.CTkLabel(progress_frame, text="Overall Progress:")
        overall_label.pack(anchor="w", padx=10, pady=(5, 0))

        self.overall_progress = ctk.CTkProgressBar(progress_frame)
        self.overall_progress.pack(fill="x", padx=10, pady=5)
        self.overall_progress.set(0)

        self.overall_progress_label = ctk.CTkLabel(progress_frame, text="0/0 items processed")
        self.overall_progress_label.pack(anchor="w", padx=10)

        # Current task progress
        current_label = ctk.CTkLabel(progress_frame, text="Current Task:")
        current_label.pack(anchor="w", padx=10, pady=(10, 0))

        self.current_task_label = ctk.CTkLabel(
            progress_frame,
            text="Waiting to start...",
            text_color="gray"
        )
        self.current_task_label.pack(anchor="w", padx=10, pady=5)

        # Status log
        log_label = ctk.CTkLabel(progress_frame, text="Status Log:")
        log_label.pack(anchor="w", padx=10, pady=(10, 0))

        self.status_text = ctk.CTkTextbox(progress_frame, height=150)
        self.status_text.pack(fill="both", expand=True, padx=10, pady=5)

    def create_control_buttons(self, parent):
        """Create control buttons."""
        button_frame = ctk.CTkFrame(parent)
        button_frame.pack(fill="x", pady=(0, 15))

        self.start_button = ctk.CTkButton(
            button_frame,
            text="Start Processing",
            command=self.start_processing,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.start_button.pack(side="left", padx=10, pady=10)

        self.stop_button = ctk.CTkButton(
            button_frame,
            text="Stop",
            command=self.stop_processing,
            width=100,
            height=40,
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=10, pady=10)

        self.export_button = ctk.CTkButton(
            button_frame,
            text="Export Results",
            command=self.export_results,
            width=150,
            height=40,
            state="disabled"
        )
        self.export_button.pack(side="right", padx=10, pady=10)

    def create_results_section(self, parent):
        """Create results summary section."""
        results_frame = ctk.CTkFrame(parent)
        results_frame.pack(fill="x")

        results_title = ctk.CTkLabel(
            results_frame,
            text="Summary",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        results_title.pack(pady=(10, 10))

        stats_container = ctk.CTkFrame(results_frame)
        stats_container.pack(fill="x", padx=10, pady=(0, 10))

        # Downloaded
        self.downloaded_label = ctk.CTkLabel(
            stats_container,
            text="Downloaded: 0/0",
            font=ctk.CTkFont(size=13)
        )
        self.downloaded_label.pack(side="left", padx=20)

        # Transcribed
        self.transcribed_label = ctk.CTkLabel(
            stats_container,
            text="Transcribed: 0/0",
            font=ctk.CTkFont(size=13)
        )
        self.transcribed_label.pack(side="left", padx=20)

        # Failed
        self.failed_label = ctk.CTkLabel(
            stats_container,
            text="Failed: 0",
            font=ctk.CTkFont(size=13),
            text_color="red"
        )
        self.failed_label.pack(side="left", padx=20)

    # Event Handlers
    def select_excel_file(self):
        """Open file dialog to select Excel file."""
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            self.excel_file_path = file_path
            self.excel_path_label.configure(text=os.path.basename(file_path))
            self.log_status(f"Selected Excel file: {os.path.basename(file_path)}")

    def select_download_folder(self):
        """Open folder dialog to select download folder."""
        folder_path = filedialog.askdirectory(title="Select Download Folder")

        if folder_path:
            self.download_folder = folder_path
            self.folder_path_label.configure(text=folder_path)
            self.log_status(f"Download folder set to: {folder_path}")

    def on_model_changed(self, choice):
        """Update model description when model is changed."""
        description = settings.WHISPER_MODEL_DESCRIPTIONS.get(choice, "")
        self.model_desc_label.configure(text=description)

    def toggle_login_fields(self):
        """Show/hide login credential fields."""
        if self.login_var.get():
            self.credentials_frame.pack(fill="x", padx=10, pady=5)
        else:
            self.credentials_frame.pack_forget()

    def on_browser_changed(self, choice):
        """Update browser status label when browser is changed."""
        browser_descriptions = {
            "auto": "Auto-detect from open browsers",
            "chrome": "Use Google Chrome session",
            "firefox": "Use Mozilla Firefox session",
            "edge": "Use Microsoft Edge session",
            "safari": "Use Apple Safari session"
        }
        description = browser_descriptions.get(choice, "")
        self.browser_status_label.configure(text=description)

    def import_browser_session(self):
        """Import browser session for Instagram authentication."""
        selected_browser = self.browser_var.get()

        # Show loading state
        original_text = self.import_browser_button.cget("text")
        self.import_browser_button.configure(text="Importing...", state="disabled")
        self.browser_status_label.configure(text="Testing browser session...", text_color="orange")

        def test_browser():
            """Test browser session in separate thread."""
            try:
                # Create a test downloader with selected browser
                test_downloader = InstagramDownloader(self.download_folder, selected_browser)

                # Try to detect browser cookies
                if selected_browser == "auto":
                    browsers_to_try = ['firefox', 'edge', 'safari', 'chrome']
                else:
                    browsers_to_try = [selected_browser]

                browser_found = None
                for browser in browsers_to_try:
                    try:
                        import yt_dlp
                        test_opts = {
                            'quiet': True,
                            'no_warnings': True,
                            'cookiesfrombrowser': (browser,),
                            'extract_flat': True
                        }
                        with yt_dlp.YoutubeDL(test_opts) as test_ydl:
                            pass
                        browser_found = browser
                        break
                    except:
                        continue

                # Update UI in main thread
                self.after(0, lambda: self._update_browser_import_result(browser_found, selected_browser, original_text))

            except Exception as e:
                self.after(0, lambda: self._update_browser_import_error(str(e), original_text))

        # Run test in separate thread
        thread = threading.Thread(target=test_browser, daemon=True)
        thread.start()

    def _update_browser_import_result(self, browser_found, selected_browser, original_button_text):
        """Update UI after browser session test."""
        self.import_browser_button.configure(text=original_button_text, state="normal")

        if browser_found:
            # Success!
            if selected_browser == "auto":
                message = f"✓ Found {browser_found.title()} session"
                self.log_status(f"Successfully imported {browser_found.title()} browser session")
            else:
                message = f"✓ {browser_found.title()} session ready"
                self.log_status(f"Successfully imported {selected_browser.title()} browser session")

            self.browser_status_label.configure(text=message, text_color="green")

            # Update downloader if it exists
            if self.downloader:
                self.downloader.set_browser(selected_browser)

            messagebox.showinfo(
                "Success",
                f"Browser session imported successfully!\n\nUsing: {browser_found.title()}\n\n"
                f"Make sure you're logged into Instagram in {browser_found.title()}."
            )
        else:
            # No browser session found
            if selected_browser == "auto":
                message = "⚠️ No browser sessions found"
                self.log_status("Could not find any browser sessions with Instagram cookies")
                messagebox.showwarning(
                    "No Browser Session Found",
                    "Could not find Instagram session in any browser.\n\n"
                    "Please:\n"
                    "1. Open Chrome, Firefox, Edge, or Safari\n"
                    "2. Login to Instagram (instagram.com)\n"
                    "3. Try importing again"
                )
            else:
                message = f"⚠️ {selected_browser.title()} session not found"
                self.log_status(f"Could not find {selected_browser.title()} session with Instagram cookies")
                messagebox.showwarning(
                    f"{selected_browser.title()} Session Not Found",
                    f"Could not find Instagram session in {selected_browser.title()}.\n\n"
                    f"Please:\n"
                    f"1. Open {selected_browser.title()}\n"
                    f"2. Login to Instagram (instagram.com)\n"
                    f"3. Keep {selected_browser.title()} open if using Chrome\n"
                    f"4. Try importing again"
                )

            self.browser_status_label.configure(text=message, text_color="orange")

    def _update_browser_import_error(self, error_msg, original_button_text):
        """Update UI after browser session test error."""
        self.import_browser_button.configure(text=original_button_text, state="normal")
        self.browser_status_label.configure(text="Error importing session", text_color="red")
        self.log_status(f"Error importing browser session: {error_msg}")
        messagebox.showerror(
            "Import Error",
            f"Error importing browser session:\n\n{error_msg}"
        )

    def start_processing(self):
        """Start the download and transcription process."""
        # Validate inputs
        if not self.excel_file_path:
            messagebox.showerror("Error", "Please select an Excel file")
            return

        if not os.path.exists(self.excel_file_path):
            messagebox.showerror("Error", "Selected Excel file does not exist")
            return

        # Reset state
        self.is_processing = True
        self.should_stop = False
        self.transcriptions = {}
        self.failed_items = []
        self.downloaded_count = 0
        self.transcribed_count = 0
        self.failed_count = 0

        # Update UI
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.export_button.configure(state="disabled")
        self.status_text.delete("1.0", "end")

        # Run processing in separate thread
        thread = threading.Thread(target=self.process_reels, daemon=True)
        thread.start()

    def stop_processing(self):
        """Stop the current processing."""
        self.should_stop = True
        self.log_status("Stopping... (current item will complete)")
        self.stop_button.configure(state="disabled")

    def process_reels(self):
        """Main processing logic (runs in separate thread)."""
        try:
            # Step 1: Read URLs from Excel
            self.update_current_task("Reading URLs from Excel...")
            column_name = self.column_entry.get() or settings.DEFAULT_EXCEL_COLUMN

            self.excel_handler = ExcelHandler(self.excel_file_path)
            self.urls = self.excel_handler.read_links_from_excel(column_name)

            self.total_items = len(self.urls)
            self.log_status(f"Found {self.total_items} URLs in Excel file")

            if self.total_items == 0:
                self.log_status("No URLs found in the specified column")
                self.finish_processing()
                return

            self.update_overall_progress(0, self.total_items)

            # Step 2: Initialize downloader
            self.update_current_task("Initializing Instagram downloader...")
            selected_browser = self.browser_var.get()
            self.downloader = InstagramDownloader(self.download_folder, selected_browser)
            self.downloader.setup_instaloader()
            self.log_status(f"Using browser: {selected_browser}")

            # Login if requested
            if self.login_var.get():
                username = self.username_entry.get()
                password = self.password_entry.get()

                if username and password:
                    self.update_current_task("Logging into Instagram...")
                    if self.downloader.login(username, password):
                        self.log_status("Successfully logged into Instagram")
                    else:
                        self.log_status("Login failed - continuing without authentication")
                else:
                    self.log_status("Username/password not provided - continuing without authentication")

            # Step 3: Initialize transcriber
            self.update_current_task("Loading Whisper model...")
            model_size = self.model_var.get()
            self.transcriber = WhisperTranscriber(model_size)

            # Log device info
            device_info = self.transcriber.get_model_info()
            self.log_status(f"Using device: {device_info['device_name']} ({device_info['device_type'].upper()})")
            self.log_status(f"Speed estimate: {device_info['speed_estimate']}")

            self.transcriber.load_model(progress_callback=self.log_status)

            # Step 4: Process each URL
            for idx, url in enumerate(self.urls, 1):
                if self.should_stop:
                    self.log_status("Processing stopped by user")
                    break

                self.log_status(f"\n--- Processing {idx}/{self.total_items}: {url} ---")

                # Download reel
                self.update_current_task(f"Downloading reel {idx}/{self.total_items}...")
                success, video_path, error = self.downloader.download_reel(
                    url,
                    progress_callback=self.log_status
                )

                if not success:
                    self.log_status(f"Download failed: {error}")
                    self.failed_items.append((url, f"Download failed: {error}"))
                    self.failed_count += 1
                    self.update_stats()
                    continue

                self.downloaded_count += 1
                self.update_stats()
                self.log_status(f"Downloaded: {video_path}")

                # Transcribe video
                self.update_current_task(f"Transcribing video {idx}/{self.total_items}...")
                success, transcription, _, error = self.transcriber.transcribe_video(
                    video_path,
                    progress_callback=self.log_status
                )

                if not success:
                    self.log_status(f"Transcription failed: {error}")
                    self.failed_items.append((url, f"Transcription failed: {error}"))
                    self.failed_count += 1
                else:
                    self.transcribed_count += 1
                    self.transcriptions[url] = transcription
                    self.log_status(f"Transcription: {transcription[:100]}...")

                self.update_stats()
                self.update_overall_progress(idx, self.total_items)

            # Step 5: Save results to Excel
            if self.transcriptions:
                self.update_current_task("Saving results to Excel...")
                output_path = self.excel_handler.write_transcriptions_to_excel(
                    self.transcriptions,
                    column_name=settings.DEFAULT_TRANSCRIPTION_COLUMN
                )
                self.log_status(f"\nResults saved to: {output_path}")

            # Step 6: Save failed items if any
            if self.failed_items and settings.ENABLE_EXPORT_FAILED:
                self.save_failed_items()

            self.log_status("\n=== Processing Complete ===")
            self.log_status(f"Successfully processed: {self.transcribed_count}/{self.total_items}")
            self.log_status(f"Failed: {self.failed_count}/{self.total_items}")

        except Exception as e:
            self.log_status(f"\nERROR: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

        finally:
            self.finish_processing()

    def save_failed_items(self):
        """Save failed items to a text file."""
        try:
            os.makedirs(os.path.dirname(settings.ERROR_LOG_PATH), exist_ok=True)
            with open(settings.ERROR_LOG_PATH, 'w') as f:
                f.write("Failed Instagram URLs\n")
                f.write("=" * 50 + "\n\n")
                for url, error in self.failed_items:
                    f.write(f"URL: {url}\n")
                    f.write(f"Error: {error}\n")
                    f.write("-" * 50 + "\n")
            self.log_status(f"Failed items saved to: {settings.ERROR_LOG_PATH}")
        except Exception as e:
            self.log_status(f"Could not save failed items: {str(e)}")

    def finish_processing(self):
        """Clean up after processing is complete."""
        self.is_processing = False
        self.update_current_task("Processing complete")

        # Update UI
        self.after(0, lambda: self.start_button.configure(state="normal"))
        self.after(0, lambda: self.stop_button.configure(state="disabled"))
        self.after(0, lambda: self.export_button.configure(state="normal"))

    def export_results(self):
        """Export current results to Excel."""
        if not self.excel_handler or not self.transcriptions:
            messagebox.showinfo("Info", "No results to export")
            return

        file_path = filedialog.asksaveasfilename(
            title="Save Results As",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )

        if file_path:
            try:
                self.excel_handler.write_transcriptions_to_excel(
                    self.transcriptions,
                    output_path=file_path
                )
                messagebox.showinfo("Success", f"Results exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export results:\n{str(e)}")

    # UI Update Methods (thread-safe)
    def log_status(self, message: str):
        """Add message to status log."""
        def update():
            self.status_text.insert("end", message + "\n")
            self.status_text.see("end")

        self.after(0, update)

    def update_current_task(self, task: str):
        """Update current task label."""
        self.after(0, lambda: self.current_task_label.configure(text=task))

    def update_overall_progress(self, current: int, total: int):
        """Update overall progress bar."""
        progress = current / total if total > 0 else 0

        def update():
            self.overall_progress.set(progress)
            self.overall_progress_label.configure(text=f"{current}/{total} items processed")

        self.after(0, update)

    def update_stats(self):
        """Update statistics labels."""
        def update():
            self.downloaded_label.configure(text=f"Downloaded: {self.downloaded_count}/{self.total_items}")
            self.transcribed_label.configure(text=f"Transcribed: {self.transcribed_count}/{self.total_items}")
            self.failed_label.configure(text=f"Failed: {self.failed_count}")

        self.after(0, update)


def main():
    """Main entry point for the GUI application."""
    app = InstagramTranscriberApp()
    app.mainloop()


if __name__ == "__main__":
    main()
