import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from nitolos import Nitolos

def buy_function(small_ema, large_ema, data):
    buys = []
    i = 0
    end = small_ema.size
    sixty_day = []
    sixty_day_high = 0
    last_time_bought = 999999
    last_time_bought_index = 0
    while i < end - 1:
        if len(sixty_day) > 60:
            sixty_day.pop(0)
        sixty_day.append(data['Close'].iloc[i])
        sixty_day_high = max(sixty_day)
        # if (small_ema.iloc[i] < large_ema.iloc[i]):
            # if (large_ema.iloc[i + 1] < small_ema.iloc[i + 1]):
        if (large_ema.iloc[i + 1] < small_ema.iloc[i + 1]):
            if (data['Close'].iloc[i] == sixty_day_high):
                last_time_bought = i - last_time_bought_index
                if last_time_bought > 20:
                    last_time_bought_index = i
                    buys.append(i)
        i += 1
    # Buy when small ema greater than large ema and 
    # 60 day high is met and
    # last time bought is greater than 20 days

    # Chun Buy conditions
    # DMI buy when negative signal is above positive signal, follow signal when strength is above 40
    # MACD (ma convergence, divergence), similar to above
    
    return buys

def sell_function(small_ema, large_ema, buy_dates, data):
    sells = []
    i = 0
    end = small_ema.size
    trading = False
    trading_days = []
    trading_high = 0
    trading_high_index = 0
    while i < end - 1:
        if i in buy_dates:
            trading_high_index = i
            trading = True
        if trading:
            trading_days.append(data['Close'].iloc[i])
            trading_high = max(trading_days)
        
        # if ((large_ema.iloc[i] < small_ema.iloc[i]) and (small_ema.iloc[i + 1] < large_ema.iloc[i + 1])) or (trading_high * 0.75) > (data['Close'].iloc[i]):
        if (trading_high * 0.75) > (data['Close'].iloc[i]):
            sells.append(i + 1)
            trading = False
            trading_high = 0
            trading_days = []
            trading_high_index = 0
        i += 1

    # Sell conditions
    # 25% stop loss from trading time high = all time high since bought
    # ATR stop loss, 10x multiplier (not implemented)

    # Chun Sell conditions
    # DMI sell when negative signal is above positive signal, follow signal when strength is above 40
    return sells


# def main():
#     pls = yf.Ticker("PLS.ax")

#     #pilbara_info = pls.info
#     #print(pilbara_info)

#     print("Obtaining Data")

#     df = pls.history(start="2016-01-01",
#                      end="2017-07-01",
#                      interval="1d")['Close'].to_frame()

#     df['SMA20'] = df['Close'].rolling(20).mean()
#     df['SMA200'] = df['Close'].rolling(200).mean()
#     df['STD20'] = df['Close'].rolling(20).std()
#     df['PTC'] = df['Close'].pct_change()
#     df['Upper BOLL'] = df['SMA20'] + 2 * df['STD20']
#     df['Lower BOLL'] = df['SMA20'] - 2 * df['STD20']
#     df.dropna(inplace=True)

#     print("Plotting Figure")

#     fig = plt.figure()
#     plt.fill_between(df.axes[0], df['Upper BOLL'], df['Lower BOLL'], alpha=0.4)
#     df['Close'].plot()
#     df['SMA20'].plot()
#     df['SMA200'].plot()
#     # df['PTC'].plot()

#     print("Writing Figure")

#     plt.savefig(fname="hello.png")


#     print("Second parsing")

#     df['sma200 gradient'] = df['SMA200'].pct_change()
#     df['sma200 gradient sma50'] = df['sma200 gradient'].rolling(50).mean()
#     df.dropna(inplace=True)

#     fig2 = plt.figure()

#     df['sma200 gradient'].plot()
#     df['sma200 gradient sma50'].plot()

#     plt.savefig(fname="bye.png")
#     plt.show()

def main2():
    TODAY = datetime.today().strftime("%Y-%m-%d")
    pls = Nitolos("SQ2.ax", "2014-08-01", TODAY)
    pls.calculate_ema(50)
    pls.calculate_ema(100)

    buys = buy_function(pls.data['EMA50'], pls.data['EMA100'], pls.data)
    buy_dates = []
    for i in buys:
        buy_dates.append(pls.data.index[i])

    sells = sell_function(pls.data['EMA50'], pls.data['EMA100'], buys, pls.data)
    sell_dates = []
    for i in sells:
        sell_dates.append(pls.data.index[i])

    print("buys")
    print(buy_dates)
    print("sells")
    print(sell_dates)

    interactions = []
    for i in buys:
        interactions.append((i, 1))

    for i in sells:
        interactions.append((i, 0))

    interactions.sort(key=lambda x: x[0])

    value = 1
    hold_value = 0
    holding = False
    losses = 0
    wins = 0
    neutral = 0
    for i in interactions:
        if i[1] == 1 and holding == False:
            holding = True
            hold_value = pls.data['Close'].iloc[i[0]]
            print(f"Bought at {hold_value}")
        if i[1] == 1 and holding == True:
            print("Bought again, value not included in total")
        if i[1] == 0:
            holding = False
            if hold_value == 0:
                print("Ignoring invalid sell")
                continue
            increase = (pls.data['Close'].iloc[i[0]] / hold_value)
            if (increase < 1):
                losses += 1
            elif (increase > 1):
                wins += 1
            else:
                neutral += 1
            value *= (pls.data['Close'].iloc[i[0]] / hold_value)
            hold_value = 0
            print(f"Sold at {pls.data['Close'].iloc[i[0]]}")

    print(f"Final % Gain: {value}")
    print(f"Wins: {wins}, Losses: {losses}, Neutral: {neutral}")
    
    # pls.define_buy_order(buy_function, "EMA20", "EMA50")
    # pls.define_sell_order(sell_function, "EMA20", "EMA50")
    # pls.simulate("2016-01-01", "2017-01-01")

    # pls.results()
    # pls.plot()

    fig = plt.figure()
    ax = fig.add_subplot()
    ax.plot(pls.data.index,
            pls.data['Close'],
            'k-')
    # pls.data['Close'].plot()

    pls.data['EMA50'].plot()
    pls.data['EMA100'].plot()
    for i in buy_dates:
        ax.plot(pd.Timestamp(i),
                pls.data['Close'][i],
                'bo')
        # plt.axvline(pd.Timestamp(i), color="b")

    for i in sell_dates:
        ax.plot(pd.Timestamp(i),
                pls.data['Close'][i],
                'ro')
        # plt.axvline(pd.Timestamp(i), color="r")

    plt.show()
    

if __name__ == '__main__':
    main2()
