import time, re

from Stock import Stock
from pygsheets import authorize as pygauthorize
from pygsheets.exceptions import WorksheetNotFound

class Sheet(object):

    def __init__(self, sheet_name):
        self.credentials = pygauthorize()
        self.spreadsheet = self.credentials.open(sheet_name)

    def delete_worksheets(self):

        # Fetch all existing worksheets for YYYY-MM-DD
        worksheets = self.spreadsheet.worksheets()[::]
        worksheets = [f for f in worksheets if re.search("[0-9]{4}-[0-9]{2}-[0-9]{2}", f.title)]

        # Delete all worksheets for YYYY-MM-DD
        for worksheet in worksheets:
            print ("Deleting Worksheet for {}".format(worksheet.title))
            self.spreadsheet.del_worksheet(worksheet); time.sleep(1)

    def init_worksheet(self, day, tickers, fname="stock_data.log"):

        # Either Fetch or Create a Worksheet for the given day
        try: worksheet = self.spreadsheet.worksheet_by_title(day)
        except WorksheetNotFound:
            source = self.spreadsheet.worksheet_by_title("Base")
            worksheet = self.spreadsheet.add_worksheet(day, src_worksheet=source)

        # Set the Title, Tickers, and find today's formulas
        title_sentence = "Pre-Market vs Bell-Till-Latest Predictions for {}"
        worksheet.update_value("A1", title_sentence.format(day))
        columns = [[f, *Stock(f, fname).compute_model(day)] for f in tickers]
        worksheet.update_values(crange="A4:C1500", values=columns)

    def update_worksheet(self, day, tickers, fname="stock_data.log"):

        # Fetch the Worksheet and all tracked Stocks
        worksheet = self.spreadsheet.worksheet_by_title(day)
        tickers = worksheet.get_values("A4", "A1500")

        # Prepare to compute information for each Stock
        tickers = [ticker[0] for ticker in tickers]
        stocks  = [Stock(ticker, fname) for ticker in tickers]

        # Try to determine Pre and Open Market movements
        pre_market = []; open_market = [];
        for stock in stocks:
            try: pre_market.append(stock.pre_market_gains(day))
            except: pre_market.append("")
            try: open_market.append(stock.open_market_gains(day))
            except: open_market.append("")

        values = [[A, B] for A, B in zip(pre_market, open_market)]
        worksheet.update_values(crange="D4:E1500", values=values)

if __name__ == "__main__":
    Sheet("Stock Market Predictions Model").delete_worksheets()