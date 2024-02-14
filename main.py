import os
from tokentrove_price_scrapper import scrape_prices_tokentrove
from immutable_price_scrapper import scrape_prices_immutable
from excel_handler import read_card_names, fill_in_column
import traceback

if __name__ == '__main__':
    try:
        excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'card_prices.xlsx')  # Where to find excel
        excel_sheet_name = 'Feb 14'  # Which sheet to get card list from (assumes names are in "A" column & first 3 rows are headers)
        qualities = ['Meteorite', 'Shadow', 'Gold', 'Diamond']  # Which card qualities to check
        currencies = ['ETH', 'GODS']  # Which currencies to check (NOTE: USDC and IMX also work, but idgaf about those)
        excel_column_structure = {'Meteorite': {'ETH': 2, 'GODS': 3},  # openpyxl column numbers for each quality/currency in card_prices.xlsx
                                  'Shadow':    {'ETH': 5, 'GODS': 6},
                                  'Gold':      {'ETH': 8, 'GODS': 9},
                                  'Diamond':   {'ETH': 11, 'GODS': 12}}

        cards = read_card_names(excel_path, sheet_name=excel_sheet_name)
        local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output.txt')
        for quality in qualities:
            for currency in currencies:
                card_prices = scrape_prices_immutable(cards, quality, currency)
                for card in cards:
                    price = str(card_prices[card][quality]['USD']).replace('.', ',')
                simple_price_list_usd = [str(card_prices[card][quality]['USD']) for card in cards]
                fill_in_column(simple_price_list_usd, excel_path, excel_sheet_name, excel_column_structure[quality][currency])
    except Exception:
        traceback.print_exc()
        quit()
