import pandas as pd

"""
This is the long term ema strategy proposed by Solotin.
It is also the first strategy Solotin proposed.
"""

def buy(ema_small: pd.Series,
        ema_large: pd.Series,
        close: pd.Series) -> list:
    buys = []

    sixty_day = []
    sixty_day_high = 0
    last_bought = 0
    
    i = 1
    end = close.size
    while i < end:
        # Maintain sixty_day buffer
        if len(sixty_day) > 60:
            sixty_day.pop(0)
        sixty_day.append(close.iloc[i])
        sixty_day_high = max(sixty_day)

        # Smaller ema passes larger ema
        # if ema_small.iloc[i - 1] < ema_large.iloc[i - 1]:
            # if ema_small.iloc[i] >= ema_large.iloc[i]:

        # Small ema greater than large ema
        if ema_small.iloc[i] > ema_large.iloc[i]:
            # 60 day high
            if (close.iloc[i] == sixty_day_high):
                # Last time bought was over 20 days ago
                if (i - last_bought) > 20:
                    buys.append(ema_small.index[i])
                    last_bought = i
        i += 1

    return buys

def sell(buys: list,
         ema_small: pd.Series,
         ema_large: pd.Series,
         close: pd.Series) -> list:
    sells = []

    trading = False
    trading_high = 0

    i = 0
    end = close.size
    while i < end:
        # Determine trading from buys
        if close.index[i] in buys:
            trading = True
        
        # Obtain trading high after buy
        if trading:
            trading_high = max(trading_high, close.iloc[i])

            # 25% Stop loss exceeded
            if (trading_high * 0.75) >= close.iloc[i]:
                sells.append(close.index[i])
                trading = False
                trading_high = 0


        # atr 21 days
        # ATR x 8 (small) or 10 (large)
        # subtract peak since bought
        # that is stop loss
        

        
        i += 1

    return sells
