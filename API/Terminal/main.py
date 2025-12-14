import requests
import time
import os
import sys
import random
from colorama import Fore, init

# Hardcoded Base URL
BASE_URL = "https://wasenderapi.com/api"

# Initialize colorama
init(autoreset=True)

logo_colors = [
    Fore.BLUE, Fore.CYAN, Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX,
    Fore.LIGHTMAGENTA_EX, Fore.LIGHTYELLOW_EX, Fore.MAGENTA,
    Fore.YELLOW, Fore.GREEN, Fore.LIGHTGREEN_EX, Fore.RED, Fore.LIGHTRED_EX
]

def get_api_key():
    """Reads the API Key from api.txt"""
    api_file = "api.txt"
    if not os.path.exists(api_file):
        print(Fore.RED + f"Error: '{api_file}' not found.")
        print(Fore.YELLOW + "Please create 'api.txt' and paste your API Key inside it.")
        input("Press Enter to exit...")
        sys.exit()
        
    try:
        with open(api_file, 'r') as f:
            key = f.read().strip()
            if not key:
                print(Fore.RED + "Error: API Key is empty in 'api.txt'.")
                input("Press Enter to exit...")
                sys.exit()
            return key
    except Exception as e:
        print(Fore.RED + f"Error reading 'api.txt': {e}")
        sys.exit()

def intro():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(random.choice(logo_colors)+"\t\t\t                            .-==========" + Fore.RESET)
    print(random.choice(logo_colors)+"\t\t\t                         .-' O    =====" + Fore.RESET)
    print(random.choice(logo_colors)+"\t\t\t                        /___       ===" + Fore.RESET)
    print(random.choice(logo_colors)+"\t\t\t                           \_      |" + Fore.RESET)
    print(random.choice(logo_colors)+"\t\t\t_____________________________)    (_____________________________" + Fore.RESET)
    print(random.choice(logo_colors)+"\t\t\t\\___________               .'      `,              ____________/" + Fore.RESET)
    print(random.choice(logo_colors)+"\t\t\t  \\__________`.     |||<   `.      .'   >|||     .'__________/" + Fore.RESET)
    print(random.choice(logo_colors)+"\t\t\t     \\_________`._  |||  <   `-..-'   >  |||  _.'_________/" + Fore.RESET)
    print(random.choice(logo_colors)+"\t\t\t        \\_________`-..|_  _ <      > _  _|..-'_________/" + Fore.RESET)
    print(random.choice(logo_colors)+"\t\t\t           \\_________   |_|  //  \\  |_|   _________/" + Fore.RESET)
    print(random.choice(logo_colors)+"\t\t\t                      .-\   //    \\   /-." + Fore.RESET)
    print(random.choice(logo_colors)+"\t\t\t      ,  .         _.'.- `._        _.' -.`._         .  ," + Fore.RESET)
    print(random.choice(logo_colors)+"\t\t\t    <<<<>>>>     .' .'  /  '``----''`  \  `. `.     <<<<>>>>" + Fore.RESET)
    print(random.choice(logo_colors)+"\t\t\t      '/\\`         /  .' .'.'/|..|\\'.'.`. \\           '/\\`" + Fore.RESET)
    print(random.choice(logo_colors)+"\t\t\t      (())        `  /  / .'| |||| |`. \\  \\  '        (())" + Fore.RESET)
    print(random.choice(logo_colors)+"\t\t\t       /\\          ::_.' .' /| || |\\ `. `._::          /\\" + Fore.RESET)
    print(random.choice(logo_colors)+"\t\t\t      //\\\\           '``.' | | || | | `.''`           //\\\\" + Fore.RESET)
    print(random.choice(logo_colors)+"\t\t\t      //\\\\             .` .` | || | '. '.             //\\\\" + Fore.RESET)
    print(random.choice(logo_colors)+"\t\t\t      //\\\\                `  | `' |  '                //\\\\" + Fore.RESET)
    print(random.choice(logo_colors)+"\t\t\t      \\\\//                                            \\\\//" + Fore.RESET)
    print(random.choice(logo_colors)+"\t\t\t       \\/                   Elsakr                      \\/" + Fore.RESET)
    print(random.choice(logo_colors)+"\t\t\t       \\/           https://elsakr.company             \\/" + Fore.RESET)
    print(random.choice(logo_colors)+"\t\t\t       \\/           Whatsapp Numbers Checker           \\/" + Fore.RESET)
    time.sleep(2)
    os.system('cls' if os.name == 'nt' else 'clear')

def check_numbers(input_file, valid_file, invalid_file):
    """
    Reads numbers from input_file, checks them against WASenderAPI,
    and sorts them into valid_file and invalid_file using WASenderAPI.
    """
    
    api_key = get_api_key()
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(Fore.RED + f"Error: Input file '{input_file}' not found.")
        print(Fore.YELLOW + f"Please create '{input_file}' and add numbers to check.")
        return

    # Open files
    try:
        with open(input_file, 'r') as f_in:
            numbers = [line.strip() for line in f_in if line.strip()]
    except Exception as e:
        print(Fore.RED + f"Error reading input file: {e}")
        return

    print(Fore.CYAN + f"Found {len(numbers)} numbers to check.")
    print(Fore.YELLOW + "--------------------------------------------------")

    # Prepare output files
    with open(valid_file, 'w') as f: pass
    with open(invalid_file, 'w') as f: pass

    # Headers for API request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    count = 0
    valid_count = 0
    invalid_count = 0

    for number in numbers:
        count += 1
        print(Fore.CYAN + f"[{count}/{len(numbers)}] Checking {number}...", end='', flush=True)

        url = f"{BASE_URL}/on-whatsapp/{number}"
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                is_valid = False
                if isinstance(data, dict):
                    result_data = data.get('data', data) 
                    
                    if isinstance(result_data, dict):
                         if 'exists' in result_data:
                            is_valid = result_data['exists']
                         elif 'on_whatsapp' in result_data:
                            is_valid = result_data['on_whatsapp']
                    
                    if not is_valid and 'exists' in data:
                        is_valid = data['exists']
                
                if is_valid:
                    print(Fore.GREEN + " VALID ✓")
                    with open(valid_file, 'a') as f_valid:
                        f_valid.write(f"{number}\n")
                    valid_count += 1
                else:
                    print(Fore.RED + " NOT FOUND ✗")
                    with open(invalid_file, 'a') as f_invalid:
                        f_invalid.write(f"{number}\n")
                    invalid_count += 1

            else:
                print(Fore.RED + f" Error: {response.status_code}")
                with open(invalid_file, 'a') as f_invalid:
                    f_invalid.write(f"{number} (API Error {response.status_code})\n")
                invalid_count += 1

        except Exception as e:
            print(Fore.RED + f" Exception: {e}")
            with open(invalid_file, 'a') as f_invalid:
                f_invalid.write(f"{number} (Script Error)\n")
            invalid_count += 1

        time.sleep(0.5)

    print(Fore.MAGENTA + "\n=============================================")
    print(Fore.GREEN + f" Done! Total checked: {len(numbers)}")
    print(Fore.GREEN + f" Valid: {valid_count} (Saved to {valid_file})")
    print(Fore.RED + f" Invalid: {invalid_count} (Saved to {invalid_file})")
    print(Fore.MAGENTA + "=============================================")
    
    print(Fore.YELLOW + "\nPress Enter to Exit")
    input(">>> ")

if __name__ == "__main__":
    intro()
    # File names
    INPUT_FILE = "numbers.txt"
    VALID_FILE = "valid.txt"
    INVALID_FILE = "invalid.txt"

    check_numbers(INPUT_FILE, VALID_FILE, INVALID_FILE)
