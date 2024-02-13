from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import NoSuchElementException
import yfinance as yf
from pprint import pprint
import warnings
from tqdm import tqdm


def get_crypto_price(ticker):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        crypto = yf.Ticker(ticker)
        price = crypto.history(period='1d')['Close'].iloc[0]
    return price


def setup_driver():
    options = Options()
    options.add_argument("--headless")
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(options=options, service=service)
    return driver


def scrape_prices(cards, qualities, currencies):

    # In cases if only one card/quality/currency is given, convert to list for iteration to work
    if not isinstance(cards, list):
        cards = [cards]
    if not isinstance(qualities, list):
        qualities = [qualities]
    if not isinstance(currencies, list):
        currencies = [currencies]

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
                    print(f"\n{card} - {quality} - {currency}: Price not found. Set to 0.")
                    card_prices[card][quality][currency] = '0.00'
                except Exception as e:
                    print(f"{card}-{quality}-{currency}: {e}")
                    card_prices[card][quality][currency] = '0.00'
                if currency == 'GODS':
                    card_prices[card][quality]['USD'] = round(float(price_text) * gods_price, 2)
                elif currency == 'ETH':
                    card_prices[card][quality]['USD'] = round(float(price_text) * eth_price, 2)
                # print(f"{card}-{quality}-{currency}: {card_prices[card][quality][currency]} (${card_prices[card][quality]['USD']})")
    # pprint(card_prices)
    driver.quit()
    return card_prices
