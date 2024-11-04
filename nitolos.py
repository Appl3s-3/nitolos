import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

class Nitolos:
    def __init__(self, stock: str, start: str, end: str):
        self.ticker = yf.Ticker(stock)
        self.data = self.ticker.history(start=start, end=end, interval="1d")['Close'].to_frame()
        self.strategy_results = []

    def calculate_ema(self, period: int):
        self.data['EMA' + str(period)] = self.data['Close'].ewm(span=period, adjust=False).mean()

    def simulate_strategy(self, start: str, end: str, strategy):
        self.strategy_results.append(strategy(self.data.loc[start:end]))

    def display_strategy_results(self, index: int = 0):
        results = self.strategy_results[index]

        # Print trades
        print("Trades: ")
        for trade in results['trades']:
            print(trade)

        # Print results
        print("Result: ")
        print(results['balance'])

        # Plot results
        start_date = results['active_period'][0]
        end_date = results['active_period'][1]
        auxiliary_series = results['auxiliary']

        fig = plt.figure()
        self.data['Close'].plot()
        for series in auxiliary_series:
            self.data[series].plot()

        

    # def simulate(self, start: str, end: str):
    #     buys = self.buy_order(self.data['EMA20'].loc(start, end),
    #                           self.data['EMA50'].loc(start, end))
    #     print(self.data.axes)
    #     # self.buy_dates = [self.data.axes[i for i in buys]]
    #     for buy_date in self.buy_dates:
    #         self.data['buys'][buy_date] = self.data['Close'][buy_date]

    #     sells = self.sell_order(self.data[i].loc(start, end) for i in self.sell_args)
    #     # self.sell_dates = [self.data.axes[i for i in sells]]
    #     for sell_date in self.sell_dates:
    #         self.data['sells'][sell_date] = self.data['Close'][sell_date]

    # def results(self):
    #     print(f"Buys: {len(self.buy_dates)}")
    #     print(f"Buy dates: {[i for i in self.buy_dates]}")

    #     print(f"Sells: {len(self.sell_dates)}")
    #     print(f"Sell dates: {[i for i in self.sell_dates]}")

    def plot(self, *args):
        fig = plt.figure()
        self.data['Close'].plot()

        self.data['EMA20'].plot()
        self.data['EMA50'].plot()
        # self.data['buys'].plot(kind='o', color='blue')
        # self.data['sells'].plot(kind='o', color='red')

        plt.show()

