import pandas as pd

def buy(dema: pd.Series,
        close: pd.Series) -> list:
    buys = []

    upwards = False
    
    i = 1
    end = close.size
    while i < end:
        if dema.iloc[i] >= 0 and upwards is False:
            upwards = True
            buys.append(close.index[i])

        if dema.iloc[i] < 0:
            upwards = False
        
        i += 1

    return buys

def sell(buys: list,
         dema: pd.Series,
         close: pd.Series) -> list:
    sells = []

    upwards = False

    i = 0
    end = close.size
    while i < end:
        if dema.iloc[i] <= 0 and upwards is True:
            upwards = False
            sells.append(close.index[i])
            
        if dema.iloc[i] > 0:
            upwards = True

        i += 1

    return sells


