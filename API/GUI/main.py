import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk
import requests
import threading
import os
import sys
import subprocess

# ============================================
# Configuration
# ============================================
BASE_URL = "https://wasenderapi.com/api"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================
# Theme Settings
# ============================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Custom Colors
COLORS = {
    "bg_dark": "#1a1a2e",
    "bg_medium": "#16213e",
    "accent": "#0f3460",
    "primary": "#e94560",
    "success": "#00d26a",
    "error": "#ff4757",
    "text": "#eaeaea",
    "text_muted": "#a0a0a0"
}

class WhatsAppCheckerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window Configuration
        self.title("WhatsApp Numbers Checker - Elsakr Soft")
        self.geometry("800x650")
        self.minsize(700, 550)
        self.configure(fg_color=COLORS["bg_dark"])
        
        # Set window icon
        self.set_icon()
        
        # Variables
        self.is_checking = False
        self.check_completed = False  # Track if checking finished
        self.valid_numbers = []
        self.invalid_numbers = []
        self.api_key = ""
        
        # Load API Key from file
        self.load_api_key()
        
        # Build UI
        self.create_widgets()
        self.load_numbers()
        
    def set_icon(self):
        """Set window icon using .ico file"""
        try:
            icon_path = os.path.join(SCRIPT_DIR, "assets", "fav.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception as e:
            print(f"Icon error: {e}")
    
    def create_widgets(self):
        """Create all UI components"""
        
        # ========== Header Frame ==========
        self.header_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_medium"], corner_radius=0)
        self.header_frame.pack(fill="x", padx=0, pady=0)
        
        # Logo
        try:
            logo_path = os.path.join(SCRIPT_DIR, "assets", "Sakr-logo.png")
            if os.path.exists(logo_path):
                logo_image = ctk.CTkImage(Image.open(logo_path), size=(100, 100))
                self.logo_label = ctk.CTkLabel(self.header_frame, image=logo_image, text="")
                self.logo_label.pack(pady=10)
        except Exception:
            pass
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="WhatsApp Numbers Checker",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text"]
        )
        self.title_label.pack(pady=(0, 3))
        
        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Powered by Elsakr Soft",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"]
        )
        self.subtitle_label.pack(pady=(0, 10))
        
        # ========== Main Content Frame ==========
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Configure grid - numbers section should expand
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)  # Numbers section expands
        
        # ========== Numbers Input Section ==========
        self.numbers_frame = ctk.CTkFrame(self.main_frame, fg_color=COLORS["bg_medium"], corner_radius=15)
        self.numbers_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        
        # Numbers header with label and upload button
        self.numbers_header = ctk.CTkFrame(self.numbers_frame, fg_color="transparent")
        self.numbers_header.pack(fill="x", padx=15, pady=(10, 5))
        
        self.numbers_label = ctk.CTkLabel(
            self.numbers_header,
            text="📱 Phone Numbers",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text"]
        )
        self.numbers_label.pack(side="left")
        
        self.upload_numbers_btn = ctk.CTkButton(
            self.numbers_header,
            text="📁 Upload",
            font=ctk.CTkFont(size=12),
            width=80,
            height=28,
            fg_color=COLORS["accent"],
            hover_color="#1a4a7a",
            command=self.upload_numbers_file
        )
        self.upload_numbers_btn.pack(side="right", padx=(5, 0))
        
        self.count_label = ctk.CTkLabel(
            self.numbers_header,
            text="0 numbers",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"]
        )
        self.count_label.pack(side="right")
        
        # Numbers textbox - make it expand properly
        self.numbers_textbox = ctk.CTkTextbox(
            self.numbers_frame,
            font=ctk.CTkFont(size=13),
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["accent"],
            border_width=2,
            corner_radius=10,
            height=200
        )
        self.numbers_textbox.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        # ========== Control Buttons ==========
        self.buttons_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.buttons_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        self.start_button = ctk.CTkButton(
            self.buttons_frame,
            text="🚀 Start Checking",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=45,
            fg_color=COLORS["primary"],
            hover_color="#c73e54",
            command=self.start_checking
        )
        self.start_button.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        self.clear_button = ctk.CTkButton(
            self.buttons_frame,
            text="🗑️ Clear All",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=45,
            fg_color=COLORS["accent"],
            hover_color="#1a4a7a",
            command=self.clear_all
        )
        self.clear_button.pack(side="right", expand=True, fill="x", padx=(5, 0))
        
        # ========== Progress Section ==========
        self.progress_frame = ctk.CTkFrame(self.main_frame, fg_color=COLORS["bg_medium"], corner_radius=15)
        self.progress_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="Ready to check...",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text"]
        )
        self.progress_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            height=12,
            corner_radius=6,
            fg_color=COLORS["bg_dark"],
            progress_color=COLORS["primary"]
        )
        self.progress_bar.pack(fill="x", padx=15, pady=(0, 10))
        self.progress_bar.set(0)
        
        # ========== Results Section ==========
        self.results_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.results_frame.grid(row=3, column=0, columnspan=2, sticky="ew")
        self.results_frame.grid_columnconfigure(0, weight=1)
        self.results_frame.grid_columnconfigure(1, weight=1)
        
        # Valid Results Button
        self.valid_button = ctk.CTkButton(
            self.results_frame,
            text="✅ Valid: 0",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=60,
            fg_color=COLORS["bg_medium"],
            hover_color="#1a3a2e",
            text_color=COLORS["success"],
            state="disabled",
            command=self.open_valid_file
        )
        self.valid_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Invalid Results Button
        self.invalid_button = ctk.CTkButton(
            self.results_frame,
            text="❌ Invalid: 0",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=60,
            fg_color=COLORS["bg_medium"],
            hover_color="#3a1a2e",
            text_color=COLORS["error"],
            state="disabled",
            command=self.open_invalid_file
        )
        self.invalid_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        # ========== Footer ==========
        self.footer_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_medium"], corner_radius=0)
        self.footer_frame.pack(fill="x", side="bottom")
        
        self.footer_label = ctk.CTkLabel(
            self.footer_frame,
            text="© Elsakr Soft | elsakr.company",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"],
            cursor="hand2"
        )
        self.footer_label.pack(pady=8)
        self.footer_label.bind("<Button-1>", lambda e: self.open_url("https://elsakr.company"))
    
    def open_url(self, url):
        """Open URL in browser"""
        import webbrowser
        webbrowser.open(url)
    
    def upload_numbers_file(self):
        """Open file dialog to upload numbers.txt"""
        file_path = filedialog.askopenfilename(
            title="Select Numbers File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    numbers = f.read().strip()
                if numbers:
                    self.numbers_textbox.delete("1.0", "end")
                    self.numbers_textbox.insert("1.0", numbers)
                    count = len([n for n in numbers.split('\n') if n.strip()])
                    self.count_label.configure(text=f"{count} numbers")
                    self.progress_label.configure(text=f"📂 Loaded {count} numbers from file")
            except Exception as e:
                self.progress_label.configure(text=f"⚠️ Error loading file: {str(e)}", text_color=COLORS["error"])
    
    def upload_api_file(self):
        """Open file dialog to upload api.txt"""
        file_path = filedialog.askopenfilename(
            title="Select API Key File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.api_key = f.read().strip()
                if self.api_key:
                    # Save to local api.txt
                    api_file = os.path.join(SCRIPT_DIR, "api.txt")
                    with open(api_file, 'w') as f:
                        f.write(self.api_key)
                    self.progress_label.configure(text="🔑 API key loaded successfully!", text_color=COLORS["success"])
                    return True
            except Exception as e:
                self.progress_label.configure(text=f"⚠️ Error loading API key: {str(e)}", text_color=COLORS["error"])
        return False
    
    def open_valid_file(self):
        """Open valid.txt file"""
        valid_file = os.path.join(SCRIPT_DIR, "valid.txt")
        if os.path.exists(valid_file):
            if sys.platform == 'win32':
                os.startfile(valid_file)
            else:
                subprocess.run(['xdg-open', valid_file])
    
    def open_invalid_file(self):
        """Open invalid.txt file"""
        invalid_file = os.path.join(SCRIPT_DIR, "invalid.txt")
        if os.path.exists(invalid_file):
            if sys.platform == 'win32':
                os.startfile(invalid_file)
            else:
                subprocess.run(['xdg-open', invalid_file])
    
    def load_api_key(self):
        """Load API key from api.txt"""
        api_file = os.path.join(SCRIPT_DIR, "api.txt")
        if os.path.exists(api_file):
            try:
                with open(api_file, 'r') as f:
                    self.api_key = f.read().strip()
            except Exception:
                pass
    
    def load_numbers(self):
        """Load numbers from numbers.txt if exists"""
        numbers_file = os.path.join(SCRIPT_DIR, "numbers.txt")
        if os.path.exists(numbers_file):
            try:
                with open(numbers_file, 'r') as f:
                    numbers = f.read().strip()
                    if numbers:
                        self.numbers_textbox.insert("1.0", numbers)
                        count = len([n for n in numbers.split('\n') if n.strip()])
                        self.count_label.configure(text=f"{count} numbers")
                        self.progress_label.configure(text=f"📂 Loaded {count} numbers from numbers.txt")
            except Exception:
                pass
    
    def clear_all(self):
        """Clear all inputs and results"""
        self.numbers_textbox.delete("1.0", "end")
        self.valid_numbers = []
        self.invalid_numbers = []
        self.check_completed = False
        self.valid_button.configure(text="✅ Valid: 0", state="disabled")
        self.invalid_button.configure(text="❌ Invalid: 0", state="disabled")
        self.progress_bar.set(0)
        self.progress_label.configure(text="Ready to check...", text_color=COLORS["text"])
        self.count_label.configure(text="0 numbers")
    
    def start_checking(self):
        """Start checking numbers in a background thread"""
        if self.is_checking:
            return
        
        # Check API key - prompt upload if missing
        if not self.api_key:
            self.progress_label.configure(text="⚠️ API key not found! Please select api.txt file.", text_color=COLORS["error"])
            if not self.upload_api_file():
                return
        
        numbers_text = self.numbers_textbox.get("1.0", "end").strip()
        if not numbers_text:
            self.progress_label.configure(text="⚠️ No numbers! Please upload numbers file.", text_color=COLORS["error"])
            self.upload_numbers_file()
            numbers_text = self.numbers_textbox.get("1.0", "end").strip()
            if not numbers_text:
                return
        
        numbers = [n.strip() for n in numbers_text.split('\n') if n.strip()]
        if not numbers:
            self.progress_label.configure(text="⚠️ No valid numbers found!", text_color=COLORS["error"])
            return
        
        # Reset results
        self.valid_numbers = []
        self.invalid_numbers = []
        self.check_completed = False
        self.valid_button.configure(text="✅ Valid: 0", state="disabled")
        self.invalid_button.configure(text="❌ Invalid: 0", state="disabled")
        self.progress_bar.set(0)
        
        # Start checking in background thread
        self.is_checking = True
        self.start_button.configure(state="disabled", text="⏳ Checking...")
        thread = threading.Thread(target=self.check_numbers, args=(numbers,), daemon=True)
        thread.start()
    
    def check_numbers(self, numbers):
        """Check numbers against WASenderAPI"""
        total = len(numbers)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        for i, number in enumerate(numbers):
            try:
                url = f"{BASE_URL}/on-whatsapp/{number}"
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    result_data = data.get('data', data)
                    is_valid = result_data.get('exists', False) if isinstance(result_data, dict) else False
                    
                    if is_valid:
                        self.valid_numbers.append(number)
                    else:
                        self.invalid_numbers.append(number)
                elif response.status_code == 401:
                    # API key is invalid
                    self.after(0, lambda: self.progress_label.configure(
                        text="⚠️ Invalid API key! Please upload correct api.txt",
                        text_color=COLORS["error"]
                    ))
                    self.after(0, self.upload_api_file)
                    break
                else:
                    self.invalid_numbers.append(number)
                    
            except Exception:
                self.invalid_numbers.append(number)
            
            # Update UI (thread-safe)
            progress = (i + 1) / total
            self.after(0, self.update_progress, i + 1, total, progress)
        
        # Finished
        self.after(0, self.checking_finished)
    
    def update_progress(self, current, total, progress):
        """Update progress bar and labels"""
        self.progress_bar.set(progress)
        self.progress_label.configure(
            text=f"Checking {current}/{total}...",
            text_color=COLORS["text"]
        )
        self.valid_button.configure(text=f"✅ Valid: {len(self.valid_numbers)}")
        self.invalid_button.configure(text=f"❌ Invalid: {len(self.invalid_numbers)}")
    
    def checking_finished(self):
        """Called when checking is complete"""
        self.is_checking = False
        self.check_completed = True
        self.start_button.configure(state="normal", text="🚀 Start Checking")
        self.progress_label.configure(
            text=f"✅ Complete! Click results to open files.",
            text_color=COLORS["success"]
        )
        
        # Enable result buttons
        self.valid_button.configure(state="normal")
        self.invalid_button.configure(state="normal")
        
        # Save results to files
        self.save_results()
    
    def save_results(self):
        """Save results to valid.txt and invalid.txt"""
        try:
            valid_file = os.path.join(SCRIPT_DIR, "valid.txt")
            invalid_file = os.path.join(SCRIPT_DIR, "invalid.txt")
            
            with open(valid_file, 'w') as f:
                f.write('\n'.join(self.valid_numbers))
            
            with open(invalid_file, 'w') as f:
                f.write('\n'.join(self.invalid_numbers))
        except Exception as e:
            self.progress_label.configure(
                text=f"⚠️ Error saving results: {str(e)}",
                text_color=COLORS["error"]
            )

if __name__ == "__main__":
    app = WhatsAppCheckerApp()
    app.mainloop()
