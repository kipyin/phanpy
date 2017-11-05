# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 04:22:57 2017
@author: Kip
"""

import numpy as np

from mechanisms.tables import ailments


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

    Usage
    -----
        >>> clock = 1
        >>> poison = Status(5)
        >>> leech_seed = Status(18,5)
        >>> combined = poison + leech_seed
        >>> combined.remaining_round
        array([ inf,   5.])
        >>> clock += 1
        >>> another_combined = Status('burn') + combined
        ...                    + Status('nightmare')
        >>> another_combined.name
        array(['burn', 'leech-seed', 'nightmare'],
        dtype='<U10')

    Attributes
    ----------
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

    Built-in Methods
    ----------------
        __add__ :
        __len__ :
        __iter__ :


    See also
    --------
        https://bulbapedia.bulbagarden.net/wiki/Status_condition
    """

    def __init__(self, status, lasting_time=None):

        global clock

        try:
            # Check if `clock` is defined.
            clock = clock

        except NameError:
            clock = 1

        if status in list(ailments.id.values):
            # If the input is a valid id, get the status name from the
            # table.
            __cond = ailments["id"] == status
            __name = ailments[__cond]["identifier"].values[0]
            __status_id = status

        elif status in ailments.identifier.values:
            # Else if the input is a valid status name, get the id
            # from the table.
            __cond = (ailments["identifier"] == status)
            __name = status
            __status_id = ailments[__cond]["id"].values[0]

        else:
            # If the input is neither, then that means it is a custom-
            # defined Status. The status' name is the input, and the
            # id is set to be a random 6-digit number in order to
            # distinguish it from all the other status id's.
            __name = status
            __status_id = np.random.randint(100000, 199999)

        # The status is of volatile type if its id is not in range(0,6).
        # Otherwise, it is a non-volatile type.
        __volatile = __status_id not in range(0, 6)

        # Set the starting time to the current round number.
        __start = clock

        if lasting_time:
            # If lasting_time is defined, calculate the stopping time.
            __stop = __start + lasting_time

        else:
            # Otherwise, the status never ends.
            __stop = float('inf')

        self.id = np.array([__status_id], dtype=int)
        # The dtype '<U20' means that it is a little-endian unicode
        # with a length of 20. In other words, it supports a maximum
        # of 20-character name.
        #
        # For example, if I define a Status as follows:
        #
        # >>> my_status = Status('123456789012345678901234567890')
        #
        # i.e. it is defined to have a 30-char name, but dtype='<U20'
        # limits it to 20 chars. Therefore, if then we do
        #
        # >>> my_status.name
        #
        # We will only get array(['freeze', '12345678901234567890'],
        # dtype='<U20').
        # 20-char should be enought, as the longest statuses in game are
        # 'infatuation', 'perish-song', 'telekinesis' (all 11-chars).
        self.name = np.array([__name], dtype='<U20')
        self.volatile = np.array([__volatile], dtype=bool)
        self.start = np.array([__start], dtype=float)
        self.stop = np.array([__stop], dtype=float)

        # A counter for __next__
        self.__current = 0

    @staticmethod
    def current_round():
        """Returns the current round num"""
        return clock

    @property
    def remaining_round(self):
        """Returns the remaining round num of the effect.

        Note that this is an n-dim array.
        """
        return self.stop - self.current_round()

    def __truncate(self, cond):
        """Used in removing unwanted statuses."""

        self.start = self.start[cond]
        self.stop = self.stop[cond]
        self.id = self.id[cond]
        self.name = self.name[cond]
        self.volatile = self.volatile[cond]

    def update(self):
        """Remove any status with 0 lifetime left."""
        if 0 in self.remaining_round:

            __stay = np.where(self.remaining_round != 0)
            self.__truncate(__stay)

    def __str__(self):
        return ', '.join(self.name)

    def __repr__(self):
        return ', '.join(self.name)

    def __len__(self):
        return len(self.name)

    def __iter__(self):
        # Make Status iterable. I don't know where it can be used, but
        # why not.
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
        self.update()

        # Get the position of the non-volatile status in each `Status`.
        # There should be *at most 1* `False` in each list.
        if False in self.volatile and False in other.volatile:

            __nvol_pos_self = np.where(~self.volatile)[0][0]
            __nvol_pos_other = np.where(~other.volatile)[0][0]
            __vol_pos_other = np.where(other.volatile)
            __vol_pos_self = np.where(self.volatile)

            # For the non-vol status, if the starting round of `other`
            # is greater than that of `self`, then replace `self` with
            # `other`. Otherwise, nothing changes.
            if self.start[__nvol_pos_self] <= other.start[__nvol_pos_other]:

                self.start[__nvol_pos_self] = other.start[__nvol_pos_other]
                self.id[__nvol_pos_self] = other.id[__nvol_pos_other]
                self.name[__nvol_pos_self] = other.name[__nvol_pos_other]
                self.stop[__nvol_pos_self] = other.stop[__nvol_pos_other]
                other.__truncate(__vol_pos_other)

            else:

                other.start[__nvol_pos_other] = self.start[__nvol_pos_self]
                other.id[__nvol_pos_other] = self.id[__nvol_pos_self]
                other.name[__nvol_pos_other] = self.name[__nvol_pos_self]
                other.stop[__nvol_pos_other] = self.stop[__nvol_pos_self]

                self.__truncate(__vol_pos_self)

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

    res = [new_combined.name, new_combined.start, new_combined.id,
           new_combined.remaining_round, new_combined.volatile]

    for i in res:
        print(i)
