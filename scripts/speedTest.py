"""An unmaintained one-shot script testing for pandas.DataFrame efficiency.

Comparing the runtime of filling a fixed-size dataframe vs. adding rows
on the fly.
"""

import timeit

setup = '''
import pandas, numpy
df1 = pandas.DataFrame(numpy.zeros(shape=[100, 30]))
df2 = pandas.DataFrame(columns=numpy.arange(30))
row = [1 for x in range(30)]
'''

f = ['df1.loc[0] = row', 'df2.loc[0] = row']

for func in f:
    print(func)
    print(min(timeit.Timer(func, setup).repeat(3, 100000)))

"""
Result:

    df1.loc[0] = row
    20.68039407208562
    df2.loc[0] = row
    24.604908964945935

Yeah. Faster to predeine rows.
"""
