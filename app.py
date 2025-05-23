import random
import os
import requests
from bs4 import BeautifulSoup
import time

# --- Cinfiguration ---
BOT_TOKEN = "7996896689:AAG0iZJiP95wf9_e8Bd9ud4tEprEU7HzleA"
CHANNEL_ID = "@DortmundDormitoryoffers"
SENT_FILE = "sent_offers.txt"

# --- Load sent offers ---
if not os.path.exists(SENT_FILE):
    open(SENT_FILE, 'w').close()

with open(SENT_FILE, 'r') as f:
    sent_offers_keys = set(line.strip() for line in f)

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
        offer_key = f"{offer["town"]}|{offer["header"]}|{offer["price"]}|{offer["area"]}|{offer["available"]}"
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


while True:
    check_for_offer()
    sleep_time = random.randint(500, 800)
    time.sleep(sleep_time)
