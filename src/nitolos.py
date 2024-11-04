from typing import Callable, Iterable
import yfinance as yf
import numpy as np
import pandas as pd
import datetime

class StockData:
    def __init__(self,
                 ticker: str,
                 start: datetime.datetime = None,
                 ticker_postfix: str = '.ax'):
        # Check if cached data exists

        # Check if cached data is within desired date range

        # self.data = pd.
        self.start_date = start
        if start is None:
            start = datetime.datetime.now() - datetime.timedelta(days=365)

        # Obtain data for the desired date range
        ticker = yf.Ticker(ticker + ticker_postfix)
        history = ticker.history(start=self.start_date)

        self.data = history['Close'].to_frame()

    def __getitem__(self, indicators: tuple) -> tuple:
        return tuple(self.data[i] for i in indicators)

    def preprocess_indicators(self, indicators: Iterable, force: bool = False):
        for i in indicators:
            self.preprocess_indicator(i, force)

    def preprocess_indicator(self, indicator: str, force: bool = False):
        # Indicator already exists
        if indicator in self.data.columns and not force:
            return

        # EMA indicator
        if indicator.startswith('ema'):
            ema_period = indicator[3:]
            if (len(ema_period) == 0
            or  not ema_period.isnumeric()):
                print(f"Could not preprocess indicator: {indicator}")
                return

            self.data[indicator] = self.ind_ema(int(ema_period))
            
        # SMA indicator
        if indicator.startswith('sma'):
            pass

    def ind_ema(self, period: int) -> pd.Series:
        ema = self.data['Close'].ewm(span=period, adjust=False).mean()
        ema[:period] = np.nan
        return ema

class Strategy:
    def __init__(self,
                 buy_signal: Callable,
                 sell_signal: Callable,
                 buy_parameters: tuple,
                 sell_parameters: tuple):
        self.buy_signal      = buy_signal
        self.sell_signal     = sell_signal
        self.buy_parameters  = buy_parameters
        self.sell_parameters = sell_parameters

    def run(self, data: StockData) -> tuple:
        # Prepare the required indicators for the strategy
        data.preprocess_indicators(self.buy_parameters)
        data.preprocess_indicators(self.sell_parameters)
        
        buys  = self.buy_signal(*data[self.buy_parameters])
        sells = self.sell_signal(buys, *data[self.sell_parameters])

        return buys, sells
