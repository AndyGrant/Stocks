import yfinance

TICKERS = [
    "MTNB", "PTN" , "ZIOP", "NERV", "AEZS",
    "AMD" , "MSFT", "TSLA", "INTC", "AAPL",
    "NCLH", "CCL" , "RCL" , "SLM" , "NAVI",
    "SNDE", "CEI" , "OXY" , "PBF" , "XOM" ,
    "T"   , "VZ"  , "F"   , "GE"  , "WMT" ,
]

class StockTickers(object):

    def __init__(self, fname="stock_data.log"):
        self.fname = fname

    def download_data(self, *tickers):

        # We merge with previous downloads
        new_info = []; old_info = [];

        # Fetch Historical Data from Yahoo Finance
        for ticker in tickers:
            yticker = yfinance.Ticker(ticker)
            history = yticker.history(period="59d", interval="15m", prepost=True)

            # Store the Ticker, Date, Time, Opens, Close, and Volume
            for index in history.index:
                opens  = history.at[index, "Open"]
                close  = history.at[index, "Close"]
                volume = history.at[index, "Volume"]
                new_info.append("{} {} {} {} {}".format(ticker, index, opens, close, volume))

        # Open the existing datafile and read it all
        with open(self.fname) as fin:
            for line in fin.readlines():
                old_info.append(line.strip())

        # Merge the datasets and retain the ordering
        combined = list(set(new_info + old_info))
        combined.sort()

        # Backup the original dataset just incase
        with open(self.fname + ".backup", "w") as fout:
            for line in old_info:
                fout.write(line+"\n")

        # Overwrite the previous file
        with open(self.fname, "w") as fout:
            for line in combined:
                fout.write(line+"\n")

if __name__ == "__main__":
    StockTickers().download_data(*TICKERS)