import random
import os
import requests
from bs4 import BeautifulSoup
import time

# --- Cinfiguration ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
SENT_FILE = "sent_offers.txt"

# --- Load sent offers ---
if not os.path.exists(SENT_FILE):
    open(SENT_FILE, 'w').close()

with open(SENT_FILE, 'r',encoding="utf-8", errors="ignore") as f:
    sent_offers_keys = set(line.strip() for line in f)
print("file read")
# --- Telegram send  function ---


def send_to_channel(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": message}
    response = requests.post(url, payload)
    print(response.status_code, response.text)

# ---- offer processing ----


def process_offers(new_offers):
    global sent_offers_keys
    for offer in new_offers:
        offer_key = f'{offer["town"]}|{offer["header"]}|{offer["price"]}|{offer["area"]}|{offer["available"]}'
        if offer_key not in sent_offers_keys:
            if create_message(offer) != 0:
                send_to_channel(create_message(offer))
                sent_offers_keys.add(offer_key)
                with open(SENT_FILE, 'a') as f:
                    f.write(offer_key + "\n")


def check_for_offer():
    url = "https://www.stwdo.de/wohnen/aktuelle-wohnangebote#residential-offer-list"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    print(soup.select_one('option[value="Dortmund"]').get_text().strip())
    Dortmund = soup.select_one(
        'option[value="Dortmund"]').get_text().strip() == "Dortmund"
    if Dortmund:
        offers = soup.select(".teaser-body")
        # print(f"offers{offers}")
        offers_list = []
        for offer in offers:
            town = offer.select_one(".subheader-5").get_text()
            header = offer.select_one(".headline-5").get_text()
            body = offer.select_one(
                ".residential-offer-card-facts").find_all("span")
            price = body[1].get_text()
            area = body[3].get_text()
            available = body[5].get_text()
            dic = {"town": town, "header": header, "price": price,
                   "area": area, "available": available}
            # print(dic)
            offers_list.append(dic)
        process_offers(offers_list)
    else:
        print("no offers")


def create_message(offer):
    message = ""
    if offer['town'] == "Dortmund":
        message += f"{offer['header']}\n\n"
        message += f"Price: {offer['price']}\n"
        message += f"Area: {offer['area']}\n"
        message += f"Available from: {offer['available']}\n"
        return message
    else:
        return 0

# i = 0
# print("script started")
# for i in range (2):
#     i += 1
#     print(i)
#     check_for_offer()
#     #sleep_time = random.randint(500, 700)
#     sleep_time = 500
#     print(f"sleeping for {sleep_time} seconds")
#     time.sleep(sleep_time)


if __name__ == "__main__":
    print("script started")
    check_for_offer()
    # print(BOT_TOKEN)
    # print(CHANNEL_ID)
    # send_to_channel(".")
