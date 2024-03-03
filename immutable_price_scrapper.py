from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import NoSuchElementException
import yfinance as yf
import warnings

from resources.immutable_card_address_dict import card_immutable_address_dict
from resources.immutable_cosmetics_name_dict import cosmetics_immutable_name_dict


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

    def get_crypto_price(self, ticker, period='1d') -> float:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            crypto = yf.Ticker(ticker)
            price = crypto.history(period=period)['Close'].iloc[0]
        return price

    def get_prices_card_list(self, cards: list[str], qualities: list[str], currencies: list[str]) -> dict:
        """
        Get the prices of cards in different qualities and currencies.

        Args:
            cards (list[str]): A list of card names.
            qualities (list[str]): A list of card qualities.
            currencies (list[str]): A list of currencies.

        Returns:
            dict: A dictionary containing the prices of cards in different qualities and currencies.
        """
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
        scan_counter = 0
        len_scans = len(cards) * len(qualities) * len(currencies)
        print(f'\nScanning {len_scans} card prices...')
        for quality in qualities:
            card_prices[quality] = {}
            for currency in currencies:
                if currency == 'GODS':
                    url_currency_part = url_part_gods
                elif currency == 'ETH':
                    url_currency_part = url_part_eth
                card_prices[quality][currency] = []
                for card in cards:
                    url_currency_part = url_part_gods if currency == 'GODS' else url_part_eth
                    card_url = card_urls[card][quality]
                    if card_url == '0':  # If the card is not found in the dict, set the price to 0.00 (some cards do not exist in certain qualities)
                        card_price = '0.00'
                    else:
                        card_price = self._get_one_card_price(card, url_currency_part, card_urls[card][quality])
                    currency_usd_price = round(float(card_price.replace(',', '')) * gods_price if currency == 'GODS' else float(card_price) * eth_price, 2)
                    currency_usd_price = str(currency_usd_price).replace('.', ',')
                    card_prices[quality][currency].append(currency_usd_price)
                    print(f"Got price for {card} - {quality} in {currency} ${currency_usd_price} (Scan {scan_counter}/{len_scans})")
                    scan_counter += 1
        return card_prices

    def _get_one_card_price(self, card: str, url_currency_part: str, url_card_part: str) -> str:
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
            print(f"{card}: Price not found. Set to 0.")
            return "0.00"
        except Exception as e:
            print(f"{card}: {e}")
            return "0.00"

    def get_prices_cosmetics_list(self, cosmetics_names: list[str], currencies: list[str]) -> dict:
        if not isinstance(currencies, list):
            currencies = [currencies]
        cosmetics_dict = cosmetics_immutable_name_dict  # import from a file
        gods_price = self.get_crypto_price('GODS-USD')
        eth_price = self.get_crypto_price('ETH-USD')
        cosmetics_prices = {}
        scan_counter = 1
        len_scans = sum([len(cosmetics_dict[type]) for type in cosmetics_dict]) * len(currencies)
        print(f'\nScanning {len_scans} cosmetics prices...')
        for type in cosmetics_dict:
            cosmetics_prices[type] = {}
            for currency in currencies:
                cosmetics_prices[type][currency] = []
                for cosmetic in cosmetics_names:
                    if cosmetic in cosmetics_dict[type]:
                        cosmetic_price = self._get_one_cosmetics_price(cosmetic, type, currency)  # Example: 'Order', 'Card back', 'GODS'
                        currency_usd_price = round(float(cosmetic_price.replace(',', '')) *
                                                   gods_price if currency == 'GODS' else float(cosmetic_price) * eth_price, 2)
                        currency_usd_price = str(currency_usd_price).replace('.', ',')
                        cosmetics_prices[type][currency].append(currency_usd_price)
                        print(f"Got price for {cosmetic} - {type} in {currency} ${currency_usd_price} (Scan {scan_counter}/{len_scans})")
                        scan_counter += 1
        return cosmetics_prices

    def _get_one_cosmetics_price(self, cosmetic: str, type: str, currency: str) -> str:
        if currency == "GODS":
            url_currency = '&currencyFilter=0xccc8cb5229b0ac8069c51fd58367fd1e622afd97'
        elif currency == "ETH":
            url_currency = ''
        else:
            raise ValueError("Invalid currency")
        type = type.replace(' ', '+').lower()
        cosmetic = cosmetic.replace(' ', '+')
        try:
            url = (
                f'https://market.immutable.com/collections/0x7c3214ddc55dfd2cac63c02d0b423c29845c03ba?filters[type][]='
                f'{type}{url_currency}&sort[order_by]=buy_quantity_with_fees&sort[direction]=asc&keywordSearch={cosmetic}'
            )
            self.driver.get(url)
            self.driver.implicitly_wait(self.IMPLICIT_WAIT_TIME)
            XPath = '/html/body/div/div[2]/div[2]/div[3]/div/a[1]/div/div[2]/div/div[2]/div/div/span'
            price_element = self.driver.find_element(By.XPATH, XPath)
            price = price_element.text
            return price
        except NoSuchElementException:
            print(f"{cosmetic}: Price not found. Set to 0.")
            return "0.00"
        except Exception as e:
            print(f"{cosmetic}: {e}")
            return "0.00"
