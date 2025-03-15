import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import nitolos as nit

from strategies import solo
from strategies import solo_mini
from strategies import jono
from strategies import test1

def plot_nested_comparisons(nested_data, group_names=None, title="Group Comparisons", 
                           xlabel="Categories", ylabel="Values", figsize=(12, 8),
                           bar_colors=None, rotation=45, layout=None, share_y=True):
    n_groups = len(nested_data)
    
    if group_names is None:
        group_names = [f"Group {i+1}" for i in range(n_groups)]
    
    if bar_colors is None:
        bar_colors = ['orange', 'pink', 'cyan', 'red', 'purple']
    
    if layout is None:
        n_cols = min(3, n_groups)
        n_rows = (n_groups + n_cols - 1) // n_cols
    else:
        n_rows, n_cols = layout
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize, sharex=False, sharey=share_y)
    
    if n_groups == 1:
        axes = np.array([axes])
    
    axes = np.array(axes).flatten()
    
    for i in range(n_groups, len(axes)):
        axes[i].set_visible(False)
    
    for i, (group_data, group_name) in enumerate(zip(nested_data, group_names)):
        ax = axes[i]
        
        categories = [name for name, _ in group_data]
        values = [value for _, value in group_data]
        x = np.arange(len(categories))
        
        for j, (cat, val) in enumerate(zip(categories, values)):
            color_idx = j % len(bar_colors)
            ax.bar(x[j], val, width=0.7, color=bar_colors[color_idx])
        
        ax.set_title(group_name)
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=rotation)
        
        if i % n_cols == 0:
            ax.set_ylabel(ylabel)
        
        if i >= n_groups - n_cols:
            ax.set_xlabel(xlabel)
        
        ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.suptitle(title, fontsize=16)
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    
    return fig, axes

def new_world_main():
    show_charts = False
    stock_codes = ["CBA", "NAB", "WAM", "TLC", "DRO", "PLS", "BHP", "NHC", "WAF"]
    results = []

    for stock_code in stock_codes:
        stock_results = []
        results.append(stock_results)
        print()
        stock_data = nit.StockData(stock_code, datetime.datetime(2016, 1, 1))

        minis = [
            solo_mini.SoloMini(10, 20),
            solo_mini.SoloMini(10, 30),
            solo_mini.SoloMini(10, 40)
        ]
        mini_names = ["10/20", "10/30", "10/40"]
        for k, mini in enumerate(minis):
            entries, exits = mini.backtest(stock_data, False)

            # Order the interactions
            interactions = []
            for i in entries:
                interactions.append((i, 'b'))
            for i in exits:
                interactions.append((i, 's'))
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
                        hold_value = stock_data.data.loc[date, 'Close']
                        # print(f"bought at {hold_value}")

                # Sell signal
                if signal == 's':
                    # Not holding
                    if hold_value == 0:
                        # print("ignoring invalid sell")
                        continue

                    # Calculate outcome of sell
                    outcome = (stock_data.data.loc[date, 'Close'] / hold_value)

                    losses  += int(outcome < 1)
                    wins    += int(outcome > 1)
                    neutral += int(outcome == 1)

                    value *= outcome
                    hold_value = 0

                    # print(f"sold at {data.data.loc[date, 'Close']} for {outcome} result")
                    # print()

            stock_results.append((mini_names[k], value))
            print(f"{stock_code.upper()} Final Value: {value:.5f}")
            if neutral > 0:
                print(f"Wins: {wins}, Losses: {losses}, Neutral: {neutral}")
            else:
                print(f"| Wins: {wins} | Losses: {losses} |")

            if show_charts:
                # print("Entries: ", entries)
                # print("Exits: ", exits)

                # Plot stock data
                fig = plt.figure()
                ax = fig.add_subplot()
                ax.plot(stock_data.data.index,
                        stock_data.data['Close'],
                        'k:',
                        label='Close')
                ax.plot(stock_data.data.index,
                        stock_data.data['ema20'],
                        'g-',
                        label='ema20')
                ax.plot(stock_data.data.index,
                        stock_data.data['ema10'],
                        'y-',
                        label='ema10')
                # ax.plot(pls.data.index,
                #         pls.data['ema100'],
                #         'c-',
                #         label='ema100')

                # Plot buy and sell dates
                def plot_bs(ax, buys, sells, b_fmt = 'bo', s_fmt = 'ro'):
                    for i in buys:
                        ax.plot(pd.Timestamp(i),
                                stock_data.data['Close'][i],
                                b_fmt,
                                markersize=8)

                    for i in sells:
                        ax.plot(pd.Timestamp(i),
                                stock_data.data['Close'][i],
                                s_fmt,
                                markersize=8)

                plot_bs(ax, entries, exits, 'bo', 'ro')

                ax.margins(x=0, y=0)
                ax.grid(True)
                ax.legend()

                # Set monthly ticks
                ax.xaxis.set_major_locator(mdates.MonthLocator())  # Major ticks on months
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # Format as 'Jan 2023'
                fig.autofmt_xdate()  # Auto-rotate date labels for better readability

                plt.title(f"Mini Solo Strategy: {stock_code.upper()}")
                plt.ylabel("Price")
                plt.xlabel("Date")

                plt.show()

    fig, ax = plot_nested_comparisons(results, group_names=stock_codes)
    plt.show()
    return


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
    
    stock = 'PLS'
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
    
    bs100, ss100, v = solotin100.run_and_evaluate(pls)
    print("Finished running solotin100\n\n")
    bs150, ss150, v = solotin150.run_and_evaluate(pls)
    print("Finished running solotin150\n\n")
    bs200, ss200, v = solotin200.run_and_evaluate(pls)
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
    new_world_main()
