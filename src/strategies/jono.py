import pandas as pd


# def buy(close: pd.Series) -> list:
#     buys = []

#     sixty_day = []
#     sixty_day_high = 0
#     last_bought = 0
    
#     i = 1
#     end = close.size
#     while i < end:
#         # Maintain sixty_day buffer
#         if len(sixty_day) > 30:
#             sixty_day.pop(0)
#         sixty_day.append(close.iloc[i])
#         sixty_day_high = max(sixty_day)

#         # 60 day high
#         if (close.iloc[i] == sixty_day_high):
#             # Last time bought was over 20 days ago
#             if (i - last_bought) > 20:
#                 buys.append(close.index[i])
#                 last_bought = i

#         i += 1

#     return buys

# def sell(buys: list,
#          close: pd.Series) -> list:
#     sells = []

#     sixty_day = []
#     sixty_day_high = 0
#     last_bought = 0

#     i = 0
#     end = close.size
#     while i < end:
#         # Maintain sixty_day buffer
#         if len(sixty_day) > 300:
#             sixty_day.pop(0)
#         sixty_day.append(close.iloc[i])
#         sixty_day_high = max(sixty_day)

#         # 60 day high
#         if (close.iloc[i] == sixty_day_high):
#             # Last time bought was over 20 days ago
#             if (i - last_bought) > 20:
#                 sells.append(close.index[i])
#                 last_bought = i

#         i += 1

#     return sells
