import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import NoSuchElementException
import yfinance as yf
import warnings
from tqdm import tqdm

from immutable_card_address_dict import card_immutable_address_dict


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


def scrape_prices_immutable(cards, qualities, currencies):

    # In cases if only one card/quality/currency is given, convert to list for iteration to work
    if not isinstance(cards, list):
        cards = [cards]
    if not isinstance(qualities, list):
        qualities = [qualities]
    if not isinstance(currencies, list):
        currencies = [currencies]

    url_part_gods = 'ERC20&token_address=0xccc8cb5229b0ac8069c51fd58367fd1e622afd97'
    url_part_eth = 'ETH&token_address='

    card_urls = card_immutable_address_dict

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
                    if currency == 'GODS':
                        url_currency = url_part_gods
                    elif currency == 'ETH':
                        url_currency = url_part_eth
                    card_url = card_urls[card][quality]
                    if card_url == '':
                        print(f"\n{card} - {quality} - {currency}: Card URL found in dict. Set to 0.")
                        card_prices[card][quality][currency] = '0.00'
                    else:
                        url = f'https://market.immutable.com/collections/0xacb3c6a43d15b907e8433077b6d38ae40936fe2c/stacked-assets/{card_url}?token_type={url_currency}'
                        driver.get(url)
                        driver.implicitly_wait(10)
                        XPath = '/html/body/div/div[2]/div[2]/div[2]/div/div/div/span'
                        price_element = driver.find_element(By.XPATH, XPath)
                        price_text = price_element.text
                        card_prices[card][quality][currency] = price_text
                        # random_sleep = random.randint(2, 6)
                        # time.sleep(random_sleep)
                except NoSuchElementException:
                    print(f"\n{card} - {quality} - {currency}: Price not found. Set to 0.")
                    card_prices[card][quality][currency] = '0.00'
                except Exception as e:
                    print(f"{card}-{quality}-{currency}: {e}")
                    card_prices[card][quality][currency] = '0.00'
                if currency == 'GODS':
                    card_prices[card][quality]['USD'] = round(float(card_prices[card][quality][currency]) * gods_price, 2)
                elif currency == 'ETH':
                    card_prices[card][quality]['USD'] = round(float(card_prices[card][quality][currency]) * eth_price, 2)
    driver.quit()
    return card_prices
