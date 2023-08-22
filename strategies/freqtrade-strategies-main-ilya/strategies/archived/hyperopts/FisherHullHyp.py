# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement

# --- Do not remove these libs ---
from functools import reduce
from typing import Any, Callable, Dict, List

import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
from skopt.space import Categorical, Dimension, Integer, Real  # noqa

from freqtrade.optimize.hyperopt_interface import IHyperOpt

# --------------------------------
# Add your lib to import here
import talib.abstract as ta  # noqa
import freqtrade.vendor.qtpylib.indicators as qtpylib
from technical.indicators import hull_moving_average

class FisherHullHyp(IHyperOpt):

    @staticmethod
    def indicator_space() -> List[Dimension]:
        return [
            Real(-100.0, 100.0, name='cci-buy'),
            Real(-1.0, 1.0, name='fisher-buy')
        ]

    @staticmethod
    def sell_indicator_space() -> List[Dimension]:
        return [
            Real(-100.0, 100.0, name='cci-sell'),
            Real(-1.0, 1.0, name='fisher-sell')
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
            dataframe.loc[
                (
                (dataframe['hma'] < dataframe['hma'].shift()) &
                (dataframe['cci'] <= params['cci-buy']) &
                (dataframe['fisher_rsi'] < params['fisher-buy'])
                )
                ,
                'buy'
            ] = 1

            return dataframe

        return populate_buy_trend

    @staticmethod
    def sell_strategy_generator(params: Dict[str, Any]) -> Callable:
        """
        Define the sell strategy parameters to be used by hyperopt
        """
        def populate_sell_trend(dataframe: DataFrame, metadata: dict) -> DataFrame:
            
            dataframe.loc[
                (
                (dataframe['hma'] > dataframe['hma'].shift()) &
                (dataframe['cci'] >= params['cci-sell']) &
                (dataframe['fisher_rsi'] > params['fisher-sell']) &
                (dataframe['volume'] > 0)
                )
                ,
                'sell'
            ] = 1

            return dataframe

        return populate_sell_trend


    @staticmethod
    def generate_roi_table(params: Dict) -> Dict[int, float]:

        roi_table = {}
        roi_table[0] = params['roi_p1'] + params['roi_p2'] + params['roi_p3'] + params['roi_p4'] + params['roi_p5'] + params['roi_p6']
        roi_table[params['roi_t6']] = params['roi_p1'] + params['roi_p2'] + params['roi_p3'] + params['roi_p4'] + params['roi_p5']
        roi_table[params['roi_t6'] + params['roi_t5']] = params['roi_p1'] + params['roi_p2'] + params['roi_p3'] + params['roi_p4']
        roi_table[params['roi_t6'] + params['roi_t5'] + params['roi_t4']] = params['roi_p1'] + params['roi_p2'] + params['roi_p3']
        roi_table[params['roi_t6'] + params['roi_t5'] + params['roi_t4'] + params['roi_t3']] = params['roi_p1'] + params['roi_p2']
        roi_table[params['roi_t6'] + params['roi_t5'] + params['roi_t4'] + params['roi_t3'] + params['roi_t2']] = params['roi_p1']
        roi_table[params['roi_t6'] + params['roi_t5'] + params['roi_t4'] + params['roi_t3'] + params['roi_t2'] + params['roi_t1']] = 0

        return roi_table

    @staticmethod
    def roi_space() -> List[Dimension]:

        return [
            Integer(1, 15, name='roi_t6'),
            Integer(1, 45, name='roi_t5'),
            Integer(1, 90, name='roi_t4'),
            Integer(45, 120, name='roi_t3'),
            Integer(45, 180, name='roi_t2'),
            Integer(90, 200, name='roi_t1'),

            Real(0.005, 0.10, name='roi_p6'),
            Real(0.005, 0.07, name='roi_p5'),
            Real(0.005, 0.05, name='roi_p4'),
            Real(0.005, 0.025, name='roi_p3'),
            Real(0.005, 0.01, name='roi_p2'),
            Real(0.003, 0.007, name='roi_p1'),
        ]