#!/usr/bin/env python3

import re
btlines = []
linenum = 0
file = input("Enter path and backtest filename to get essential information from :\n> ")
#file='user_data/logs/kumo_breakout-spot-20220929-214019-classic'
losses = re.compile('\-+\d{1,3}.\d{1,3}\s\|') # See: https://regex101.com/
patterns = ['0.000 \|', 'TIMEFRAME BACKTEST', 'ENTER TAG STATS', ' TAG \|', 'TOTAL \|', 'Starting balance', 'Final balance', 'Total profit %', 'Avg. stake amount', '\(Account\)']

with open (file, 'rt') as backtest:
    for line in backtest:
        linenum += 1
        if losses.search(line) != None: 
            btlines.append((linenum, line.rstrip('\n'))) # Append the line to a list
        for pattern in patterns:
            pattern = re.compile(pattern, re.IGNORECASE)
            if pattern.search(line) != None: # If a match is found (result is not None)
                btlines.append((linenum, line.rstrip('\n'))) # Append the line to a list

for btline in btlines:  # Iterate over the list and print them
#    print("Line " + str(btline[0]) + ": " + btline[1])
    print(btline[1])
    

