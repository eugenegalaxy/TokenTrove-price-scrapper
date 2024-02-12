from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import NoSuchElementException
import yfinance as yf

from tqdm import tqdm
from pprint import pprint


def get_crypto_price(ticker):
    crypto = yf.Ticker(ticker)
    price = crypto.history(period='1d')['Close'].iloc[0]
    return price


def setup_driver():
    options = Options()
    options.add_argument("--headless")
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(options=options, service=service)
    return driver


# NOTE: Maybe split search into different calls by quality (higher qualities, especially in GODS often not available = slow)
def scrape_prices(cards, qualities, currencies):
    driver = setup_driver()
    gods_price = get_crypto_price('GODS-USD')
    eth_price = get_crypto_price('ETH-USD')
    card_prices = {}
    for card in tqdm(cards):
        card_prices[card] = {}
        for quality in qualities:
            card_prices[card][quality] = {}
            for currency in currencies:
                try:
                    url = f'https://tokentrove.com/collection/GodsUnchainedCards?search={card.replace(" ", "%20")}&quality={quality}&currency={currency}'
                    driver.get(url)
                    driver.implicitly_wait(10)
                    XPath = '/html/body/div[1]/div/div/div[2]/div/div[2]/div[5]/div/div/div/div[1]/div/div/div/div[2]/div[2]/div[1]/span'
                    price_element = driver.find_element(By.XPATH, XPath)
                    price_text = price_element.text
                    card_prices[card][quality][currency] = price_text
                except NoSuchElementException:
                    print(f"{card}-{quality}-{currency}: Price not found. Set to 0")
                    card_prices[card][quality][currency] = 0
                except Exception as e:
                    print(f"{card}-{quality}-{currency}: {e}")
                    card_prices[card][quality][currency] = 0
                if currency == 'GODS':
                    card_prices[card][quality]['GODS_USD'] = round(float(price_text) * gods_price, 2)
                    usd_price = card_prices[card][quality]['GODS_USD']
                elif currency == 'ETH':
                    card_prices[card][quality]['ETH_USD'] = round(float(price_text) * eth_price, 2)
                    usd_price = card_prices[card][quality]['ETH_USD']
                print(f"{card}-{quality}-{currency}: {price_text} (${usd_price})")
    pprint(card_prices)
    driver.quit()
    return card_prices
