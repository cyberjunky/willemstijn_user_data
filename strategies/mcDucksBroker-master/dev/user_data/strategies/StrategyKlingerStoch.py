import freqtrade.vendor.qtpylib.indicators as qtpylib
from numpy import ceil
from pandas.core.series import Series
from freqtrade import data
from freqtrade.exchange import timeframe_to_minutes
from freqtrade.strategy import IStrategy
from pandas.core.frame import DataFrame
from mcDuck.custom_indicators import merge_dataframes, stoch_rsi_smooth, klinger_oscilator
from functools import reduce


"""
Buys when the 1D Klinger and de 4H Klinger crosses
"""


class StrategyKlingerStoch(IStrategy):
    INTERFACE_VERSION = 2

    # Optimal ticker interval for the strategy.
    timeframe = '5m'
    timeframe_main = '4h'
    timeframe_support = '1d'

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = False

    # These values can be overridden in the "ask_strategy" section in the config.
    use_sell_signal = False
    sell_profit_only = False
    ignore_roi_if_buy_signal = False
    ignore_buying_expired_candle_after = 30
    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 55

    # ROI table:
    minimal_roi = {
        "0": 0.754,
        "1735": 0.275,
        "2670": 0.071,
        "3258": 0
    }

    # Stoploss:
    stoploss = -0.05

    # Trailing stop:
    trailing_stop = True
    trailing_stop_positive = 0.318
    trailing_stop_positive_offset = 0.397
    trailing_only_offset_is_reached = True

    def informative_pairs(self):
        pairs = self.dp.current_whitelist()
        informative_pairs = [(pair, self.timeframe_main) for pair in pairs] + \
                            [(pair, self.timeframe_support) for pair in pairs]
        return informative_pairs

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        if self.config['runmode'].value in ('backtest', 'hyperopt'):
            assert (timeframe_to_minutes(self.timeframe) <=
                    5), "Backtest this strategy in 5m or 1m timeframe."

        if not self.dp:
            return dataframe

        dataframe_main = self.dp.get_pair_dataframe(
            pair=metadata['pair'],
            timeframe=self.timeframe_main
        )
        [dataframe_main["main_kvo"], dataframe_main["main_ks"]] = \
            klinger_oscilator(dataframe_main)

        dataframe_main = stoch_rsi_smooth(dataframe_main)

        dataframe = merge_dataframes(
            source=dataframe_main,
            sourceTimeframe=self.timeframe_main,
            destination=dataframe,
            destinationTimeFrame=self.timeframe
        )

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        minimum_coin_price = 0.0000015
        conditions = []
        last_candle_main = dataframe.shift(self.shift_value(self.timeframe_main))
        last_candle_support = dataframe.shift(self.shift_value(self.timeframe_support))
        conditions.append(dataframe["volume"] > 0)
        conditions.append(dataframe["close"] > minimum_coin_price)
        conditions.append(dataframe["stochk"] > last_candle_main["stochk"])
        conditions.append((last_candle_main['main_kvo'] < last_candle_main['main_ks']) &
                          (dataframe['main_kvo'] > dataframe['main_ks']))
        if('btc_stochk' in dataframe.columns):
            conditions.append(dataframe["btc_stochk"] > last_candle_main["btc_stochk"])
        if('btc_kvo' in dataframe.columns):
            conditions.append(dataframe["btc_kvo"] > last_candle_support["btc_ks"])
        if conditions:
            dataframe.loc[reduce(lambda x, y: x & y, conditions), "buy"] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        last_candle_main = dataframe.shift(self.shift_value(self.timeframe_main))
        dataframe.loc[(
            (dataframe["stochk"] < last_candle_main["stochk"]) &
            ((last_candle_main['main_kvo'] > last_candle_main['main_ks']) &
             (dataframe['main_kvo'] < dataframe['main_ks'])) &
            (dataframe["volume"] > 0)
        ), "sell"] = 0
        return dataframe

    def shift_value(self, timeframe: str) -> int:
        return int(ceil(timeframe_to_minutes(timeframe) / timeframe_to_minutes(self.timeframe)))
