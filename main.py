import matplotlib.pyplot
import Stock, Sheet, StockTickers

DAYS = [
    "2020-08-07", "2020-08-06", "2020-08-05", "2020-08-04", "2020-08-03",
    "2020-07-31", "2020-07-30", "2020-07-29", "2020-07-28", "2020-07-27",
]

def build_sheets_for_days(*days):

    sheet = Sheet.Sheet("Stock Market Predictions Model")
    for day in days:
        sheet.init_worksheet(day, StockTickers.TICKERS)
        sheet.update_worksheet(day, StockTickers.TICKERS)

def graph_model_for_day(day):

    GRID_SIZE = (5, 5)
    FIGURE = matplotlib.pyplot.figure(figsize=(9, 9))

    for idx, ticker in enumerate(StockTickers.TICKERS):
        row = idx // GRID_SIZE[0]; col = idx % GRID_SIZE[1]
        Stock.Stock(ticker, "stock_data.log").graph_model(day, GRID_SIZE, (row, col))

    FIGURE.tight_layout()
    matplotlib.pyplot.show()


build_sheets_for_days(*DAYS)