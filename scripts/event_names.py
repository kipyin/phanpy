"""An unmaintained one-shot script for setting event names.
"""

stats = ['attack', 'defence', 'specialAttack', 'specialDefence',
         'speed', 'accuracy', 'evasion', 'critical']

res = []
for stat in stats:
    res.append("'{0}_to_opponent', '{0}_to_self',".format(stat))

print('\n'.join(res))
