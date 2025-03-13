from typing import Callable, Iterable
import os
import datetime
import json
import yfinance as yf
import numpy as np
import pandas as pd

class StockData:
    CACHE_DIR = './cache/'
    CACHE_TYPE = '.csv'
    CACHE_INFO_TYPE = '.json'
    DATE_FORMAT = '%Y-%m-%d'
    
    def __init__(self,
                 ticker: str,
                 start: datetime.datetime = None,
                 ticker_postfix: str = '.ax'):
        self.ticker = ticker
        self.cache_path = (StockData.CACHE_DIR
                        +  ticker
                        +  StockData.CACHE_TYPE)
        self.cache_info_path = (StockData.CACHE_DIR
                             +  ticker
                             +  StockData.CACHE_INFO_TYPE)

        # Default start to 1 year ago
        if start is None:
            start = datetime.datetime.now() - datetime.timedelta(days=365)
        self.start_date = start

        # Download data if cache does not exist
        if not os.path.exists(self.cache_path):
            print(f"Downloading data for {ticker}"
                  f" beginning {self.start_date.strftime(StockData.DATE_FORMAT)}")
            ticker = yf.Ticker(ticker + ticker_postfix)
            history = ticker.history(start=self.start_date)

            self.data = history
            print(f"Download finished")

        # Read from cache
        else:
            cached_data = pd.read_csv(self.cache_path)
            cached_info = {}
            with open(self.cache_info_path, 'r') as cache_info:
                cached_info = json.load(cache_info)
            cached_start_date = datetime.datetime.strptime(cached_info['start-date'],
                                                           StockData.DATE_FORMAT)

            # Download data outside of desired date range
            if self.start_date < cached_start_date:
                print(f"Downloading data for {ticker}"
                      f" beginning {self.start_date.strftime(StockData.DATE_FORMAT)}"
                      f" ending {cached_start_date.strftime(StockData.DATE_FORMAT)}")
                ticker = yf.Ticker(ticker + ticker_postfix)
                before = ticker.history(start=self.start_date,
                                        end=cached_start_date)
                # TODO: after end date

                self.data = pd.concat((before, cached_data))
                print(f"Download finished")

            # Align dates with cache
            else:
                self.start_date = cached_start_date
                # TODO: end date
                self.data = cached_data

        # Generate info and cache data
        self.info = {
            'start-date': self.start_date.strftime(StockData.DATE_FORMAT),
            'end-date': 'todo'
        }
        self.cache_data()

    def __getitem__(self, indicators: tuple) -> tuple:
        return tuple(self.data[i] for i in indicators)

    def cache_data(self):
        # Store data
        self.data.to_csv(self.cache_path)

        # Store info
        with open(self.cache_info_path, 'w') as cache_info:
            json.dump(self.info, cache_info)
        
    def preprocess_indicators(self,
                              indicators: Iterable,
                              force: bool = False):
        for i in indicators:
            if isinstance(i, str):
                self.preprocess_indicator(i, force)

    def preprocess_indicator(self,
                             indicator: str,
                             force: bool = False) -> str:
        # Indicator already exists
        if indicator in self.data.columns and not force:
            return indicator

        # Exponential Moving Average
        if indicator.startswith('ema'):
            ema_period = indicator[3:]
            if (len(ema_period) == 0
            or  not ema_period.isnumeric()):
                print(f"Could not preprocess indicator: {indicator}")
                return

            self.data[indicator] = self.ind_ema(int(ema_period))
            return indicator
            
        # Simple Moving Average
        if indicator.startswith('sma'):
            pass

        # Standard Deviation
        if indicator.startswith('std'):
            pass

        # Differential indicator
        if indicator.startswith('d_'):
            primary_indicator = indicator[2:]
            if self.preprocess_indicator(primary_indicator) is None:
                print(f"Could not preprocess indicator: {indicator}")
                return

            self.data[indicator] = self.ind_d(self.data[primary_indicator])
            return indicator

        # True Range
        if indicator.startswith('tr'):
            self.data[indicator] = self.ind_tr()
            return indicator

        # Average True Range (in progress)
        if indicator.startswith('atr'):
            self.data['atr'] = self.ind_atr()
            return indicator

        # Bollinger Bands (in progress)
        if indicator.startswith('boll'):
            if len(indicator[4:]) == 0:
                self.generate_ind_boll()
                return indicator
            comma_i = indicator.find(',')
            boll_period = indicator[4:comma_i]
            boll_sd = indicator[comma_i + 1:]
            if (not boll_period.isnumeric()
            or  not boll_period.replace('.', '', 1).isnumeric()):
                print(f"Could not preprocess indicator: {indicator}")
                return
            
            self.generate_ind_boll(int(boll_period), float(boll_sd))

    def ind_ema(self, period: int) -> pd.Series:
        ema = self.data['Close'].ewm(span=period,
                                     adjust=False,
                                     min_periods=period).mean()
        # ema[:period] = np.nan
        return ema

    def ind_sma(self):
        pass # TODO

    def ind_d(self,
              primary_indicator: pd.Series,
              periods: int = 1) -> pd.Series:
        return primary_indicator.diff(periods=periods)

    def ind_tr(self):
        prev_close = self.data['Close'].shift(periods=1)
        return (np.maximum(self.data['High'], prev_close)
             -  np.minimum(self.data['Low'], prev_close))

    def ind_atr(self, period: int = 14):
        # Standard ATR calculation
        # self.data['atr'] = np.nan
        # self.data.loc[13, 'atr'] = np.mean(self.data['tr'].iloc[:14])

        # i = 14
        # end = self.data.shape[0]

        # print("began standard atr")
        # while i < end:
        #     self.data.loc[i, 'atr'] = (self.data['atr'].iloc[i - 1] * period + self.data['tr'].iloc[i]) / period
        #     i += 1
        # print("finished standard atr")

        # Custom ATR calculation
        # print("begin custom atr")
        atr = self.data['tr'].ewm(alpha=1 / period,
                                         adjust=False,
                                         min_periods=period).mean()
        # custom_atr[:period] = np.nan
        # print("end custom atr")
        return atr

    def generate_ind_boll(self, period: int = 20, sd: float = 2, sd_period: int = -1):
        if sd_period < 0:
            sd_period = period
        indicator_sma = f"sma{period}"
        indicator_std = f"std{sd_period}sma{period}"
        indicator_plus  = f"boll+{period},{sd:.1f}"
        indicator_minus = f"boll-{period},{sd:.1f}"

        self.preprocess_indicator(indicator_sma)
        self.preprocess_indicator(indicator_std)
        self.data[indicator_plus]  = (self.data[indicator_sma]
                                   +  sd * self.data[indicator_std])
        self.data[indicator_minus] = (self.data[indicator_sma]
                                   -  sd * self.data[indicator_std])

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

    def run_and_evaluate(self, data: StockData):
        buys, sells = self.run(data)

        # Order the interactions
        interactions = []
        for buy in buys:
            interactions.append((buy, 'b'))
        for sell in sells:
            interactions.append((sell, 's'))
        interactions.sort(key=lambda x: x[0])

        value = 1
        losses = 0
        wins = 0
        neutral = 0

        hold_value = 0

        for date, signal in interactions:
            # Buy signal
            if signal == 'b':
                # Already holding
                if hold_value > 0:
                    # print("rebought ignored")
                    continue

                # Not holding
                elif hold_value == 0:
                    hold_value = data.data.loc[date, 'Close']
                    # print(f"bought at {hold_value}")

            # Sell signal
            if signal == 's':
                # Not holding
                if hold_value == 0:
                    # print("ignoring invalid sell")
                    continue

                # Calculate outcome of sell
                outcome = (data.data.loc[date, 'Close'] / hold_value)

                losses += int(outcome < 1)
                wins += int(outcome > 1)
                neutral += int(outcome == 1)

                value *= outcome
                hold_value = 0

                # print(f"sold at {data.data.loc[date, 'Close']} for {outcome} result")
                # print()

        # print(f"Final Value: {value}")
        # print(f"Wins: {wins}, Losses: {losses}, Neutral: {neutral}")
        
        return buys, sells, value
