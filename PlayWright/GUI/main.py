import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk
from playwright.sync_api import sync_playwright
import phonenumbers
import threading
import time
import os

# ============================================
# Configuration
# ============================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILES_DIR = os.path.join(SCRIPT_DIR, "profiles")
PROFILE_NAME = "whatsapp_profile"
LOCALE = "en-US"
DELAY_BETWEEN_CHECKS = 2

# ============================================
# Theme Settings
# ============================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg_dark": "#1a1a2e",
    "bg_medium": "#16213e",
    "accent": "#0f3460",
    "primary": "#25D366",  # WhatsApp green
    "secondary": "#e94560",
    "success": "#00d26a",
    "error": "#ff4757",
    "text": "#eaeaea",
    "text_muted": "#a0a0a0"
}

def get_profile_path():
    return os.path.join(PROFILES_DIR, PROFILE_NAME)

def profile_exists():
    return os.path.exists(get_profile_path())

def extract_country_and_number(full_number):
    """Extract country code and local number using phonenumbers library."""
    clean = ''.join(filter(str.isdigit, full_number))
    if not full_number.startswith('+'):
        full_number = '+' + clean
    try:
        parsed = phonenumbers.parse(full_number, None)
        return str(parsed.country_code), str(parsed.national_number)
    except Exception:
        return clean[:2], clean[2:]

class PlaywrightGUIApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("WhatsApp Checker (FREE) - Elsakr Soft")
        self.geometry("850x700")
        self.minsize(750, 600)
        self.configure(fg_color=COLORS["bg_dark"])
        
        self.set_icon()
        
        # Variables
        self.is_running = False
        self.valid_numbers = []
        self.invalid_numbers = []
        
        self.create_widgets()
        self.load_numbers()
        self.update_profile_status()
        
    def set_icon(self):
        try:
            icon_path = os.path.join(SCRIPT_DIR, "assets", "fav.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass
    
    def create_widgets(self):
        # ========== Header ==========
        self.header_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_medium"], corner_radius=0)
        self.header_frame.pack(fill="x")
        
        try:
            logo_path = os.path.join(SCRIPT_DIR, "assets", "Sakr-logo.png")
            if os.path.exists(logo_path):
                logo_image = ctk.CTkImage(Image.open(logo_path), size=(80, 80))
                self.logo_label = ctk.CTkLabel(self.header_frame, image=logo_image, text="")
                self.logo_label.pack(pady=8)
        except Exception:
            pass
        
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="WhatsApp Numbers Checker (FREE)",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLORS["text"]
        )
        self.title_label.pack(pady=(0, 2))
        
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Powered by Playwright • No API Needed",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["primary"]
        )
        self.subtitle_label.pack(pady=(0, 8))
        
        # ========== Main Frame ==========
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=15)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # ========== Profile Status ==========
        self.profile_frame = ctk.CTkFrame(self.main_frame, fg_color=COLORS["bg_medium"], corner_radius=15)
        self.profile_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        self.profile_inner = ctk.CTkFrame(self.profile_frame, fg_color="transparent")
        self.profile_inner.pack(fill="x", padx=15, pady=10)
        
        self.profile_status_label = ctk.CTkLabel(
            self.profile_inner,
            text="🔒 Profile Status: Checking...",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text"]
        )
        self.profile_status_label.pack(side="left")
        
        self.login_button = ctk.CTkButton(
            self.profile_inner,
            text="🔐 Login to WhatsApp",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=35,
            fg_color=COLORS["secondary"],
            hover_color="#c73e54",
            command=self.start_login
        )
        self.login_button.pack(side="right")
        
        # ========== Numbers Section ==========
        self.numbers_frame = ctk.CTkFrame(self.main_frame, fg_color=COLORS["bg_medium"], corner_radius=15)
        self.numbers_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        
        self.numbers_header = ctk.CTkFrame(self.numbers_frame, fg_color="transparent")
        self.numbers_header.pack(fill="x", padx=15, pady=(10, 5))
        
        self.numbers_label = ctk.CTkLabel(
            self.numbers_header,
            text="📱 Phone Numbers (with country code)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text"]
        )
        self.numbers_label.pack(side="left")
        
        self.upload_btn = ctk.CTkButton(
            self.numbers_header,
            text="📁 Upload",
            font=ctk.CTkFont(size=12),
            width=80,
            height=28,
            fg_color=COLORS["accent"],
            command=self.upload_numbers
        )
        self.upload_btn.pack(side="right", padx=(5, 0))
        
        self.count_label = ctk.CTkLabel(
            self.numbers_header,
            text="0 numbers",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"]
        )
        self.count_label.pack(side="right")
        
        self.numbers_textbox = ctk.CTkTextbox(
            self.numbers_frame,
            font=ctk.CTkFont(size=13),
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["accent"],
            border_width=2,
            corner_radius=10,
            height=150
        )
        self.numbers_textbox.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        # ========== Control Buttons ==========
        self.buttons_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.buttons_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        self.start_button = ctk.CTkButton(
            self.buttons_frame,
            text="🚀 Start Checking",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=45,
            fg_color=COLORS["primary"],
            hover_color="#1da851",
            command=self.start_checking
        )
        self.start_button.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        self.clear_button = ctk.CTkButton(
            self.buttons_frame,
            text="🗑️ Clear",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=45,
            fg_color=COLORS["accent"],
            command=self.clear_all
        )
        self.clear_button.pack(side="right", expand=True, fill="x", padx=(5, 0))
        
        # ========== Progress Section ==========
        self.progress_frame = ctk.CTkFrame(self.main_frame, fg_color=COLORS["bg_medium"], corner_radius=15)
        self.progress_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="⚡ Ready to check numbers",
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
        
        # ========== Results ==========
        self.results_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.results_frame.grid(row=4, column=0, columnspan=2, sticky="ew")
        self.results_frame.grid_columnconfigure(0, weight=1)
        self.results_frame.grid_columnconfigure(1, weight=1)
        
        self.valid_button = ctk.CTkButton(
            self.results_frame,
            text="✅ On WhatsApp: 0",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            fg_color=COLORS["bg_medium"],
            hover_color="#1a4530",
            text_color=COLORS["success"],
            state="disabled",
            command=self.open_valid
        )
        self.valid_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        self.invalid_button = ctk.CTkButton(
            self.results_frame,
            text="❌ Not on WhatsApp: 0",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            fg_color=COLORS["bg_medium"],
            hover_color="#451a2e",
            text_color=COLORS["error"],
            state="disabled",
            command=self.open_invalid
        )
        self.invalid_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        # ========== Footer ==========
        self.footer = ctk.CTkFrame(self, fg_color=COLORS["bg_medium"], corner_radius=0)
        self.footer.pack(fill="x", side="bottom")
        
        self.footer_label = ctk.CTkLabel(
            self.footer,
            text="© Elsakr Soft | elsakr.company",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"]
        )
        self.footer_label.pack(pady=8)
    
    def update_profile_status(self):
        if profile_exists():
            self.profile_status_label.configure(
                text="✅ Profile found - Ready to check",
                text_color=COLORS["success"]
            )
            self.login_button.configure(text="🔄 Re-login")
        else:
            self.profile_status_label.configure(
                text="⚠️ No profile - Please login first",
                text_color=COLORS["error"]
            )
    
    def upload_numbers(self):
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
            except Exception as e:
                self.progress_label.configure(text=f"⚠️ Error: {str(e)}", text_color=COLORS["error"])
    
    def load_numbers(self):
        numbers_file = os.path.join(SCRIPT_DIR, "numbers.txt")
        if os.path.exists(numbers_file):
            try:
                with open(numbers_file, 'r') as f:
                    numbers = f.read().strip()
                if numbers:
                    self.numbers_textbox.insert("1.0", numbers)
                    count = len([n for n in numbers.split('\n') if n.strip()])
                    self.count_label.configure(text=f"{count} numbers")
            except Exception:
                pass
    
    def open_valid(self):
        valid_file = os.path.join(SCRIPT_DIR, "valid.txt")
        if os.path.exists(valid_file):
            os.startfile(valid_file)
    
    def open_invalid(self):
        invalid_file = os.path.join(SCRIPT_DIR, "invalid.txt")
        if os.path.exists(invalid_file):
            os.startfile(invalid_file)
    
    def clear_all(self):
        self.numbers_textbox.delete("1.0", "end")
        self.count_label.configure(text="0 numbers")
        self.valid_numbers = []
        self.invalid_numbers = []
        self.valid_button.configure(text="✅ On WhatsApp: 0", state="disabled")
        self.invalid_button.configure(text="❌ Not on WhatsApp: 0", state="disabled")
        self.progress_bar.set(0)
        self.progress_label.configure(text="⚡ Ready to check numbers", text_color=COLORS["text"])
    
    def start_login(self):
        if self.is_running:
            return
        
        self.is_running = True
        self.login_button.configure(state="disabled", text="⏳ Opening...")
        self.progress_label.configure(text="🔐 Opening browser for login...", text_color=COLORS["primary"])
        
        thread = threading.Thread(target=self.do_login, daemon=True)
        thread.start()
    
    def do_login(self):
        try:
            if not os.path.exists(PROFILES_DIR):
                os.makedirs(PROFILES_DIR)
            
            profile_path = get_profile_path()
            
            with sync_playwright() as p:
                context = p.firefox.launch_persistent_context(
                    user_data_dir=profile_path,
                    headless=False,
                    locale=LOCALE,
                    viewport={"width": 1280, "height": 800}
                )
                
                page = context.new_page()
                page.goto("https://web.whatsapp.com", wait_until="domcontentloaded")
                
                self.after(0, lambda: self.progress_label.configure(
                    text="📱 Scan QR code, then close Inspector to save",
                    text_color=COLORS["primary"]
                ))
                
                page.pause()
                context.close()
            
            self.after(0, self.login_complete)
            
        except Exception as e:
            self.after(0, lambda: self.progress_label.configure(
                text=f"⚠️ Login error: {str(e)[:40]}",
                text_color=COLORS["error"]
            ))
            self.after(0, lambda: self.login_button.configure(state="normal", text="🔐 Login to WhatsApp"))
            self.is_running = False
    
    def login_complete(self):
        self.is_running = False
        self.login_button.configure(state="normal", text="🔄 Re-login")
        self.progress_label.configure(text="✅ Login successful! Profile saved.", text_color=COLORS["success"])
        self.update_profile_status()
    
    def start_checking(self):
        if self.is_running:
            return
        
        if not profile_exists():
            self.progress_label.configure(text="⚠️ Please login first!", text_color=COLORS["error"])
            return
        
        numbers_text = self.numbers_textbox.get("1.0", "end").strip()
        if not numbers_text:
            self.progress_label.configure(text="⚠️ No numbers to check!", text_color=COLORS["error"])
            return
        
        # Save numbers to file
        numbers_file = os.path.join(SCRIPT_DIR, "numbers.txt")
        with open(numbers_file, 'w', encoding='utf-8') as f:
            f.write(numbers_text)
        
        self.valid_numbers = []
        self.invalid_numbers = []
        self.valid_button.configure(text="✅ On WhatsApp: 0", state="disabled")
        self.invalid_button.configure(text="❌ Not on WhatsApp: 0", state="disabled")
        self.progress_bar.set(0)
        
        self.is_running = True
        self.start_button.configure(state="disabled", text="⏳ Checking...")
        self.progress_label.configure(text="🚀 Opening browser...", text_color=COLORS["primary"])
        
        thread = threading.Thread(target=self.do_check, daemon=True)
        thread.start()
    
    def do_check(self):
        try:
            numbers_text = self.numbers_textbox.get("1.0", "end").strip()
            numbers = [n.strip() for n in numbers_text.split('\n') if n.strip()]
            
            if not numbers:
                return
            
            profile_path = get_profile_path()
            
            with sync_playwright() as p:
                context = p.firefox.launch_persistent_context(
                    user_data_dir=profile_path,
                    headless=False,
                    locale=LOCALE,
                    viewport={"width": 1280, "height": 800}
                )
                
                page = context.new_page()
                page.goto("https://web.whatsapp.com", wait_until="domcontentloaded")
                
                self.after(0, lambda: self.progress_label.configure(
                    text="⏳ Waiting for WhatsApp to load...",
                    text_color=COLORS["text"]
                ))
                
                # Wait for WhatsApp to load
                try:
                    page.get_by_role("button", name="Chats").click(timeout=30000)
                except:
                    self.after(0, lambda: self.progress_label.configure(
                        text="⚠️ WhatsApp didn't load. Please re-login.",
                        text_color=COLORS["error"]
                    ))
                    context.close()
                    self.after(0, self.checking_done)
                    return
                
                time.sleep(2)
                
                # Open Add Contact dialog
                try:
                    page.get_by_role("button", name="Add contact").click()
                    time.sleep(1)
                    page.get_by_role("textbox", name="First name").fill("Check")
                except Exception as e:
                    self.after(0, lambda: self.progress_label.configure(
                        text=f"⚠️ Could not open Add Contact",
                        text_color=COLORS["error"]
                    ))
                    context.close()
                    self.after(0, self.checking_done)
                    return
                
                # Check numbers
                current_country_code = None
                total = len(numbers)
                
                for i, number in enumerate(numbers, 1):
                    clean_number = ''.join(filter(str.isdigit, number))
                    if not clean_number:
                        continue
                    
                    country_code, local_number = extract_country_and_number(clean_number)
                    
                    try:
                        # Update country if needed
                        if country_code != current_country_code:
                            page.get_by_role("button", name="Country:").click()
                            time.sleep(0.3)
                            country_search = page.locator("#wa-popovers-bucket").get_by_role("textbox")
                            country_search.fill(country_code)
                            time.sleep(0.5)
                            page.locator("#wa-popovers-bucket").get_by_role("button").first.click()
                            time.sleep(0.3)
                            current_country_code = country_code
                        
                        # Fill phone number
                        phone_input = page.get_by_role("textbox", name="Phone number")
                        phone_input.press("ControlOrMeta+a")
                        phone_input.fill(local_number)
                        
                        time.sleep(DELAY_BETWEEN_CHECKS)
                        
                        # Check result
                        page_content = page.content()
                        
                        if "This phone number is on" in page_content:
                            self.valid_numbers.append(number)
                        else:
                            self.invalid_numbers.append(number)
                        
                    except Exception:
                        self.invalid_numbers.append(number)
                    
                    # Update UI
                    progress = i / total
                    self.after(0, lambda i=i, total=total, prog=progress: self.update_check_progress(i, total, prog))
                
                # Close dialog
                try:
                    page.keyboard.press("Escape")
                except:
                    pass
                
                context.close()
            
            self.after(0, self.checking_done)
            
        except Exception as e:
            self.after(0, lambda: self.progress_label.configure(
                text=f"⚠️ Error: {str(e)[:40]}",
                text_color=COLORS["error"]
            ))
            self.after(0, self.checking_done)
    
    def update_check_progress(self, current, total, progress):
        self.progress_bar.set(progress)
        self.progress_label.configure(
            text=f"Checking {current}/{total}...",
            text_color=COLORS["text"]
        )
        self.valid_button.configure(text=f"✅ On WhatsApp: {len(self.valid_numbers)}")
        self.invalid_button.configure(text=f"❌ Not on WhatsApp: {len(self.invalid_numbers)}")
    
    def checking_done(self):
        self.is_running = False
        self.start_button.configure(state="normal", text="🚀 Start Checking")
        
        if self.valid_numbers or self.invalid_numbers:
            self.progress_label.configure(
                text=f"✅ Complete! Click results to open files.",
                text_color=COLORS["success"]
            )
            self.valid_button.configure(state="normal")
            self.invalid_button.configure(state="normal")
            self.save_results()
    
    def save_results(self):
        try:
            valid_file = os.path.join(SCRIPT_DIR, "valid.txt")
            invalid_file = os.path.join(SCRIPT_DIR, "invalid.txt")
            
            with open(valid_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.valid_numbers))
            
            with open(invalid_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.invalid_numbers))
        except Exception:
            pass

if __name__ == "__main__":
    app = PlaywrightGUIApp()
    app.mainloop()
