import os
from tokentrove_price_scrapper import scrape_prices
from excel_handler import read_card_names


if __name__ == '__main__':
    try:
        excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'card_prices.xlsx')  # Where to find excel
        excel_sheet_name = 'Feb 12'  # Which sheet to get card list from (assumes names are in "A" column & first 3 rows are headers)

        qualities = ['Meteorite', 'Shadow', 'Gold', 'Diamond']  # Which card qualities to check
        currencies = ['GODS', 'ETH']  # Which currencies to check (NOTE: USDC and IMX also work, but idgaf about those)

        cards = read_card_names(excel_path, sheet_name=excel_sheet_name)
        print(f'Found {len(cards)} names: {cards}')
        card_prices = scrape_prices(cards, qualities, currencies)
    except Exception as e:
        print(e)
        quit()
