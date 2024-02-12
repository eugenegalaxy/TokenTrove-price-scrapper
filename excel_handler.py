import openpyxl


def read_card_names(excel_path, sheet_name='active', column='A', start_row=3):
    workbook = openpyxl.load_workbook(excel_path)
    if sheet_name not in workbook.sheetnames:
        sheet = workbook.active
    else:
        sheet = workbook[sheet_name]
    first_column_values = [cell.value for cell in sheet[column][start_row:] if cell.value is not None]
    workbook.close()
    return first_column_values
