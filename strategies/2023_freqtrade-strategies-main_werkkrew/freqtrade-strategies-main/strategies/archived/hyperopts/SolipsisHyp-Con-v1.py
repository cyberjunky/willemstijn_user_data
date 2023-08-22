from functools import reduce
from typing import Any, Callable, Dict, List

import numpy as np
import pandas as pd
from pandas import DataFrame
from skopt.space import Categorical, Dimension, Integer, Real

from freqtrade.optimize.hyperopt_interface import IHyperOpt

import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib

class SolipsisConHyp(IHyperOpt):

    @staticmethod
    def indicator_space() -> List[Dimension]:
        return [
            Integer(0, 100, name='consensus-buy'),
            # Informative Timeframe
            Categorical(['lower', 'upper', 'both', 'none'], name='inf-guard'),
            Real(0.70, 0.99, name='inf-pct-adr-top'),
            Real(0.01, 0.20, name='inf-pct-adr-bot'),
            # Extra BTC/ETH Stakes
            Integer(10, 70, name='xtra-inf-stake-rmi'),
            Integer(10, 70, name='xtra-base-stake-rmi'),
            Integer(10, 70, name='xtra-base-fiat-rmi'),
            # Extra BTC/STAKE if not in whitelist
            Integer(0, 100, name='xbtc-consensus-buy')
        ]

    @staticmethod
    def sell_indicator_space() -> List[Dimension]:
        return [
            Integer(0, 100, name='consensus-sell')
        ]

    @staticmethod
    def buy_strategy_generator(params: Dict[str, Any]) -> Callable:

        def populate_buy_trend(dataframe: DataFrame, metadata: dict) -> DataFrame:
            conditions = []

            inf_timeframe = '1h'
            stake_currency = 'USD'
            custom_fiat = 'USD'
            btc_in_whitelist = False

            if params['inf-guard'] == 'upper' or params['inf-guard'] == 'both':
                conditions.append(
                    (dataframe['close'] <= dataframe[f"3d_low_{inf_timeframe}"] + 
                    (params['inf-pct-adr-top'] * dataframe[f"adr_{inf_timeframe}"]))
                )

            if params['inf-guard'] == 'lower' or params['inf-guard'] == 'both':
                conditions.append(
                    (dataframe['close'] >= dataframe[f"3d_low_{inf_timeframe}"] + 
                    (params['inf-pct-adr-bot'] * dataframe[f"adr_{inf_timeframe}"]))
                )

            conditions.append(dataframe['consensus_buy'] > params['consensus-buy'])  

            if stake_currency in ('BTC', 'ETH'):
                conditions.append(
                    (dataframe[f"{stake_currency}_rmi"] < params['xtra-base-stake-rmi']) | 
                    (dataframe[f"{custom_fiat}_rmi"] > params['xtra-base-fiat-rmi'])
                )
                conditions.append(dataframe[f"{stake_currency}_rmi_{inf_timeframe}"] < params['xtra-inf-stake-rmi'])
            else:
                if btc_in_whitelist == False:
                    conditions.append(dataframe['BTC_consensus_buy'] > params['xbtc-consensus-buy'])

            conditions.append(dataframe['volume'].gt(0))

            if conditions:
                dataframe.loc[
                    reduce(lambda x, y: x & y, conditions),
                    'buy'] = 1
                return dataframe

        return populate_buy_trend

    @staticmethod
    def sell_strategy_generator(params: Dict[str, Any]) -> Callable:

        def populate_sell_trend(dataframe: DataFrame, metadata: dict) -> DataFrame:
            conditions = []

            conditions.append(dataframe['consensus_sell'] > params['consensus-sell'])

            if conditions:
                dataframe.loc[
                    reduce(lambda x, y: x & y, conditions),
                    'sell'] = 1

            # dataframe['sell'] = 0
            return dataframe

        return populate_sell_trend

    # If not optimizing the sell space assume it is disabled entirely.
    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe['sell'] = 0
        return dataframe