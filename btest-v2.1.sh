#!/bin/bash
# V2.1  Changed config file names and futures backtest data directory

# This file should be in the /opt/freqtrade directory!
LOGDIR=user_data/backtest_results
TIMESTAMP=`date "+%Y%m%d-%H%M%S"`
scriptstart=$SECONDS
SPOTCONFIGFILE=./user_data/spot_config.json
SPOTDATA=binance
FUTURESCONFIGFILE=./user_data/futures_config.json
FUTURESDATA=binance
TIMERANGE='-20230101'
EXTENSION='txt'

echo
echo This script will run multiple backtests at the same time on a certain strategy.
echo See \"freqtrade list-strategies\" for available strategies.
echo Tested timeframes are: 1d, 4h, 1h, 30m, 15m, 5m
echo
read -p 'Input strategy name: ' STRATEGY
read -p 'For Classic spot backtest, type "c";
for Futures backtest (timeperiod 2019-2023), type "f";
for Spot trading over Futures timeperiod, type "x".
Please make a selection (c/f/x): ' CHOICE


if [ $CHOICE = 'c' ]; then
    CONFIG=$SPOTCONFIGFILE
    DATADIR=$SPOTDATA
    TPE='spot-classic'
    echo Config $CONFIG will be used for $TPE trading.
elif [ $CHOICE = 'f' ]; then
    CONFIG=$FUTURESCONFIGFILE
    DATADIR=$FUTURESDATA
    TPE='futures-2017_2023'
    echo Config $CONFIG will be used for $TPE trading.
elif [ $CHOICE = 'x' ]; then
   CONFIG=$SPOTCONFIGFILE
   DATADIR=$FUTURESDATA
   TPE='spot-2017_2023'
   echo Config $CONFIG will be used for $TPE trading.
else
   echo "You entered an unknown parameter."
   echo "Exiting!"
   set -u
fi

echo
echo Strategy $STRATEGY will be tested on $TIMESTAMP and logs will be placed in $LOGDIR/$STRATEGY-$TPE-$TIMESTAMP.$EXTENSION
echo
echo Start backtest 2>&1 | tee $LOGDIR/$STRATEGY-$TPE-$TIMESTAMP


for TIMEFRAME in 1d 4h 1h 30m 15m 5m
do
    echo
    echo ========== $TIMEFRAME TIMEFRAME BACKTEST ========== 2>&1 | tee -a $LOGDIR/$STRATEGY-$TPE-$TIMESTAMP.$EXTENSION
    start=$SECONDS
    freqtrade backtesting --config $CONFIG --export trades --export-filename 'user_data/backtest_results/'$STRATEGY'-'$TPE'-'$TIMEFRAME --timeframe $TIMEFRAME --timerange=$TIMERANGE --strategy $STRATEGY --datadir user_data/data/$DATADIR 2>&1 | tee -a $LOGDIR/$STRATEGY-$TPE-$TIMESTAMP.$EXTENSION
    end=$SECONDS
    echo "duration: $((end-start)) seconds." | tee -a $LOGDIR/$STRATEGY-$TPE-$TIMESTAMP.$EXTENSION
    echo =========================================== 2>&1 | tee -a $LOGDIR/$STRATEGY-$TPE-$TIMESTAMP.$EXTENSION
done


echo
scriptend=$SECONDS
echo "Total backtest duration: $(((scriptend-scriptstart)/60)) minutes." | tee -a $LOGDIR/$STRATEGY-$TPE-$TIMESTAMP.$EXTENSION
echo
echo End backtest of $STRATEGY strategy on $TIMESTAMP 2>&1 | tee -a $LOGDIR/$STRATEGY-$TPE-$TIMESTAMP.$EXTENSION
echo Logs can be found in \"user_data/backtest_results\" and $LOGDIR/$STRATEGY-$TPE-$TIMESTAMP 2>&1 | tee -a $LOGDIR/$STRATEGY-$TPE-$TIMESTAMP.$EXTENSION
echo
echo To plot a profit chart of a backtest, use:
echo freqtrade plot-profit --config user_data/backtest-config.json --auto-open --timeframe [1d \| 4h \| 1h \| 30m \| 15m \| 5m]
echo
echo To plot a chart of a certain pair on a certain timeframe, use:
echo freqtrade plot-dataframe --config user_data/backtest-config.json --strategy $STRATEGY-$TPE-$TIMESTAMP --timeframe [1d \| 4h \| 1h \| 30m \| 15m \| 5m] --pair [best pair] [worst pair]
echo
