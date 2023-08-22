# --- Do not remove these libs --------------------------------------
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
import freqtrade.vendor.qtpylib.indicators as qtpylib
from freqtrade.optimize.hyperopt_interface import IHyperOpt
from skopt.space import Categorical, Dimension, Integer, Real  # noqa
from typing import Any, Callable, Dict, List
# -------------------------------------------------------------------


class MoniGoManiHyperOpt(IHyperOpt):
    """
    ####################################################################################
    ####                                                                            ####
    ###                  MoniGoManiHyperOpt for v0.8.0 by Rikj000                    ###
    ####                                                                            ####
    ####################################################################################
    """

    @staticmethod
    def indicator_space() -> List[Dimension]:
        """
        Define your Hyperopt space for searching buy strategy parameters.
        """
        return [
            # Decide on which kinds of trends the bot should trade or hold
            Categorical([True, False], name='buy___trades_when_downwards'),
            Categorical([True, False], name='buy___trades_when_sideways'),
            Categorical([True, False], name='buy___trades_when_upwards'),
            # Downwards Trend
            # ------------
            # Total Buy Signal Percentage needed for a signal to be positive
            Integer(0, 100, name='buy__downwards_trend_total_signal_needed'),
            # Buy Signal Weight Influence Table
            Integer(0, 100, name='buy_downwards_trend_adx_strong_up_weight'),
            Integer(0, 100, name='buy_downwards_trend_rsi_weight'),
            Integer(0, 100, name='buy_downwards_trend_macd_weight'),
            Integer(0, 100, name='buy_downwards_trend_sma_short_golden_cross_weight'),
            Integer(0, 100, name='buy_downwards_trend_ema_short_golden_cross_weight'),
            Integer(0, 100, name='buy_downwards_trend_sma_long_golden_cross_weight'),
            Integer(0, 100, name='buy_downwards_trend_ema_long_golden_cross_weight'),
            Integer(0, 100, name='buy_downwards_trend_bollinger_bands_weight'),
            Integer(0, 100, name='buy_downwards_trend_vwap_cross_weight'),
            # Sideways Trend
            # ------------
            # Total Buy Signal Percentage needed for a signal to be positive
            Integer(0, 100, name='buy__sideways_trend_total_signal_needed'),
            # Buy Signal Weight Influence Table
            Integer(0, 100, name='buy_sideways_trend_adx_strong_up_weight'),
            Integer(0, 100, name='buy_sideways_trend_rsi_weight'),
            Integer(0, 100, name='buy_sideways_trend_macd_weight'),
            Integer(0, 100, name='buy_sideways_trend_sma_short_golden_cross_weight'),
            Integer(0, 100, name='buy_sideways_trend_ema_short_golden_cross_weight'),
            Integer(0, 100, name='buy_sideways_trend_sma_long_golden_cross_weight'),
            Integer(0, 100, name='buy_sideways_trend_ema_long_golden_cross_weight'),
            Integer(0, 100, name='buy_sideways_trend_bollinger_bands_weight'),
            Integer(0, 100, name='buy_sideways_trend_vwap_cross_weight'),
            # Upwards Trend
            # ------------
            # Total Buy Signal Percentage needed for a signal to be positive
            Integer(0, 100, name='buy__upwards_trend_total_signal_needed'),
            # Buy Signal Weight Influence Table
            Integer(0, 100, name='buy_upwards_trend_adx_strong_up_weight'),
            Integer(0, 100, name='buy_upwards_trend_rsi_weight'),
            Integer(0, 100, name='buy_upwards_trend_macd_weight'),
            Integer(0, 100, name='buy_upwards_trend_sma_short_golden_cross_weight'),
            Integer(0, 100, name='buy_upwards_trend_ema_short_golden_cross_weight'),
            Integer(0, 100, name='buy_upwards_trend_sma_long_golden_cross_weight'),
            Integer(0, 100, name='buy_upwards_trend_ema_long_golden_cross_weight'),
            Integer(0, 100, name='buy_upwards_trend_bollinger_bands_weight'),
            Integer(0, 100, name='buy_upwards_trend_vwap_cross_weight')
        ]

    @staticmethod
    def buy_strategy_generator(params: Dict[str, Any]) -> Callable:
        """
        Define the buy strategy parameters to be used by Hyperopt.
        """

        def populate_buy_trend(dataframe: DataFrame, metadata: dict) -> DataFrame:
            """
            Buy strategy Hyperopt will build and use.
            """

            # Detect if current trend going Downwards / Sideways / Upwards, strategy will respond accordingly
            dataframe.loc[(dataframe['adx'] > 20) &
                          (dataframe['plus_di'] < dataframe['minus_di']), 'trend'] = 'downwards'
            dataframe.loc[dataframe['adx'] < 20, 'trend'] = 'sideways'
            dataframe.loc[(dataframe['adx'] > 20) & (dataframe['plus_di'] > dataframe['minus_di']), 'trend'] = 'upwards'

            # If a Weighted Buy Signal goes off => Bullish Indication, Set to true (=1) and multiply by weight
            # percentage

            # Weighted Buy Signal: ADX above 25 & +DI above -DI (The trend has strength while moving up)
            dataframe.loc[(dataframe['trend'] == 'downwards') & (dataframe['adx'] > 25),
                          'total_buy_signal_strength'] += params['buy_downwards_trend_adx_strong_up_weight']
            dataframe.loc[(dataframe['trend'] == 'sideways') & (dataframe['adx'] > 25),
                          'total_buy_signal_strength'] += params['buy_sideways_trend_adx_strong_up_weight']
            dataframe.loc[(dataframe['trend'] == 'upwards') & (dataframe['adx'] > 25),
                          'total_buy_signal_strength'] += params['buy_upwards_trend_adx_strong_up_weight']

            # Weighted Buy Signal: RSI crosses above 30 (Under-bought / low-price and rising indication)
            dataframe.loc[(dataframe['trend'] == 'downwards') & qtpylib.crossed_above(dataframe['rsi'], 30),
                          'total_buy_signal_strength'] += params['buy_downwards_trend_rsi_weight']
            dataframe.loc[(dataframe['trend'] == 'sideways') & qtpylib.crossed_above(dataframe['rsi'], 30),
                          'total_buy_signal_strength'] += params['buy_sideways_trend_rsi_weight']
            dataframe.loc[(dataframe['trend'] == 'upwards') & qtpylib.crossed_above(dataframe['rsi'], 30),
                          'total_buy_signal_strength'] += params['buy_upwards_trend_rsi_weight']

            # Weighted Buy Signal: MACD above Signal
            dataframe.loc[(dataframe['trend'] == 'downwards') & (dataframe['macd'] > dataframe['macdsignal']),
                          'total_buy_signal_strength'] += params['buy_downwards_trend_macd_weight']
            dataframe.loc[(dataframe['trend'] == 'sideways') & (dataframe['macd'] > dataframe['macdsignal']),
                          'total_buy_signal_strength'] += params['buy_sideways_trend_macd_weight']
            dataframe.loc[(dataframe['trend'] == 'upwards') & (dataframe['macd'] > dataframe['macdsignal']),
                          'total_buy_signal_strength'] += params['buy_upwards_trend_macd_weight']

            # Weighted Buy Signal: SMA short term Golden Cross (Short term SMA crosses above Medium term SMA)
            dataframe.loc[(dataframe['trend'] == 'downwards') & qtpylib.crossed_above(dataframe['sma9'], dataframe[
                'sma50']), 'total_buy_signal_strength'] += params['buy_downwards_trend_sma_short_golden_cross_weight']
            dataframe.loc[(dataframe['trend'] == 'sideways') & qtpylib.crossed_above(dataframe['sma9'], dataframe[
                'sma50']), 'total_buy_signal_strength'] += params['buy_sideways_trend_sma_short_golden_cross_weight']
            dataframe.loc[(dataframe['trend'] == 'upwards') & qtpylib.crossed_above(dataframe['sma9'], dataframe[
                'sma50']), 'total_buy_signal_strength'] += params['buy_upwards_trend_sma_short_golden_cross_weight']

            # Weighted Buy Signal: EMA short term Golden Cross (Short term EMA crosses above Medium term EMA)
            dataframe.loc[(dataframe['trend'] == 'downwards') & qtpylib.crossed_above(dataframe['ema9'], dataframe[
                'ema50']), 'total_buy_signal_strength'] += params['buy_downwards_trend_ema_short_golden_cross_weight']
            dataframe.loc[(dataframe['trend'] == 'sideways') & qtpylib.crossed_above(dataframe['ema9'], dataframe[
                'ema50']), 'total_buy_signal_strength'] += params['buy_sideways_trend_ema_short_golden_cross_weight']
            dataframe.loc[(dataframe['trend'] == 'upwards') & qtpylib.crossed_above(dataframe['ema9'], dataframe[
                'ema50']), 'total_buy_signal_strength'] += params['buy_upwards_trend_ema_short_golden_cross_weight']

            # Weighted Buy Signal: SMA long term Golden Cross (Medium term SMA crosses above Long term SMA)
            dataframe.loc[(dataframe['trend'] == 'downwards') & qtpylib.crossed_above(dataframe['sma50'], dataframe[
                'sma200']), 'total_buy_signal_strength'] += params['buy_downwards_trend_sma_long_golden_cross_weight']
            dataframe.loc[(dataframe['trend'] == 'sideways') & qtpylib.crossed_above(dataframe['sma50'], dataframe[
                'sma200']), 'total_buy_signal_strength'] += params['buy_sideways_trend_sma_long_golden_cross_weight']
            dataframe.loc[(dataframe['trend'] == 'upwards') & qtpylib.crossed_above(dataframe['sma50'], dataframe[
                'sma200']), 'total_buy_signal_strength'] += params['buy_upwards_trend_sma_long_golden_cross_weight']

            # Weighted Buy Signal: EMA long term Golden Cross (Medium term EMA crosses above Long term EMA)
            dataframe.loc[(dataframe['trend'] == 'downwards') & qtpylib.crossed_above(dataframe['ema50'], dataframe[
                'ema200']), 'total_buy_signal_strength'] += params['buy_downwards_trend_ema_long_golden_cross_weight']
            dataframe.loc[(dataframe['trend'] == 'sideways') & qtpylib.crossed_above(dataframe['ema50'], dataframe[
                'ema200']), 'total_buy_signal_strength'] += params['buy_sideways_trend_ema_long_golden_cross_weight']
            dataframe.loc[(dataframe['trend'] == 'upwards') & qtpylib.crossed_above(dataframe['ema50'], dataframe[
                'ema200']), 'total_buy_signal_strength'] += params['buy_upwards_trend_ema_long_golden_cross_weight']

            # Weighted Buy Signal: Re-Entering Lower Bollinger Band after downward breakout
            # (Candle closes below Upper Bollinger Band)
            dataframe.loc[(dataframe['trend'] == 'downwards') & qtpylib.crossed_above(dataframe['close'], dataframe[
                'bb_lowerband']), 'total_buy_signal_strength'] += params['buy_downwards_trend_bollinger_bands_weight']
            dataframe.loc[(dataframe['trend'] == 'sideways') & qtpylib.crossed_above(dataframe['close'], dataframe[
                'bb_lowerband']), 'total_buy_signal_strength'] += params['buy_sideways_trend_bollinger_bands_weight']
            dataframe.loc[(dataframe['trend'] == 'upwards') & qtpylib.crossed_above(dataframe['close'], dataframe[
                'bb_lowerband']), 'total_buy_signal_strength'] += params['buy_upwards_trend_bollinger_bands_weight']

            # Weighted Buy Signal: VWAP crosses above current price (Simultaneous rapid increase in volume and price)
            dataframe.loc[(dataframe['trend'] == 'downwards') & qtpylib.crossed_above(dataframe['vwap'], dataframe[
                'close']), 'total_buy_signal_strength'] += params['buy_downwards_trend_vwap_cross_weight']
            dataframe.loc[(dataframe['trend'] == 'sideways') & qtpylib.crossed_above(dataframe['vwap'], dataframe[
                'close']), 'total_buy_signal_strength'] += params['buy_sideways_trend_vwap_cross_weight']
            dataframe.loc[(dataframe['trend'] == 'upwards') & qtpylib.crossed_above(dataframe['vwap'], dataframe[
                'close']), 'total_buy_signal_strength'] += params['buy_upwards_trend_vwap_cross_weight']

            # Check if buy signal should be sent depending on the current trend

            dataframe.loc[
                (
                        (dataframe['trend'] == 'downwards') &
                        (dataframe['total_buy_signal_strength'] >= params['buy__downwards_trend_total_signal_needed'])
                ) | (
                        (dataframe['trend'] == 'sideways') &
                        (dataframe['total_buy_signal_strength'] >= params['buy__sideways_trend_total_signal_needed'])
                ) | (
                        (dataframe['trend'] == 'upwards') &
                        (dataframe['total_buy_signal_strength'] >= params['buy__upwards_trend_total_signal_needed'])
                ), 'buy'] = 1

            # Override Buy Signal: When configured buy signals can be completely turned off for each kind of trend
            if not params['buy___trades_when_downwards']:
                dataframe.loc[dataframe['trend'] == 'downwards', 'buy'] = 0
            if not params['buy___trades_when_sideways']:
                dataframe.loc[dataframe['trend'] == 'sideways', 'buy'] = 0
            if not params['buy___trades_when_upwards']:
                dataframe.loc[dataframe['trend'] == 'upwards', 'buy'] = 0

            return dataframe

        return populate_buy_trend

    @staticmethod
    def sell_indicator_space() -> List[Dimension]:
        """
        Define your Hyperopt space for searching sell strategy parameters.
        """
        return [
            # Decide on which kinds of trends the bot should trade or hold
            Categorical([True, False], name='sell___trades_when_downwards'),
            Categorical([True, False], name='sell___trades_when_sideways'),
            Categorical([True, False], name='sell___trades_when_upwards'),
            # Downwards Trend
            # ------------
            # Total Buy Signal Percentage needed for a signal to be positive
            Integer(0, 100, name='sell__downwards_trend_total_signal_needed'),
            # Buy Signal Weight Influence Table
            Integer(0, 100, name='sell_downwards_trend_adx_strong_down_weight'),
            Integer(0, 100, name='sell_downwards_trend_rsi_weight'),
            Integer(0, 100, name='sell_downwards_trend_macd_weight'),
            Integer(0, 100, name='sell_downwards_trend_sma_short_death_cross_weight'),
            Integer(0, 100, name='sell_downwards_trend_ema_short_death_cross_weight'),
            Integer(0, 100, name='sell_downwards_trend_sma_long_death_cross_weight'),
            Integer(0, 100, name='sell_downwards_trend_ema_long_death_cross_weight'),
            Integer(0, 100, name='sell_downwards_trend_bollinger_bands_weight'),
            Integer(0, 100, name='sell_downwards_trend_vwap_cross_weight'),
            # Sideways Trend
            # ------------
            # Total Buy Signal Percentage needed for a signal to be positive
            Integer(0, 100, name='sell__sideways_trend_total_signal_needed'),
            # Buy Signal Weight Influence Table
            Integer(0, 100, name='sell_sideways_trend_adx_strong_down_weight'),
            Integer(0, 100, name='sell_sideways_trend_rsi_weight'),
            Integer(0, 100, name='sell_sideways_trend_macd_weight'),
            Integer(0, 100, name='sell_sideways_trend_sma_short_death_cross_weight'),
            Integer(0, 100, name='sell_sideways_trend_ema_short_death_cross_weight'),
            Integer(0, 100, name='sell_sideways_trend_sma_long_death_cross_weight'),
            Integer(0, 100, name='sell_sideways_trend_ema_long_death_cross_weight'),
            Integer(0, 100, name='sell_sideways_trend_bollinger_bands_weight'),
            Integer(0, 100, name='sell_sideways_trend_vwap_cross_weight'),
            # Upwards Trend
            # ------------
            # Total Buy Signal Percentage needed for a signal to be positive
            Integer(0, 100, name='sell__upwards_trend_total_signal_needed'),
            # Buy Signal Weight Influence Table
            Integer(0, 100, name='sell_upwards_trend_adx_strong_down_weight'),
            Integer(0, 100, name='sell_upwards_trend_rsi_weight'),
            Integer(0, 100, name='sell_upwards_trend_macd_weight'),
            Integer(0, 100, name='sell_upwards_trend_sma_short_death_cross_weight'),
            Integer(0, 100, name='sell_upwards_trend_ema_short_death_cross_weight'),
            Integer(0, 100, name='sell_upwards_trend_sma_long_death_cross_weight'),
            Integer(0, 100, name='sell_upwards_trend_ema_long_death_cross_weight'),
            Integer(0, 100, name='sell_upwards_trend_bollinger_bands_weight'),
            Integer(0, 100, name='sell_upwards_trend_vwap_cross_weight')
        ]

    @staticmethod
    def sell_strategy_generator(params: Dict[str, Any]) -> Callable:
        """
        Define the sell strategy parameters to be used by Hyperopt.
        """

        def populate_sell_trend(dataframe: DataFrame, metadata: dict) -> DataFrame:
            # Detect if current trend going Downwards / Sideways / Upwards, strategy will respond accordingly
            dataframe.loc[(dataframe['adx'] > 20) &
                          (dataframe['plus_di'] < dataframe['minus_di']), 'trend'] = 'downwards'
            dataframe.loc[dataframe['adx'] < 20, 'trend'] = 'sideways'
            dataframe.loc[(dataframe['adx'] > 20) & (dataframe['plus_di'] > dataframe['minus_di']), 'trend'] = 'upwards'

            # If a Weighted Sell Signal goes off => Bearish Indication, Set to true (=1) and multiply by weight
            # percentage

            # Weighted Sell Signal: ADX above 25 & +DI below -DI (The trend has strength while moving down)
            dataframe.loc[(dataframe['trend'] == 'downwards') & (dataframe['adx'] > 25),
                          'total_sell_signal_strength'] += params['sell_downwards_trend_adx_strong_down_weight']
            dataframe.loc[(dataframe['trend'] == 'sideways') & (dataframe['adx'] > 25),
                          'total_sell_signal_strength'] += params['sell_sideways_trend_adx_strong_down_weight']
            dataframe.loc[(dataframe['trend'] == 'upwards') & (dataframe['adx'] > 25),
                          'total_sell_signal_strength'] += params['sell_upwards_trend_adx_strong_down_weight']

            # Weighted Sell Signal: RSI crosses below 70 (Over-bought / high-price and dropping indication)
            dataframe.loc[(dataframe['trend'] == 'downwards') & qtpylib.crossed_below(dataframe['rsi'], 70),
                          'total_sell_signal_strength'] += params['sell_downwards_trend_rsi_weight']
            dataframe.loc[(dataframe['trend'] == 'sideways') & qtpylib.crossed_below(dataframe['rsi'], 70),
                          'total_sell_signal_strength'] += params['sell_sideways_trend_rsi_weight']
            dataframe.loc[(dataframe['trend'] == 'upwards') & qtpylib.crossed_below(dataframe['rsi'], 70),
                          'total_sell_signal_strength'] += params['sell_upwards_trend_rsi_weight']

            # Weighted Sell Signal: MACD below Signal
            dataframe.loc[(dataframe['trend'] == 'downwards') & (dataframe['macd'] < dataframe['macdsignal']),
                          'total_sell_signal_strength'] += params['sell_downwards_trend_macd_weight']
            dataframe.loc[(dataframe['trend'] == 'sideways') & (dataframe['macd'] < dataframe['macdsignal']),
                          'total_sell_signal_strength'] += params['sell_sideways_trend_macd_weight']
            dataframe.loc[(dataframe['trend'] == 'upwards') & (dataframe['macd'] < dataframe['macdsignal']),
                          'total_sell_signal_strength'] += params['sell_upwards_trend_macd_weight']

            # Weighted Sell Signal: SMA short term Death Cross (Short term SMA crosses below Medium term SMA)
            dataframe.loc[(dataframe['trend'] == 'downwards') & qtpylib.crossed_below(dataframe['sma9'], dataframe[
                'sma50']), 'total_sell_signal_strength'] += params['sell_downwards_trend_sma_short_death_cross_weight']
            dataframe.loc[(dataframe['trend'] == 'sideways') & qtpylib.crossed_below(dataframe['sma9'], dataframe[
                'sma50']), 'total_sell_signal_strength'] += params['sell_sideways_trend_sma_short_death_cross_weight']
            dataframe.loc[(dataframe['trend'] == 'upwards') & qtpylib.crossed_below(dataframe['sma9'], dataframe[
                'sma50']), 'total_sell_signal_strength'] += params['sell_upwards_trend_sma_short_death_cross_weight']

            # Weighted Sell Signal: EMA short term Death Cross (Short term EMA crosses below Medium term EMA)
            dataframe.loc[(dataframe['trend'] == 'downwards') & qtpylib.crossed_below(dataframe['ema9'], dataframe[
                'ema50']), 'total_sell_signal_strength'] += params['sell_downwards_trend_ema_short_death_cross_weight']
            dataframe.loc[(dataframe['trend'] == 'sideways') & qtpylib.crossed_below(dataframe['ema9'], dataframe[
                'ema50']), 'total_sell_signal_strength'] += params['sell_sideways_trend_ema_short_death_cross_weight']
            dataframe.loc[(dataframe['trend'] == 'upwards') & qtpylib.crossed_below(dataframe['ema9'], dataframe[
                'ema50']), 'total_sell_signal_strength'] += params['sell_upwards_trend_ema_short_death_cross_weight']

            # Weighted Sell Signal: SMA long term Death Cross (Medium term SMA crosses below Long term SMA)
            dataframe.loc[(dataframe['trend'] == 'downwards') & qtpylib.crossed_below(dataframe['sma50'], dataframe[
                'sma200']), 'total_sell_signal_strength'] += params['sell_downwards_trend_sma_long_death_cross_weight']
            dataframe.loc[(dataframe['trend'] == 'sideways') & qtpylib.crossed_below(dataframe['sma50'], dataframe[
                'sma200']), 'total_sell_signal_strength'] += params['sell_sideways_trend_sma_long_death_cross_weight']
            dataframe.loc[(dataframe['trend'] == 'upwards') & qtpylib.crossed_below(dataframe['sma50'], dataframe[
                'sma200']), 'total_sell_signal_strength'] += params['sell_upwards_trend_sma_long_death_cross_weight']

            # Weighted Sell Signal: EMA long term Death Cross (Medium term EMA crosses below Long term EMA)
            dataframe.loc[(dataframe['trend'] == 'downwards') & qtpylib.crossed_below(dataframe['ema50'], dataframe[
                'ema200']), 'total_sell_signal_strength'] += params['sell_downwards_trend_ema_long_death_cross_weight']
            dataframe.loc[(dataframe['trend'] == 'sideways') & qtpylib.crossed_below(dataframe['ema50'], dataframe[
                'ema200']), 'total_sell_signal_strength'] += params['sell_sideways_trend_ema_long_death_cross_weight']
            dataframe.loc[(dataframe['trend'] == 'upwards') & qtpylib.crossed_below(dataframe['ema50'], dataframe[
                'ema200']), 'total_sell_signal_strength'] += params['sell_upwards_trend_ema_long_death_cross_weight']

            # Weighted Sell Signal: Re-Entering Upper Bollinger Band after upward breakout
            # (Candle closes below Upper Bollinger Band)
            dataframe.loc[(dataframe['trend'] == 'downwards') & qtpylib.crossed_below(dataframe['close'], dataframe[
                'bb_upperband']), 'total_sell_signal_strength'] += params['sell_downwards_trend_bollinger_bands_weight']
            dataframe.loc[(dataframe['trend'] == 'sideways') & qtpylib.crossed_below(dataframe['close'], dataframe[
                'bb_upperband']), 'total_sell_signal_strength'] += params['sell_sideways_trend_bollinger_bands_weight']
            dataframe.loc[(dataframe['trend'] == 'upwards') & qtpylib.crossed_below(dataframe['close'], dataframe[
                'bb_upperband']), 'total_sell_signal_strength'] += params['sell_upwards_trend_bollinger_bands_weight']

            # Weighted Sell Signal: VWAP crosses below current price
            dataframe.loc[(dataframe['trend'] == 'downwards') & qtpylib.crossed_below(dataframe['vwap'], dataframe[
                'close']), 'total_sell_signal_strength'] += params['sell_downwards_trend_vwap_cross_weight']
            dataframe.loc[(dataframe['trend'] == 'sideways') & qtpylib.crossed_below(dataframe['vwap'], dataframe[
                'close']), 'total_sell_signal_strength'] += params['sell_sideways_trend_vwap_cross_weight']
            dataframe.loc[(dataframe['trend'] == 'upwards') & qtpylib.crossed_below(dataframe['vwap'], dataframe[
                'close']), 'total_sell_signal_strength'] += params['sell_upwards_trend_vwap_cross_weight']

            # Check if sell signal should be sent depending on the current trend
            dataframe.loc[
                (
                        (dataframe['trend'] == 'downwards') &
                        (dataframe['total_sell_signal_strength'] >= params['sell__downwards_trend_total_signal_needed'])
                ) | (
                        (dataframe['trend'] == 'sideways') &
                        (dataframe['total_sell_signal_strength'] >= params['sell__sideways_trend_total_signal_needed'])
                ) | (
                        (dataframe['trend'] == 'upwards') &
                        (dataframe['total_sell_signal_strength'] >= params['sell__upwards_trend_total_signal_needed'])
                ), 'sell'] = 1

            # Override Sell Signal: When configured sell signals can be completely turned off for each kind of trend
            if not params['sell___trades_when_downwards']:
                dataframe.loc[dataframe['trend'] == 'downwards', 'sell'] = 0
            if not params['sell___trades_when_sideways']:
                dataframe.loc[dataframe['trend'] == 'sideways', 'sell'] = 0
            if not params['sell___trades_when_upwards']:
                dataframe.loc[dataframe['trend'] == 'upwards', 'sell'] = 0

            return dataframe

        return populate_sell_trend
