# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 04:22:57 2017

@author: Kip
"""

from collections import deque
import pandas as pd
import numpy as np


with open('./data/csv/move_meta_ailments.csv') as csv_file:
    ailments = pd.read_csv(csv_file)

clock = 1


class Status():
    """A class containing all current statuses of a Pokémon.
    Status conditions, also referred to as status problems or status
    ailments, affect a Pokémon's ability to battle. There are three
    kinds of status. The first are non-volatile, the second are
    volatile, and the third lasts while a Pokémon is in battle. For our
    purposes, there is no point to make distinctions to the last two,
    so we combine them and call them 'volatile'.

    The csv files call it an 'ailment'.

    A `non-volatile` status is one of the following: paralysis, sleep,
    freeze, burn, and poison, with some sub-categories under each if
    they exist. Non-volatile statuses cannot stack; one Pokémon can
    only have one non-volatile status each time.

    A `volatile` status is the one that does not exist out side of a
    battle.Some classic examples would be confusion, ingrain,
    infatuation, etc. Onecan have multiple volatile statuses.

    Usage:
        >>>

    See also:
    https://bulbapedia.bulbagarden.net/wiki/Status_condition
    """

    def __init__(self, status_id, lasting_time=None):

        __name = ailments[ailments["id"] == status_id]["identifier"].values[0]
        __volatile = status_id in range(0, 6)
        __start = clock

        if lasting_time:
            __stop = __start + lasting_time
        else:
            __stop = float('inf')

        self.id = np.array([status_id], dtype=int)
        self.name = np.array([__name])
        self.volatile = np.array([__volatile], dtype=bool)
        self.start = np.array([__start], dtype=int)
        self.stop = np.array([__stop], dtype=int)

    @staticmethod
    def current_round():
        return clock

    @property
    def remaining_round(self):
        return self.stop - self.current_round()

    def __add__(self, other):
        pass


burn = Status(4)
