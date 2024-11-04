import pandas as pd
import matplotlib.pyplot as plt
import datetime
import nitolos as nit

def main():
    def solo_buy(ema_small: pd.Series,
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

    def solo_sell(buys: list,
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

            i += 1

        return sells

    pls = nit.StockData('PLS', datetime.datetime(2018, 1, 1))

    # Create and run a strategy
    solotin = nit.Strategy(solo_buy,
                           solo_sell,
                           ('ema50', 'ema100', 'Close'),
                           ('ema50', 'ema100', 'Close'))
    buys, sells = solotin.run(pls)

    # Plot stock data
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.plot(pls.data.index,
            pls.data['Close'],
            'k:',
            label='Close')
    ax.plot(pls.data.index,
            pls.data['ema50'],
            'g-',
            label='ema50')
    ax.plot(pls.data.index,
            pls.data['ema100'],
            'c-',
            label='ema100')

    # Plot buy and sell dates
    for i in buys:
        ax.plot(pd.Timestamp(i),
                pls.data['Close'][i],
                'bo',
                markersize=5)

    for i in sells:
        ax.plot(pd.Timestamp(i),
                pls.data['Close'][i],
                'ro',
                markersize=5)

    ax.margins(x=0, y=0)
    ax.legend()

    plt.show()

if __name__ == '__main__':
    main()
