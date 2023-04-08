import requests, yaml
from threading import Thread, Lock
from colorama import Fore,init 
init(autoreset=True,convert=True)
config = yaml.safe_load(open("config.yml"))
print_lock = Lock()
def lprint(text):
    with print_lock:
        print(text)
class colors:
    r = Fore.RESET
    cyan = Fore.CYAN; lcyan = Fore.LIGHTCYAN_EX
    blue = Fore.BLUE; lblue = Fore.LIGHTBLUE_EX
    green = Fore.GREEN; lgreen = Fore.LIGHTGREEN_EX
    red = Fore.RED; lred = Fore.LIGHTRED_EX
    yellow = Fore.YELLOW; lyellow = Fore.LIGHTYELLOW_EX
class console:
    def input(text):
        content = input(f"({colors.lcyan}@{colors.r}) {colors.lcyan}{text}{colors.r} >> {colors.cyan}")
        print(colors.r,end="\r")
        return content
    def success(text,content=None):
        lprint(
            f"({colors.lgreen}+{colors.r}) {text}{colors.lgreen+': '+colors.r+content if content else ''}"
        )
    def failed(text,content=None):
        lprint(
            f"({colors.lred}-{colors.r}) {text}{colors.lred+': '+colors.r+content if content else ''}"
        )
    def information(text,content=None):
        lprint(
            f"({colors.lyellow}~{colors.r}) {text}{colors.lyellow+': '+colors.r+content if content else ''}"
        )
roblox_cookie = config['roblox cookie']
if config['item id'] == 0:
    item_id = console.input("Item id?")
else:
    item_id = config['item id']
threads = console.input("Buying threads?")
def get_xcsrf():
    r = requests.post('https://friends.roblox.com/v1/users/1/request-friendship',cookies={".ROBLOSECURITY":roblox_cookie})
    return r.headers['x-csrf-token']

def buy_limited(name, seller_id):
    r = requests.post(
        f"https://economy.roblox.com/v1/purchases/products/{item_id}",
        headers={
            '.ROBLOSECURITY': roblox_cookie,
            'x-csrf-token': get_xcsrf()
        },
        data={
            "expectedCurrency":1,
            "expectedPrice":0,
            "expectedSellerId":seller_id
        }
    )
    if r.status_code == 200 and r.json()['purchased'] == True:
        console.failed(f'Buyed',f"{name} {colors.lgreen}|{colors.r} {roblox_cookie[:40]}...")
    elif r.json()['purchased'] == False:
        console.failed(f'Failed to buy',f"{name} {colors.lred}|{colors.r} {r.text}")


def get_item_information(id):
    cookies = {
        '.ROBLOSECURITY': roblox_cookie,
    }
    headers = {
        'authority': 'catalog.roblox.com',
        'accept': 'application/json',
        'origin': 'https://www.roblox.com',
        'referer': 'https://www.roblox.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    }
    r = requests.get(f'https://catalog.roblox.com/v1/catalog/items/{id}/details',params={'itemType':'Asset'},headers=headers,cookies=cookies)
    if r.json().get("name"):
        data = r.json()
        #console.success("Scraped item information",f"{data['name']} {colors.lgreen}|{colors.r} Status{colors.lgreen}: {colors.r}{data['priceStatus']}")
        return data
    else:
        if "Invalid asset type id." in r.text:
            console.failed("Failed to scrape item information for",f"{id} | Invalid Id")
            return "invalid_id"
        elif "Too many requests" in r.text:
            console.failed("Failed to scrape item information for",f"{id} | Ratelimited")
            return "ratelimited"

while True:
    data = get_item_information(item_id)
    if not isinstance(data,str):
            
        if data['priceStatus'] != "Off Sale":
            console.success("Item OnSale",f"{data['name']} {colors.lgreen}|{colors.r} {'FREE' if not data.get('price') else ''}")
            break
        else:
            console.information("Item still OffSale",f"{data['name']}")
def thread():
    while True:
        buy_limited(data['name'],data['creatorTargetId'])

for _ in range(int(threads)):
    Thread(target=thread).start()
