"""This is an unmaintained one-shot script for trying out the MultiIndex
feature in pandas.
"""
from collections import defaultdict
import pandas as pd
import numpy as np



statnames = ['attack', 'defense', 'specialAttack', 'specialDefense',
             'speed', 'critical', 'accuracy', 'evasion']


multiIndexDict = defaultdict()

values = {k: 0. for k in np.arange(1, 51)}

for part in ['self', 'opponent']:

    for name in statnames:
        multiIndexDict[(part, 'stat_change', name)] = values
        multiIndexDict[(part, 'ailment')] = values

events = pd.DataFrame(multiIndexDict)

__zeros = np.zeros((50, 1))

for top in ['order', 'move', 'item']:
    events[top] = __zeros

events.index.names = ['turn']

events.info()
