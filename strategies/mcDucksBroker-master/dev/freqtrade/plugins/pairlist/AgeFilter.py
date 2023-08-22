"""
Minimum age (days listed) pair list filter
"""
import logging
from copy import deepcopy
from typing import Any, Dict, List, Optional

import arrow
from pandas import DataFrame

from freqtrade.exceptions import OperationalException
from freqtrade.misc import plural
from freqtrade.plugins.pairlist.IPairList import IPairList


logger = logging.getLogger(__name__)


class AgeFilter(IPairList):

    # Checked symbols cache (dictionary of ticker symbol => timestamp)
    _symbolsChecked: Dict[str, int] = {}

    def __init__(self, exchange, pairlistmanager,
                 config: Dict[str, Any], pairlistconfig: Dict[str, Any],
                 pairlist_pos: int) -> None:
        super().__init__(exchange, pairlistmanager, config, pairlistconfig, pairlist_pos)

        self._min_days_listed = pairlistconfig.get('min_days_listed', 10)

        if self._min_days_listed < 1:
            raise OperationalException("AgeFilter requires min_days_listed to be >= 1")
        if self._min_days_listed > exchange.ohlcv_candle_limit('1d'):
            raise OperationalException("AgeFilter requires min_days_listed to not exceed "
                                       "exchange max request size "
                                       f"({exchange.ohlcv_candle_limit('1d')})")

    @property
    def needstickers(self) -> bool:
        """
        Boolean property defining if tickers are necessary.
        If no Pairlist requires tickers, an empty Dict is passed
        as tickers argument to filter_pairlist
        """
        return False

    def short_desc(self) -> str:
        """
        Short whitelist method description - used for startup-messages
        """
        return (f"{self.name} - Filtering pairs with age less than "
                f"{self._min_days_listed} {plural(self._min_days_listed, 'day')}.")

    def filter_pairlist(self, pairlist: List[str], tickers: Dict) -> List[str]:
        """
        :param pairlist: pairlist to filter or sort
        :param tickers: Tickers (from exchange.get_tickers()). May be cached.
        :return: new allowlist
        """
        needed_pairs = [(p, '1d') for p in pairlist if p not in self._symbolsChecked]
        if not needed_pairs:
            return pairlist

        since_ms = int(arrow.utcnow()
                       .floor('day')
                       .shift(days=-self._min_days_listed - 1)
                       .float_timestamp) * 1000
        candles = self._exchange.refresh_latest_ohlcv(needed_pairs, since_ms=since_ms, cache=False)
        if self._enabled:
            for p in deepcopy(pairlist):
                daily_candles = candles[(p, '1d')] if (p, '1d') in candles else None
                if not self._validate_pair_loc(p, daily_candles):
                    pairlist.remove(p)
        self.log_once(f"Validated {len(pairlist)} pairs.", logger.info)
        return pairlist

    def _validate_pair_loc(self, pair: str, daily_candles: Optional[DataFrame]) -> bool:
        """
        Validate age for the ticker
        :param pair: Pair that's currently validated
        :param ticker: ticker dict as returned from ccxt.fetch_tickers()
        :return: True if the pair can stay, false if it should be removed
        """
        # Check symbol in cache
        if pair in self._symbolsChecked:
            return True

        if daily_candles is not None:
            if len(daily_candles) >= self._min_days_listed:
                # We have fetched at least the minimum required number of daily candles
                # Add to cache, store the time we last checked this symbol
                self._symbolsChecked[pair] = int(arrow.utcnow().float_timestamp) * 1000
                return True
            else:
                self.log_once(f"Removed {pair} from whitelist, because age "
                              f"{len(daily_candles)} is less than {self._min_days_listed} "
                              f"{plural(self._min_days_listed, 'day')}", logger.info)
                return False
        return False
