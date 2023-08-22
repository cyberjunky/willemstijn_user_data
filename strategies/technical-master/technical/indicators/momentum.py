"""
Momentum indicators
"""

########################################
#
# Momentum Indicator Functions
#

# ADX                  Average Directional Movement Index
# ADXR                 Average Directional Movement Index Rating
# APO                  Absolute Price Oscillator
# AROON                Aroon
# AROONOSC             Aroon Oscillator
# BOP                  Balance Of Power

# CCI                  Commodity Channel Index

# CMO                  Chande Momentum Oscillator

# DX                   Directional Movement Index
# MACD                 Moving Average Convergence/Divergence
# MACDEXT              MACD with controllable MA type
# MACDFIX              Moving Average Convergence/Divergence Fix 12/26
# MFI                  Money Flow Index
# MINUS_DI             Minus Directional Indicator
# MINUS_DM             Minus Directional Movement

# MOM                  Momentum

# PLUS_DI              Plus Directional Indicator
# PLUS_DM              Plus Directional Movement
# PPO                  Percentage Price Oscillator
# ROC                  Rate of change : ((price/prevPrice)-1)*100
# ROCP                 Rate of change Percentage: (price-prevPrice)/prevPrice
# ROCR                 Rate of change ratio: (price/prevPrice)
# ROCR100              Rate of change ratio 100 scale: (price/prevPrice)*100
# RSI                  Relative Strength Index
# STOCH                Stochastic
# STOCHF               Stochastic Fast
# STOCHRSI             Stochastic Relative Strength Index
# TRIX                 1-day Rate-Of-Change (ROC) of a Triple Smooth EMA

# ULTOSC               Ultimate Oscillator


# WILLR                Williams' %R
def williams_percent(dataframe, period=14):
    highest_high = dataframe["high"].rolling(period).max()
    lowest_low = dataframe["low"].rolling(period).min()
    wr = (highest_high - dataframe["close"]) / (highest_high - lowest_low) * -100
    return wr
