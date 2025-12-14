from playwright.sync_api import sync_playwright
from colorama import Fore, init
import random
import time
import re
import os

init(autoreset=True)

# ============================================
# Configuration
# ============================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILES_DIR = os.path.join(SCRIPT_DIR, "profiles")
PROFILE_NAME = "whatsapp_profile"
LOCALE = "en-US"
DELAY_BETWEEN_CHECKS = 2

# ============================================
# Colors for terminal
# ============================================
logo_colors = [Fore.BLUE, Fore.CYAN, Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX, 
               Fore.LIGHTMAGENTA_EX, Fore.LIGHTYELLOW_EX, Fore.MAGENTA, 
               Fore.YELLOW, Fore.GREEN, Fore.LIGHTGREEN_EX]

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def intro():
    clear_screen()
    color = random.choice(logo_colors)
    print(color + r"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║     ██╗    ██╗██╗  ██╗ █████╗ ████████╗███████╗ █████╗ ██████╗║
    ║     ██║    ██║██║  ██║██╔══██╗╚══██╔══╝██╔════╝██╔══██╗██╔══██║
    ║     ██║ █╗ ██║███████║███████║   ██║   ███████╗███████║██████╔║
    ║     ██║███╗██║██╔══██║██╔══██║   ██║   ╚════██║██╔══██║██╔═══╝║
    ║     ╚███╔███╔╝██║  ██║██║  ██║   ██║   ███████║██║  ██║██║    ║
    ║      ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝    ║
    ║                                                               ║
    ║        WhatsApp Numbers Checker - FREE (Playwright)          ║
    ║                   Powered by Elsakr Soft                      ║
    ║                   https://elsakr.company                      ║
    ╚═══════════════════════════════════════════════════════════════╝
    """ + Fore.RESET)

def get_profile_path():
    return os.path.join(PROFILES_DIR, PROFILE_NAME)

def profile_exists():
    return os.path.exists(get_profile_path())

def show_menu():
    print(Fore.CYAN + "\n    Choose an option:" + Fore.RESET)
    print(Fore.YELLOW + "    [1] " + Fore.WHITE + "Login to WhatsApp (First Time Setup)" + Fore.RESET)
    print(Fore.YELLOW + "    [2] " + Fore.WHITE + "Start Checking Numbers" + Fore.RESET)
    print(Fore.YELLOW + "    [0] " + Fore.WHITE + "Exit" + Fore.RESET)
    print()
    choice = input(Fore.GREEN + "    Enter your choice: " + Fore.RESET).strip()
    return choice

import phonenumbers

def extract_country_and_number(full_number):
    """
    Extract country code and local number using phonenumbers library.
    Supports ALL countries automatically.
    """
    clean = ''.join(filter(str.isdigit, full_number))
    
    # Add + prefix if not present
    if not full_number.startswith('+'):
        full_number = '+' + clean
    
    try:
        parsed = phonenumbers.parse(full_number, None)
        country_code = str(parsed.country_code)
        national_number = str(parsed.national_number)
        return country_code, national_number
    except Exception:
        # Fallback: assume first 2 digits are country code
        return clean[:2], clean[2:]

def option_login():
    """Option 1: Create profile and login to WhatsApp"""
    print(Fore.YELLOW + "\n[*] Creating browser profile..." + Fore.RESET)
    
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
        
        print(Fore.YELLOW + "[*] Opening WhatsApp Web..." + Fore.RESET)
        page.goto("https://web.whatsapp.com", wait_until="domcontentloaded")
        
        print(Fore.CYAN + "\n" + "="*55 + Fore.RESET)
        print(Fore.GREEN + "[!] Browser opened with Playwright Inspector" + Fore.RESET)
        print(Fore.YELLOW + "[!] Scan the QR code with your WhatsApp app" + Fore.RESET)
        print(Fore.YELLOW + "[!] After login, close the Inspector to save profile" + Fore.RESET)
        print(Fore.CYAN + "="*55 + Fore.RESET)
        
        page.pause()
        
        context.close()
    
    print(Fore.GREEN + "\n[✓] Profile saved successfully!" + Fore.RESET)
    print(Fore.CYAN + "[i] You can now use Option 2 to check numbers" + Fore.RESET)

def option_check_numbers():
    """Option 2: Check numbers using existing profile"""
    
    if not profile_exists():
        print(Fore.RED + "\n[!] No profile found!" + Fore.RESET)
        print(Fore.YELLOW + "[i] Please use Option 1 to login first" + Fore.RESET)
        return
    
    numbers = load_numbers()
    if not numbers:
        print(Fore.RED + "\n[!] No numbers to check. Add numbers to numbers.txt" + Fore.RESET)
        return
    
    print(Fore.GREEN + f"\n[✓] Loaded {len(numbers)} numbers to check" + Fore.RESET)
    print(Fore.GREEN + f"[✓] Using existing profile" + Fore.RESET)
    
    valid_numbers = []
    invalid_numbers = []
    
    print(Fore.YELLOW + "\n[*] Starting browser..." + Fore.RESET)
    
    profile_path = get_profile_path()
    
    with sync_playwright() as p:
        context = p.firefox.launch_persistent_context(
            user_data_dir=profile_path,
            headless=False,
            locale=LOCALE,
            viewport={"width": 1280, "height": 800}
        )
        
        page = context.new_page()
        
        print(Fore.YELLOW + "[*] Opening WhatsApp Web..." + Fore.RESET)
        page.goto("https://web.whatsapp.com", wait_until="domcontentloaded")
        
        print(Fore.YELLOW + "[*] Waiting for WhatsApp to load..." + Fore.RESET)
        try:
            page.get_by_role("button", name="Chats").click(timeout=30000)
            print(Fore.GREEN + "[✓] WhatsApp loaded!" + Fore.RESET)
        except:
            print(Fore.RED + "[!] WhatsApp didn't load. Profile may be expired." + Fore.RESET)
            print(Fore.YELLOW + "[i] Please use Option 1 to login again" + Fore.RESET)
            context.close()
            return
        
        time.sleep(2)
        
        # Open Add Contact dialog ONCE
        print(Fore.YELLOW + "[*] Opening Add Contact dialog..." + Fore.RESET)
        try:
            page.get_by_role("button", name="Add contact").click()
            time.sleep(1)
            
            # Fill dummy name
            page.get_by_role("textbox", name="First name").fill("Check")
            
            print(Fore.GREEN + "[✓] Add Contact dialog ready!" + Fore.RESET)
        except Exception as e:
            print(Fore.RED + f"[!] Could not open Add Contact: {str(e)[:40]}" + Fore.RESET)
            context.close()
            return
        
        print(Fore.CYAN + f"\n[*] Starting to check {len(numbers)} numbers...\n" + Fore.RESET)
        
        current_country_code = None
        
        for i, number in enumerate(numbers, 1):
            clean_number = ''.join(filter(str.isdigit, number))
            if not clean_number:
                continue
            
            country_code, local_number = extract_country_and_number(clean_number)
            
            print(Fore.WHITE + f"[{i}/{len(numbers)}] Checking +{country_code} {local_number}..." + Fore.RESET, end=" ")
            
            try:
                # If country code changed, update it
                if country_code != current_country_code:
                    # Click country button
                    page.get_by_role("button", name="Country:").click()
                    time.sleep(0.3)
                    
                    # Search for country by code
                    country_search = page.locator("#wa-popovers-bucket").get_by_role("textbox")
                    country_search.fill(country_code)
                    time.sleep(0.5)
                    
                    # Click first result (the flag button)
                    page.locator("#wa-popovers-bucket").get_by_role("button").first.click()
                    time.sleep(0.3)
                    
                    current_country_code = country_code
                
                # Fill phone number
                phone_input = page.get_by_role("textbox", name="Phone number")
                phone_input.press("ControlOrMeta+a")
                phone_input.fill(local_number)
                
                # Wait for result
                time.sleep(DELAY_BETWEEN_CHECKS)
                
                # Check result
                page_content = page.content()
                
                if "This phone number is on" in page_content:
                    print(Fore.GREEN + "✓ ON WHATSAPP" + Fore.RESET)
                    valid_numbers.append(number)
                elif "This phone number is not on" in page_content:
                    print(Fore.RED + "✗ NOT ON WHATSAPP" + Fore.RESET)
                    invalid_numbers.append(number)
                else:
                    print(Fore.YELLOW + "? UNKNOWN" + Fore.RESET)
                    invalid_numbers.append(number)
                
            except Exception as e:
                print(Fore.YELLOW + f"⚠ ERROR: {str(e)[:30]}" + Fore.RESET)
                invalid_numbers.append(number)
        
        # Close dialog
        try:
            page.keyboard.press("Escape")
        except:
            pass
        
        context.close()
    
    save_results(valid_numbers, invalid_numbers)
    
    print(Fore.CYAN + "\n" + "="*50 + Fore.RESET)
    print(Fore.GREEN + f"[✓] On WhatsApp: {len(valid_numbers)}" + Fore.RESET)
    print(Fore.RED + f"[✗] Not on WhatsApp: {len(invalid_numbers)}" + Fore.RESET)
    print(Fore.CYAN + "="*50 + Fore.RESET)
    print(Fore.YELLOW + "\n[i] Results saved to valid.txt and invalid.txt" + Fore.RESET)

def load_numbers():
    """Load numbers from numbers.txt"""
    numbers_file = os.path.join(SCRIPT_DIR, "numbers.txt")
    if not os.path.exists(numbers_file):
        print(Fore.RED + f"[!] Error: '{numbers_file}' not found!" + Fore.RESET)
        return []
    
    with open(numbers_file, 'r', encoding='utf-8') as f:
        numbers = [line.strip() for line in f if line.strip()]
    
    return numbers

def save_results(valid_numbers, invalid_numbers):
    """Save results to files"""
    valid_file = os.path.join(SCRIPT_DIR, "valid.txt")
    invalid_file = os.path.join(SCRIPT_DIR, "invalid.txt")
    
    with open(valid_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(valid_numbers))
    
    with open(invalid_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(invalid_numbers))

def main():
    while True:
        intro()
        
        if profile_exists():
            print(Fore.GREEN + "    [✓] Profile found - Ready to check numbers" + Fore.RESET)
        else:
            print(Fore.YELLOW + "    [!] No profile - Please login first (Option 1)" + Fore.RESET)
        
        choice = show_menu()
        
        if choice == "1":
            option_login()
            input("\nPress Enter to continue...")
        elif choice == "2":
            option_check_numbers()
            input("\nPress Enter to continue...")
        elif choice == "0":
            print(Fore.CYAN + "\nGoodbye! 👋" + Fore.RESET)
            break
        else:
            print(Fore.RED + "\n[!] Invalid choice!" + Fore.RESET)
            time.sleep(1)

if __name__ == "__main__":
    main()
