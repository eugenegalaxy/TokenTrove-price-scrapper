from datetime import datetime
import os
import traceback

from immutable_price_scrapper import ImmutablePriceScrapper
from excel_handler import ExcelHandler


def scan_cards(excel_filename: str) -> None:
    try:
        excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), excel_filename)  # Where to find excel
        qualities = ['Meteorite', 'Shadow', 'Gold', 'Diamond']  # Which card qualities to check
        currencies = ['ETH', 'GODS']  # Which currencies to check (NOTE: USDC and IMX also work, but idgaf about those)
        excel_column_structure = {'Meteorite': {'ETH': 2, 'GODS': 3},  # openpyxl column numbers for each quality/currency in card_prices.xlsx
                                  'Shadow':    {'ETH': 5, 'GODS': 6},
                                  'Gold':      {'ETH': 8, 'GODS': 9},
                                  'Diamond':   {'ETH': 11, 'GODS': 12}}

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
    except FileNotFoundError as e:
        print(f"FileNotFoundError: {e}")
        print("Please make sure the file exists and is in the same directory as the script.")
    except Exception as e:
        EH.save_and_close()
        raise e


def scan_cosmetics(excel_filename: str) -> None:
    try:
        excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), excel_filename)  # Where to find excel
        currencies = ['ETH', 'GODS']  # Which currencies to check (NOTE: USDC and IMX also work, but idgaf about those)
        excel_column_structure = {
            'Card back': {
                'ETH': {'column': 2, 'start_row': 3},
                'GODS': {'column': 3, 'start_row': 3}
            },
            'Board': {
                'ETH': {'column': 2, 'start_row': 8},
                'GODS': {'column': 3, 'start_row': 8}
            },
            'Trinket': {
                'ETH': {'column': 2, 'start_row': 28},
                'GODS': {'column': 3, 'start_row': 28}
            }
        }

        IMX = ImmutablePriceScrapper()
        EH = ExcelHandler(excel_path)

        sheet_name_now = datetime.now().strftime('%b %d %H_%M_%S')
        cosmetics_names = EH.read_card_names(sheet_name=sheet_name_now)
        EH.copy_sheet(destination_sheet_name=sheet_name_now)  # Creates a new sheet with the current date and time as the name from 'Template' sheet
        cosmetics_prices = IMX.get_prices_cosmetics_list(cosmetics_names, currencies)
        for type in cosmetics_prices:
            for currency in cosmetics_prices[type]:
                EH.fill_in_column(cosmetics_prices[type][currency], sheet_name_now,
                                  excel_column_structure[type][currency]['column'], start_row=excel_column_structure[type][currency]['start_row'])
        EH.update_changes_sheet(new_sheet_name=sheet_name_now)
        EH.save_and_close()
    except PermissionError as e:
        print(f"PermissionError: {e}")
        print("Please close the excel file before running the script.")
    except FileNotFoundError as e:
        print(f"FileNotFoundError: {e}")
        print("Please make sure the file exists and is in the same directory as the script.")
    except Exception as e:
        EH.save_and_close()
        raise e


if __name__ == '__main__':
    try:
        # scan_cards('card_prices.xlsx')
        scan_cosmetics('cosmetics_prices.xlsx')
    except Exception:
        traceback.print_exc()
        quit()
