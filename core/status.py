# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 04:22:57 2017
@author: Kip
"""

import numpy as np

from mechanisms.tables import ailments

clock = 1


# TODO: finish the __doc__ string.
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

    Attributes:
        id : numpy.array of int
            The `ailment_id` in `move_meta_ailments.csv`.
        name : numpy.array of str
            The name of the status(es).
        volatile : numpy.array of bool
            True for volatile statuses, and False for non-volatile
            statuses (id in 1~5).
        start, stop : np array of float
            These are the timestamps of when the statuses have been
            inflicted.

    Built-in Methods:
        __add__ :
        __len__ :
        __iter__ :


    See also:
    https://bulbapedia.bulbagarden.net/wiki/Status_condition
    """

    def __init__(self, status_id, lasting_time=None):

        __name = ailments[ailments["id"] == status_id]["identifier"].values[0]
        __volatile = status_id not in range(0, 6)
        __start = clock

        if lasting_time:
            __stop = __start + lasting_time
        else:
            __stop = float('inf')

        self.id = np.array([status_id], dtype=int)
        self.name = np.array([__name], dtype=str)
        self.volatile = np.array([__volatile], dtype=bool)
        self.start = np.array([__start], dtype=float)
        self.stop = np.array([__stop], dtype=float)

        self.__current = 0

    @staticmethod
    def current_round():
        return clock

    @property
    def remaining_round(self):
        return self.stop - self.current_round()

    def truncate(self, cond):
        self.start = self.start[cond]
        self.stop = self.stop[cond]
        self.id = self.id[cond]
        self.name = self.name[cond]
        self.volatile = self.volatile[cond]

    def update(self):
        if 0 in self.remaining_round:
            __stay = np.where(self.remaining_round != 0)
            self.truncate(__stay)

    def __str__(self):
        return ', '.join(self.name)

    def __repr__(self):
        return ', '.join(self.name)

    def __len__(self):
        return len(self.name)

    def __iter__(self):
        return self

    def __next__(self):

        if self.__current >= len(self.id):
            raise StopIteration

        else:
            self.__current += 1
            return list(self.id)[self.__current - 1]

    def __add__(self, other):
        """Adds two statuses together.
        Append volatile statuses; update non-volatile statuses.
        """

        # Get the position of the non-volatile status in each `Status`.
        # There should be *at most 1* `False` in each list.
        if False in self.volatile and False in other.volatile:

            __nvol_pos_self = np.where(self.volatile == False)[0][0]
            __nvol_pos_other = np.where(other.volatile == False)[0][0]
            __vol_pos_other = np.where(other.volatile)

            # For the non-vol status, if the starting round of `other`
            # is greater than that of `self`, then replace `self` with
            # `other`. Otherwise, nothing changes.
            if self.start[__nvol_pos_self] < other.start[__nvol_pos_other]:

                self.start[__nvol_pos_self] = other.start[__nvol_pos_other]
                self.id[__nvol_pos_self] = other.id[__nvol_pos_other]
                self.name[__nvol_pos_self] = other.name[__nvol_pos_other]
                self.stop[__nvol_pos_self] = other.stop[__nvol_pos_other]

                other.truncate(__vol_pos_other)

        self.id = np.append(self.id, other.id)
        self.name = np.append(self.name, other.name)
        self.start = np.append(self.start, other.start)
        self.stop = np.append(self.stop, other.stop)
        self.volatile = np.append(self.volatile, other.volatile)

        self.update()

        return self


def test():

    global clock

    poison = Status(5)
    leech_seed = Status(18, 5)
    combined = leech_seed + poison
    clock += 1
    burn = Status(4)
    combined += burn
    clock += 1
    nightmare = Status(9, 5)
    new_combined = poison + nightmare + combined

    print(new_combined.name, new_combined.start, new_combined.id,
          new_combined.remaining_round, new_combined.volatile)
