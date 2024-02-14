from datetime import datetime
import os
import traceback

from immutable_price_scrapper import ImmutablePriceScrapper
from excel_handler import ExcelHandler


if __name__ == '__main__':
    try:
        excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'card_prices.xlsx')  # Where to find excel
        qualities = ['Meteorite', 'Shadow', 'Gold', 'Diamond']  # Which card qualities to check
        currencies = ['ETH', 'GODS']  # Which currencies to check (NOTE: USDC and IMX also work, but idgaf about those)
        excel_column_structure = {'Meteorite': {'ETH': 2, 'GODS': 3},  # openpyxl column numbers for each quality/currency in card_prices.xlsx
                                  'Shadow':    {'ETH': 5, 'GODS': 6},
                                  'Gold':      {'ETH': 8, 'GODS': 9},
                                  'Diamond':   {'ETH': 11, 'GODS': 12}}

        prices_structure = {'Meteorite': {'ETH': [], 'GODS': []},
                            'Shadow':    {'ETH': [], 'GODS': []},
                            'Gold':      {'ETH': [], 'GODS': []},
                            'Diamond':   {'ETH': [], 'GODS': []}}

        IMX = ImmutablePriceScrapper()
        EH = ExcelHandler(excel_path)

        sheet_name_now = datetime.now().strftime('%b %d %H_%M_%S')
        EH.copy_sheet(destination_sheet_name=sheet_name_now)  # Creates a new sheet with the current date and time as the name from 'Template' sheet
        cards = EH.read_card_names(sheet_name=sheet_name_now)
        card_prices = IMX.get_prices_card_list(cards, qualities, currencies)
        for quality in qualities:
            for currency in currencies:
                EH.fill_in_column(card_prices[quality][currency], sheet_name_now, excel_column_structure[quality][currency])
        EH.update_changes_sheet(new_sheet_name=sheet_name_now, card_name_list=cards)
        EH.save_and_close()
    except PermissionError as e:
        print(f"PermissionError: {e}")
        print("Please close the excel file before running the script.")
    except Exception:
        EH.save_and_close()
        traceback.print_exc()
        quit()
