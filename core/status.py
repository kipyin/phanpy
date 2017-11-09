# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 04:22:57 2017
@author: Kip
"""

import numpy as np

from mechanisms.data.tables import ailments


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
    battle. Some classic examples would be confusion, ingrain,
    infatuation, etc. One can have multiple volatile statuses.

    Usage
    -----
        >>> poison = Status(5)
        >>> leech_seed = Status(18,5)
        >>> combined = poison + leech_seed
        >>> combined.duration
        array([ inf,   5.])


    Attributes
    ----------
        id : numpy.array of int
            The `ailment_id` in `move_meta_ailments.csv`.
        name : numpy.array of str
            The name of the status(es).
        volatile : numpy.array of bool
            True for volatile statuses, and False for non-volatile
            statuses (id in 1~5).

    Built-in Methods
    ----------------
        __add__ :
        __len__ :
        __iter__ :


    See also
    --------
        https://bulbapedia.bulbagarden.net/wiki/Status_condition
    """

    def __init__(self, status, duration=float('inf')):

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

        self.id = np.array([__status_id], dtype='int64')
        # The dtype '<U24' means that it is a little-endian unicode
        # with a length of 24. In other words, it supports a maximum
        # of 24-character name.
        #
        # For example, if I define a Status as follows:
        #
        # >>> my_status = Status('123456789012345678901234567890')
        #
        # i.e. it is defined to have a 30-char name, but dtype='<U24'
        # limits it to 24 chars. Therefore, if then we do
        #
        # >>> my_status.name
        #
        # We will only get array(['freeze', '123456789012345678901234'],
        # dtype='<U24').
        # 24-char should be enought, as the longest statuses in game is
        # 'whipping-up-a-whirlwind' (23-chars).
        self.name = np.array([__name], dtype='<U24')
        self.volatile = np.array([__volatile], dtype='bool')
        self.duration = np.array([duration], dtype='float64')

        # A counter for __next__
        self.__current = 0

    def __repr__(self):
        return ', '.join(self.name)

    def __len__(self):
        return len(self.name)

    def __iter__(self):
        """Make Status iterable.

        Usage
        -----
            >>> for status in Pokemon(123).status
            ...

        """
        return self

    def __next__(self):

        if self.__current >= len(self.name):
            raise StopIteration

        else:
            self.__current += 1
            yield list(self.name)[self.__current - 1]

    def __contains__(self, item):
        """
            >>> 'flinch' in Pokemon(123).status
            >>> 5 in Pokemon(123).status

        """
        if type(item) is str:
            return True if item in self.name else False

        elif str(item).isnumeric():
            return True if item in self.id else False

        else:
            return False

    def __add__(self, other):
        """Adds two statuses together.

        Append volatile statuses; replace non-volatile statuses.
        """
        if self.volatile.all() or self.volatile.all():
            # As long as not both of them have a non-volatile status
            # at the same time...(double negative, sorry).
            self.duration = np.append(self.duration, other.duration)
            self.id = np.append(self.id, other.id)
            self.name = np.append(self.name, other.name)
            self.volatile = np.append(self.volatile, other.volatile)
        else:
            # If both of them have a non-volatile status at the same
            # time, replace `self`'s non-volatile status with that of
            # `other`'s.
            nvol_pos = np.where(~self.volatile)[0][0]

            self.duration[nvol_pos] = other.duration[0]
            self.id[nvol_pos] = other.id[0]
            self.name = other.name[0]
            self.volatile = other.volatile[0]

        return self

    def __bool__(self):
        """Returns True if 0 is not in the status id's.

            >>> 'bad' if some_pokemon.status else 'good'
        """
        return True if 0 not in self.id else False

    def cut(self):
        """Subtract 1 from all durations.

        """
        self.duration -= 1


def test():

    poison = Status(5)
    leech_seed = Status(18, 5)
    combined = leech_seed + poison
    burn = Status(4)
    combined += burn
    nightmare = Status(9, 5)
    new_combined = poison + nightmare + combined
    new_combined.cut()
    new_combined.cut()

    res = [new_combined.name, new_combined.id, new_combined.duration]

    for i in res:
        print(i)

    print(0 in Status(0))
    print('poison' in new_combined)


test()
