import pandas as pd

def buy_low(boll_low: pd.Series,
            boll_high: pd.Series,
            close: pd.Series) -> list:
    buys = []

    holding = False

    i = 0
    end = boll_low.size
    while i < end:
        # Not currently holding
        if holding is False:
            if close.iloc[i] <= boll_low.iloc[i]:
                holding = True
                buys.append(close.index[i])

        # Mark as sold
        if close.iloc[i] >= boll_high.iloc[i]:
            holding = False

    return buys

def sell_high(buys: list,
              boll_low: pd.Series,
              boll_high: pd.Series,
              close: pd.Series) -> list:
    sells = []

    holding = False

    i = 0
    end = boll_low.size
    while i < end:
        # Holding
        if holding is True:
            if close.iloc[i] >= boll_high.iloc[i]:
                holding = False
                sells.append(close.index[i])

        # Mark as bought
        if close.iloc[i] <= boll_low.iloc[i]:
            holding = True

    return sells

