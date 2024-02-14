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


class ImmutablePriceScrapper:

    IMPLICIT_WAIT_TIME = 5  # When the driver waits for an element to appear, it waits for this many seconds before throwing an error.
    RUN_HEADLESS = True  # If True, the browser will not open when the script is run.

    def __init__(self):
        self.driver = self.setup_driver()

    def setup_driver(self):
        options = Options()
        if self.RUN_HEADLESS:
            options.add_argument("--headless")
        service = Service(GeckoDriverManager().install())
        return webdriver.Firefox(options=options, service=service)

    def get_prices_card_list(self, cards: list[str], qualities: list[str], currencies: list[str]) -> dict:
        if not isinstance(cards, list):
            cards = [cards]
        if not isinstance(qualities, list):
            qualities = [qualities]
        if not isinstance(currencies, list):
            currencies = [currencies]

        card_urls = card_immutable_address_dict  # import from a file
        url_part_gods = 'ERC20&token_address=0xccc8cb5229b0ac8069c51fd58367fd1e622afd97'
        url_part_eth = 'ETH&token_address='
        gods_price = self.get_crypto_price('GODS-USD')
        eth_price = self.get_crypto_price('ETH-USD')
        card_prices = {}
        for quality in tqdm(qualities):
            card_prices[quality] = {}
            for currency in currencies:
                if currency == 'GODS':
                    url_currency_part = url_part_gods
                elif currency == 'ETH':
                    url_currency_part = url_part_eth
                card_prices[quality][currency] = []
                for card in cards:
                    url_currency_part = url_part_gods if currency == 'GODS' else url_part_eth
                    card_price = self.get_one_card_price(card, url_currency_part, card_urls[card][quality])
                    currency_usd_price = round(float(card_price) * gods_price if currency == 'GODS' else float(card_price) * eth_price, 2)
                    currency_usd_price = str(currency_usd_price).replace('.', ',')
                    card_prices[quality][currency].append(currency_usd_price)
        return card_prices

    def get_one_card_price(self, card: str, url_currency_part: str, url_card_part: str) -> str:
        """
        Retrieves the lowest price of a card from the Immutable marketplace by scrapping the price from a given URL.

        Args:
            card (str): The name of the card.
            url_currency_part (str): The currency part of the URL.
            url_card_part (str): The card part of the URL.

        Returns:
            str: The price of the card as a string.

        Raises:
            NoSuchElementException: If the price element is not found on the page.
            Exception: If any other error occurs during the price retrieval process.
        """
        try:
            if url_currency_part == '':
                print(f"\n{card}: Card URL found in dict. Price set to 0.00")
                price = '0.00'
            else:
                url = (
                    f'https://market.immutable.com/collections/0xacb3c6a43d15b907e8433077b6d38ae40936fe2c/'
                    f'stacked-assets/{url_card_part}?token_type={url_currency_part}'
                )
                self.driver.get(url)
                self.driver.implicitly_wait(self.IMPLICIT_WAIT_TIME)
                XPath = '/html/body/div/div[2]/div[2]/div[2]/div/div/div/span'
                price_element = self.driver.find_element(By.XPATH, XPath)
                price = price_element.text
                return price
        except NoSuchElementException:
            print(f"\n{card}: Price not found. Set to 0.")
            return "0.00"
        except Exception as e:
            print(f"{card}: {e}")
            return "0.00"

    def get_crypto_price(self, ticker):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            crypto = yf.Ticker(ticker)
            price = crypto.history(period='1d')['Close'].iloc[0]
        return price
