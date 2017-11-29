#!/usr/bin/env python3

import timeit


# import csv
# from collections import defaultdict
#
# with open('data/csv/pokemon.csv', 'r') as f:
#     dict_ = defaultdict(str)
#
#     reader = csv.DictReader(f)
#
#     for row in reader:
#         dict_[int(row["id"])] = row
#
# a = dict_[1]['species_id']
# print(a)

import pandas as pd

with open('data/csv/pokemon.csv', 'r') as f:

    df = pd.read_csv(f)


b = df.loc[1, 'species_id']
print(b)
