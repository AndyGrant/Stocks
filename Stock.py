from numpy import array, polyfit
from datetime import datetime
from yahoo_fin import stock_info
from matplotlib.pyplot import subplot2grid
from collections import namedtuple as NamedTuple

class Stock(object):

    Point = NamedTuple('Point', ['date', 'time', 'opens', 'close', 'volume'])

    def __init__(self, ticker, datafile):
        self.ticker  = ticker
        self.data    = self.parse_data(datafile)
        self.alldays = list(set([f.date for f in self.data]))
        self.alldays.sort()

    def __str__(self):
        output = "=============== {} ===============\n".format(self.ticker)
        for date, time, opens, close, volume in self.data:
            output += "{} {} {} {} {}\n".format(date, time, opens, close, volume)
        return output

    def parse_data(self, datafile):
        with open(datafile) as fin:
            data = fin.readlines()
        return [self.Point(*f.split()[1:]) for f in data if self.ticker == f.split()[0]]


    def earliest_datapoint(self, day):
        for point in self.data:
            if point.date == day:
                return point
        raise Exception("No data found on given day.")

    def opening_datapoint(self, day):
        for point in self.data[::-1]:
            if point.date == day and "09:30:00-04:00" in point.time:
                return point
        raise Exception("No opening data found on given day.")

    def latest_datapoint(self, day):
        for point in self.data[::-1]:
            if point.date == day:
                return point
        raise Exception("No data found on given day.")


    def pre_market_gains(self, day):
        pre_market  = float(self.earliest_datapoint(day).opens)
        open_market = float(self.opening_datapoint(day).opens)
        return str(100 * (open_market / pre_market - 1)) + "%"

    def open_market_gains(self, day):

        # If in the past, assume we have logged data
        if day != str(datetime.today().strftime('%Y-%m-%d')):
            open_market  = float(self.opening_datapoint(day).opens)
            after_market = float(self.latest_datapoint(day).close)
            return str(100 * (after_market / open_market - 1)) + "%"

        # If in the present, we can fetch a realtime value
        else:
            open_market  = float(self.opening_datapoint(day).opens)
            after_market = float(stock_info.get_live_price(self.ticker))
            return str(100 * (after_market / open_market - 1)) + "%"


    def compute_gains_for_model(self, day, length=30):

        # Fetch the last 'length' days of trades
        before = [f for f in self.alldays if f < day]
        if len(before) < length:
            raise Exception("Not enough data points.")
        inrange = before[-length:]

        # For each day, fetch the earliest, at open, and latest, Stock prices
        pre_markets   = [float(self.earliest_datapoint(day).opens) for day in inrange]
        open_markets  = [float(self.opening_datapoint(day).opens)  for day in inrange]
        after_markets = [float(self.latest_datapoint(day).close)   for day in inrange]

        # Compute % gained during pre-market and % gained until latest Stock prices
        pre_gains  = [100 * (opens /   pre - 1) for   pre, opens in zip( pre_markets,  open_markets)]
        open_gains = [100 * (after / opens - 1) for opens, after in zip(open_markets, after_markets)]

        return [pre_gains, open_gains]

    def compute_model(self, day, length=30):

        # For each 'length' previous days, find pre vs actual gains
        pre_gains, open_gains = self.compute_gains_for_model(day, length)

        try:
            M, B = polyfit(array(pre_gains), array(open_gains), 1)
            return [str(M), str(B) + "%"]
        except: print("Unable to fit a model for {} on {}".format(self.ticker, day))
        return ["0.00", "0.00%"] # This ensures that our model never invests

    def graph_model(self, day, gridsize, location, length=30):

        # For each 'length' previous days, find pre vs actual gains
        pre_gains, open_gains = self.compute_gains_for_model(day, length)

        # Build the Model if possible, otherwise set to None
        try: M, B = polyfit(array(pre_gains), array(open_gains), 1)
        except: print ("Unable to fit a model for {} on {}".format(self.ticker, day)); M = B = None

        # Build and Title a Scatter Plot
        ax = subplot2grid(gridsize, location)
        ax.set_title(self.ticker)
        ax.scatter(array(pre_gains), array(open_gains))

        # Plot the M & B values computed
        if M != None and B != None:
            colour = ["r", "g"][M >= 0.0]
            ax.plot(array(pre_gains), M*array(pre_gains) + B, colour)