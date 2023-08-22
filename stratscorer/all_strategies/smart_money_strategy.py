import numpy
import talib.abstract as ta
from pandas import DataFrame
from technical.indicators import chaikin_money_flow
from freqtrade.strategy import (DecimalParameter, IStrategy, IntParameter)


# this strat buy deep and sell up and it's not smart sorry
# u or gain profit or just hodl(when drowdown)
# i fixed some false signal, thank EMA(200)
# when long drowdown, some time u get only sell_profit_offset! Because get false sell signal bellow buy price.
# but u have no stop-loss and sell only profit

# lets plot:
# freqtrade plot-dataframe -s smart_money_strategy --timerange 20210601- -i 1h -p DOT/USDT --indicators1 ema_200 --indicators2 cmf mfi

# params hyper-optable, just use class smart_money_strategy_hyperopt
# freqtrade hyperopt --hyperopt-loss SharpeHyperOptLoss --strategy smart_money_strategy_hyperopt --spaces buy sell --timerange 20210601- --dry-run-wallet 160 --stake 12 -i 1h -e 1000


#class smart_money_strategy(IStrategy):
    # Minimal ROI designed for the strategy.
#    minimal_roi = {
#        "0": 10
#    }

    # Stoploss:
#    stoploss = -1
    # Optimal timeframe for the strategy
#    timeframe = '1h'
#    sell_profit_only = True
#    sell_profit_offset = 0.01

    # enumeration of indicators
#    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Chaikin
#        dataframe['cmf'] = chaikin_money_flow(dataframe, period=20)

        # MFI
#        dataframe['mfi'] = ta.MFI(dataframe)

        # EMA
#        dataframe['ema_200'] = ta.EMA(dataframe, timeperiod=200)
#        return dataframe

    # params for buy
#    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
#        dataframe.loc[
#            (
#                    (dataframe['close'] < dataframe['ema_200']) &
#                    (dataframe['mfi'] < 35) &
#                    (dataframe['cmf'] < -0.07)
#            ),
#            'buy'] = 1
#        return dataframe

    # params for sell
#    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
#        dataframe.loc[
#            (
#                    (dataframe['close'] > dataframe['ema_200']) &
#                    (dataframe['mfi'] > 70) &
#                    (dataframe['cmf'] > 0.20)
#            ),
#            'sell'] = 1
        #         dataframe.to_csv('./sell_result.csv')
#        return dataframe


# FOR HYPEROPT
class smart_money_strategy_hyperopt(IStrategy):
    # ROI table:
    minimal_roi = {
        "0": 10
    }

    # Stoploss:
    stoploss = -1
    # Optimal timeframe for the strategy
    timeframe = '1h'
    sell_profit_only = True
    sell_profit_offset = 0.01

    # buy params
    buy_mfi = IntParameter(20, 60, default=35, space="buy")
    buy_cmf = DecimalParameter(-0.4, -0.01, decimals=2, default=-0.07, space="buy")

    # sell params
    sell_mfi = IntParameter(50, 95, default=70, space="sell")
    sell_cmf = DecimalParameter(0.1, 0.6, decimals=2, default=0.2, space="sell")

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Chaikin
        dataframe['cmf'] = chaikin_money_flow(dataframe, period=20)

        # MFI
        dataframe['mfi'] = ta.MFI(dataframe)

        # EMA
        dataframe['ema_200'] = ta.EMA(dataframe, timeperiod=200)
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                    (dataframe['close'] < dataframe['ema_200']) &
                    (dataframe['mfi'] < self.buy_mfi.value) &
                    (dataframe['cmf'] < self.buy_cmf.value)
            ),
            'buy'] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                    (dataframe['close'] > dataframe['ema_200']) &
                    (dataframe['mfi'] > self.sell_mfi.value) &
                    (dataframe['cmf'] > self.sell_cmf.value)
            ),
            'sell'] = 1
        return dataframe
