import os
import json
import time
import random

# ---------------- SETUP ----------------

os.makedirs("users", exist_ok=True)
os.makedirs("servers", exist_ok=True)

DB_FILE = "users/users.json"

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({}, f)


# ---------------- DATABASE ----------------

def load_users():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_users(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)


# ---------------- RANK ----------------

def get_rank(coins):

    if coins >= 20000:
        return "Legend"
    elif coins >= 5000:
        return "ApexHost"
    elif coins >= 1500:
        return "ProHoster"
    elif coins >= 500:
        return "Hoster"
    elif coins >= 100:
        return "Miner"
    else:
        return "Noob"


# ---------------- REGISTER ----------------

def register():

    db = load_users()

    user = input("Username: ")

    if user in db:
        print("User exists")
        return

    password = input("Password: ")

    db[user] = {
        "password": password,
        "coins": 5,
        "tokens": 0,
        "rank": "Noob",
        "last_daily": 0,
        "last_mine": 0
    }

    save_users(db)

    print("Registered successfully (+5 coins)")


# ---------------- LOGIN ----------------

def login():

    db = load_users()

    user = input("Username: ")
    password = input("Password: ")

    if user not in db:
        print("User not found")
        return None

    if db[user]["password"] != password:
        print("Wrong password")
        return None

    print("Login success")
    return user


# ---------------- PROFILE ----------------

def profile(user):

    db = load_users()

    coins = db[user]["coins"]
    tokens = db[user]["tokens"]

    rank = get_rank(coins)

    db[user]["rank"] = rank

    save_users(db)

    print("\n----- PROFILE -----")
    print("User:", user)
    print("Rank:", rank)
    print("Coins:", coins)
    print("Tokens:", tokens)

    print("\nServers:")
    for s in os.listdir("servers"):
        if s.endswith("_" + user):
            print(" ", s)


# ---------------- SERVER PLANS ----------------

PLANS = {
    "1": (512, 30),
    "2": (1024, 60),
    "3": (2048, 120),
    "4": (4096, 250),
    "5": (6144, 400),
    "6": (8192, 800)
}


# ---------------- BUY SERVER ----------------

def buy_server(user):

    db = load_users()

    print("\nBuy Server:")
    print("1. 512MB - 30 coins")
    print("2. 1024MB - 60 coins")
    print("3. 2048MB - 120 coins")
    print("4. 4096MB - 250 coins")
    print("5. 6144MB - 400 coins")
    print("6. 8192MB - 800 coins")

    choice = input("> ")

    if choice not in PLANS:
        return

    ram, price = PLANS[choice]

    if db[user]["coins"] < price:
        print("Not enough coins")
        return

    db[user]["coins"] -= price

    save_users(db)

    name = f"{ram}_{user}"

    path = f"servers/{name}"

    os.makedirs(path, exist_ok=True)
    os.makedirs(f"{path}/plugins", exist_ok=True)

    with open(f"{path}/start.sh", "w") as f:
        f.write(f"java -Xms{ram}M -Xmx{ram}M -jar server.jar nogui")

    print("Server created:", name)


# ---------------- DELETE SERVER ----------------

def delete_server(user):

    ram = input("Enter server RAM to delete: ")

    path = f"servers/{ram}_{user}"

    if os.path.exists(path):

        os.system(f"rm -rf {path}")

        print("Server deleted")

    else:
        print("Server not found")


# ---------------- UPGRADE SERVER ----------------

def upgrade_server(user):

    db = load_users()

    old_ram = input("Current RAM: ")
    new_ram = input("New RAM: ")

    old_path = f"servers/{old_ram}_{user}"
    new_path = f"servers/{new_ram}_{user}"

    if not os.path.exists(old_path):
        print("Server not found")
        return

    cost = int(new_ram) // 10

    if db[user]["coins"] < cost:
        print("Not enough coins")
        return

    db[user]["coins"] -= cost

    save_users(db)

    os.rename(old_path, new_path)

    with open(f"{new_path}/start.sh", "w") as f:
        f.write(f"java -Xms{new_ram}M -Xmx{new_ram}M -jar server.jar nogui")

    print("Server upgraded")


# ---------------- MINE WITH 15 SEC COOLDOWN ----------------

def mine(user):

    db = load_users()

    now = int(time.time())

    last = db[user].get("last_mine", 0)

    cooldown = 15

    remaining = cooldown - (now - last)

    if remaining > 0:
        print(f"Cooldown active: wait {remaining} seconds")
        return

    print("Mining...")
    time.sleep(1)

    reward = random.randint(1,5)

    db[user]["coins"] += reward

    token_chance = random.randint(1,20)

    if token_chance == 1:

        db[user]["tokens"] += 1

        print("You found a TOKEN!")

    db[user]["last_mine"] = now

    save_users(db)

    print(f"You mined {reward} coins")


# ---------------- DAILY ----------------

def daily(user):

    db = load_users()

    now = int(time.time())

    if now - db[user]["last_daily"] < 86400:
        print("Already claimed today")
        return

    db[user]["coins"] += 5

    db[user]["last_daily"] = now

    save_users(db)

    print("Daily reward claimed: 5 coins")


# ---------------- SEND COINS ----------------

def send_coins(user):

    db = load_users()

    to = input("Send to: ")
    amount = int(input("Amount: "))

    if to not in db:
        print("User not found")
        return

    if db[user]["coins"] < amount:
        print("Not enough coins")
        return

    db[user]["coins"] -= amount
    db[to]["coins"] += amount

    save_users(db)

    print("Coins sent")


# ---------------- SEND TOKENS ----------------

def send_tokens(user):

    db = load_users()

    to = input("Send to: ")
    amount = int(input("Amount: "))

    if to not in db:
        print("User not found")
        return

    if db[user]["tokens"] < amount:
        print("Not enough tokens")
        return

    db[user]["tokens"] -= amount
    db[to]["tokens"] += amount

    save_users(db)

    print("Tokens sent")


# ---------------- PORT SHOP ----------------

def port_shop(user):

    db = load_users()

    cost = 300

    if db[user]["coins"] < cost:
        print("Not enough coins")
        return

    db[user]["coins"] -= cost

    save_users(db)

    print("Playit port forwarding purchased")


# ---------------- USER MENU ----------------

def user_menu(user):

    while True:

        print("\n---- MENU ----")
        print("1 Profile")
        print("2 Buy Server")
        print("3 Upgrade Server")
        print("4 Delete Server")
        print("5 Mine")
        print("6 Daily Reward")
        print("7 Send Coins")
        print("8 Send Tokens")
        print("9 Port Shop")
        print("10 Logout")

        choice = input("> ")

        if choice == "1":
            profile(user)

        elif choice == "2":
            buy_server(user)

        elif choice == "3":
            upgrade_server(user)

        elif choice == "4":
            delete_server(user)

        elif choice == "5":
            mine(user)

        elif choice == "6":
            daily(user)

        elif choice == "7":
            send_coins(user)

        elif choice == "8":
            send_tokens(user)

        elif choice == "9":
            port_shop(user)

        elif choice == "10":
            break


# ---------------- MAIN ----------------

while True:

    print("\n--- MC HOSTING GAME ---")
    print("1 Register")
    print("2 Login")
    print("3 Exit")

    choice = input("> ")

    if choice == "1":
        register()

    elif choice == "2":

        user = login()

        if user:
            user_menu(user)

    elif choice == "3":
        break
