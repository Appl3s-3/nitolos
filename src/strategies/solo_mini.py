import pandas as pd
import nitolos as nit

class SoloMini:
    """
    Trading Strategy:
    - Entry Criteria:
    1. 10-day EMA crosses above 20-day EMA.
    2. Stock makes a new 1-month high (~20 trading days).
    3. Volatility filter to exclude extreme moves: ** NOT IMPLEMENTED **
        - Option 1: Exclude stocks that rose >10% in a single day.
        - Option 2: Exclude stocks that rose >20% in the last month.
    4. Avoid holding through earnings. ** NOT IMPLEMENTED **

    - Exit Criteria:
    - Use ATR-based stop loss with a multiplier of 3.
    """
    def __init__(self,
                 small_ema_period: int = 10,
                 large_ema_period: int = 20,
                 high_lookback_period: int = 20,
                 volatility_filter: float = 0.1,
                 volatility_period: int = 1,
                 atr_period: int = 14,
                 atr_stop_loss_multiplier: float = 3):
        """
        Initializes the trading strategy parameters.

        Parameters:
        - small_ema_period (int): The period for the short-term EMA, defaulting to 10 days.
        - large_ema_period (int): The period for the long-term EMA, defaulting to 20 days.
        - high_period (int): The lookback period for identifying a 1-month high, defaulting to 20 trading days.
        - volatility_filter (float): The threshold for filtering out highly volatile stocks, defaulting to 10%.
        - volatility_period (int): The lookback period for the volatility filter, defaulting to 1 day.
        - atr_period (int): The period for the ATR, defaulting to 14 days.
        - atr_stop_loss_multiplier (float): The multiplier for the Average True Range (ATR) stop-loss, defaulting to 3.
        
        Notes:
        - This strategy avoids holding through earnings reports. ** NOT IMPLEMENTED **
        - Entries are determined by a combination of moving average crossovers, new highs, and volatility filtering.
        - Exits are solely based on the ATR stop-loss rule.
        """
        self.small_ema_period         = small_ema_period
        self.large_ema_period         = large_ema_period
        self.high_lookback_period     = high_lookback_period
        self.volatility_filter        = volatility_filter
        self.volatility_period        = volatility_period
        self.atr_period               = atr_period
        self.atr_stop_loss_multiplier = atr_stop_loss_multiplier

    def backtest(self, stock: nit.StockData, show_output: bool = False) -> tuple[list]:
        if show_output: print("Beginning SoloMini Backtest")
        indicators = [
            "ema" + str(self.small_ema_period),
            "ema" + str(self.large_ema_period),
            "atr" + str(self.atr_period),
            "ema50",
            "ema100"
        ]

        if show_output: print("Preprocessing indicators...")
        stock.preprocess_indicators(indicators)
        if show_output: print("Preprocessed indicators.")

        if show_output: print("Backtesting strategy")
        lookback_index = 0
        lookback_high = 0
        close = stock['Close']
        ema_small, ema_large, atr, ema_50, ema_100 = stock[*indicators]
        stop_loss = 0
        entries = []
        exits = []
        holding = False
        hold_price = 0
        volatile_price = 0

        i = 0
        end = close.size
        while i < end:
            # Update lookback
            lookback_index = max(i - self.high_lookback_period, 0)
            lookback_high = max(close.iloc[lookback_index:i + 1])
            
            # Update volatile price
            volatile_price = close.iloc[max(i - self.volatility_period, 0)]

            # Entry conditions
            # Small ema passes large ema
            if (holding is False):
                if (ema_small.iloc[i] > ema_large.iloc[i]):
                    # Reached a new high in the lookback period
                    if (close.iloc[i] == lookback_high):
                        if not (close.iloc[i] > (1 + self.volatility_filter) * volatile_price):
                            if (ema_50.iloc[i] > ema_100.iloc[i]):
                                entries.append(close.index[i])
                                stop_loss = 0
                                hold_price = close.iloc[i]
                                holding = True
            
            # Exit conditions
            if (holding is True):
                stop_loss = max(stop_loss, nit.StopLoss.atr_long(close.iloc[i], atr.iloc[i], self.atr_stop_loss_multiplier))
                if (close.iloc[i] < stop_loss) or (close.iloc[i] > 1.2 * hold_price):
                    exits.append(close.index[i])
                    hold_price = 0
                    holding = False

            i += 1
            
        
        if show_output: print("Finished backtest")

        return (entries, exits)
    