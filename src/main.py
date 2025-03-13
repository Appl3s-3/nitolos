import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import nitolos as nit

from strategies import solo
from strategies import jono
from strategies import test1

def atr_test():
    pls = nit.StockData('PLS', datetime.datetime(2018, 1, 1))

    pls.preprocess_indicator('tr')
    pls.preprocess_indicator('atr')
    pls.preprocess_indicator('ema20')

    fig = plt.figure()
    ax = fig.add_subplot()
    ax.plot(pls.data.index,
            pls.data['Close'],
            'k:',
            label='Close')
    # ax.plot(pls.data.index,
    #         pls.data['ema20'],
    #         'g-',
    #         label='ema20')

    # ax.plot(pls.data.index,
    #         pls.data['atr'],
    #         'g-',
    #         label='atr')
    ax.plot(pls.data.index,
            pls.data['custom_atr'],
            'c-',
            label='custom_atr')

    ax.margins(x=0, y=0)
    ax.legend()

    plt.show()
    

def main():
    # atr_test()
    # return
    
    stock = 'TSLA'
    pls = nit.StockData(stock, datetime.datetime(2016, 1, 1), ticker_postfix = '')

    john = nit.Strategy(jono.buy,
                        jono.sell,
                        ('Close', ),
                        ('Close', ))
    b, s, v = john.run_and_evaluate(pls)
    # print(v)
    # return

    # Create and run a strategy
    solotin100 = nit.Strategy(solo.buy,
                              solo.sell,
                              ('ema50', 'ema100', 'Close'),
                              ('ema50', 'ema100', 'Close'))
    solotin150 = nit.Strategy(solo.buy,
                              solo.sell,
                              ('ema50', 'ema150', 'Close'),
                              ('ema50', 'ema150', 'Close'))
    solotin200 = nit.Strategy(solo.buy,
                              solo.sell,
                              ('ema50', 'ema200', 'Close'),
                              ('ema50', 'ema200', 'Close'))

    test_strat1 = nit.Strategy(test1.buy,
                               test1.sell,
                               ('d_ema200', 'Close'),
                               ('d_ema200', 'Close'))

    # buys, sells = test_strat1.run(pls)
    solotins = []
    value_array = []
    solo_buys = []
    solo_sells = []
    lema = ''
    indent = -1

    for i in range(20, 301, 10):
        value_array.insert(0, [])
        large_ema = 'ema' + str(i)
        for j in range(10, 151, 10):
            small_ema = 'ema' + str(j)
            if (j >= i):
                value_array[0].append(np.nan)
                continue

            # Run strategy
            strategy = nit.Strategy(solo.buy,
                                    solo.sell,
                                    (small_ema, large_ema, 'Close'),
                                    (small_ema, large_ema, 'Close'))
            b, s, v = strategy.run_and_evaluate(pls)
            solotins.append((
                strategy,
                small_ema,
                large_ema
            ))

            # Store results
            solo_buys.append(b)
            solo_sells.append(s)
            value_array[0].append(v)

            # Display
            if lema != large_ema:
                lema = large_ema
                indent += 1
            if int(large_ema[3:]) % 20 == 0:
                indent = 0
            indents = '\t' * indent
            # print(f"{indents}Large EMA {large_ema[3:]}, Small EMA {small_ema[3:]}, Value {v}")

    # Display heatmap
    values = np.array(value_array)
    values[values < 1] = 0
    print(f"Min: {np.nanmin(values)}, Max: {np.nanmax(values)}")
    
    fig = plt.figure()
    ax = fig.add_subplot()
    im = ax.imshow(values)
    ax.set_xticks(np.arange(len(value_array[0])), np.arange(10, 151, 10))
    ax.set_yticks(np.arange(len(value_array)), np.arange(300, 19, -10))
    ax.set_xlabel("Small EMA")
    ax.set_ylabel("Large EMA")
    ax.set_title(f"Heatmap of {stock}")
    fig.tight_layout()
    plt.show()
    

    return

    
    bs100, ss100 = solotin100.run_and_evaluate(pls)
    print("Finished running solotin100\n\n")
    bs150, ss150 = solotin150.run_and_evaluate(pls)
    print("Finished running solotin150\n\n")
    bs200, ss200 = solotin200.run_and_evaluate(pls)
    print("Finished running solotin200")

    # Plot stock data
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.plot(pls.data.index,
            pls.data['Close'],
            'k:',
            label='Close')
    ax.plot(pls.data.index,
            pls.data['ema200'],
            'g-',
            label='ema200')
    # ax.plot(pls.data.index,
    #         pls.data['ema100'],
    #         'c-',
    #         label='ema100')

    # Plot buy and sell dates
    def plot_bs(ax, buys, sells, b_fmt = 'bo', s_fmt = 'ro'):
        for i in buys:
            ax.plot(pd.Timestamp(i),
                    pls.data['Close'][i],
                    b_fmt,
                    markersize=8)

        for i in sells:
            ax.plot(pd.Timestamp(i),
                    pls.data['Close'][i],
                    s_fmt,
                    markersize=16)

    plot_bs(ax, bs100, ss100, 'bo', 'ro')
    plot_bs(ax, bs150, ss150, 'co', 'mo')
    plot_bs(ax, bs200, ss200, 'go', 'yo')

    ax.margins(x=0, y=0)
    ax.legend()

    plt.show()

if __name__ == '__main__':
    main()
