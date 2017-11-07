"""This is an unmaintained one-shot script for trying out the MultiIndex
feature in pandas.
"""
from collections import defaultdict
import pandas as pd
import numpy as np

"""
info = list(zip(*[['info'] * 3, ['order', 'move', 'item']]))

damage = list(zip(*[['damage'] * 2, ['self', 'op']]))

status = list(zip(*[['status'] * 2, ['self','op']]))

stats = list(zip(*[['stats'] * 8, ['attack', 'defense',
                                   'specialAttack', 'specialDefense',
                                   'speed', 'critical',
                                   'accuracy', 'evasion']]))

(info, damage, status, stats) = (pd.MultiIndex.from_tuples(x) for x in
                                 [info, damage, status, stats])
"""

#events = pd.DataFrame(index=np.arange(1,51),
#                      columns=['order', 'move', 'item', 'self', 'opponent'],
#                      data=np.zeros((50,5)))

statnames = ['attack', 'defense', 'specialAttack', 'specialDefense',
             'speed', 'critical', 'accuracy', 'evasion']


multiIndexDict = defaultdict()

values = {k: 0. for k in np.arange(1, 51)}

for part in ['self', 'opponent']:

    for name in statnames:
        multiIndexDict[(part, 'stat_change', name)] = values

events = pd.DataFrame(multiIndexDict)

__zeros = np.zeros((50, 1))

for top in ['order', 'move', 'item']:
    events[top] = __zeros

for part in ['self', 'opponent']:
    events.loc[:, (part, 'ailment')] = __zeros

events.index.names = ['turn']

events.info()
