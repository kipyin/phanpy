#!/usr/bin/env python3
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

    A ``non-volatile`` status is one of the following: paralysis, sleep,
    freeze, burn, and poison, with some sub-categories under each if
    they exist. Non-volatile statuses cannot stack; one Pokémon can
    only have one non-volatile status each time.

    A ``volatile`` status is the one that does not exist out side of a
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
            The ``ailment_id`` in ``move_meta_ailments.csv``. If no
            match is found, then randomly generate a pseudo-id.
        name : numpy.array of str
            The name of the status(es).
        volatile : numpy.array of bool
            True for volatile statuses, and False for non-volatile
            statuses (id in 0~5).

    Built-in Methods
    ----------------
        __add__ :
        __len__ :
        __iter__ :


    See also
    --------
        https://bulbapedia.bulbagarden.net/wiki/Status_condition
    """

    def __init__(self, status=None, duration=float('inf')):

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
        # >>> my_status += Status('freeze')
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
            ...     # do something

        """
        return self

    def __next__(self):

        if self.__current >= len(self.name):
            raise StopIteration

        else:
            self.__current += 1
            return list(self.name)[self.__current - 1]

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
        new = Status(0)

        new.duration = self.duration
        new.name = self.name
        new.id = self.id
        new.volatile = self.volatile

        if self.volatile.all() or other.volatile.all():
            # As long as not both of them have a non-volatile status
            # at the same time...(double negative, sorry).
            new.duration = np.append(self.duration, other.duration)
            new.id = np.append(self.id, other.id)
            new.name = np.append(self.name, other.name)
            new.volatile = np.append(self.volatile, other.volatile)
        else:
            # If both of them have a non-volatile status at the same
            # time, replace `self`'s non-volatile status with that of
            # `other`'s.
            nvol_pos = np.where(~self.volatile)[0][0]

            new.duration[nvol_pos] = other.duration[0]
            new.id[nvol_pos] = other.id[0]
            new.name[nvol_pos] = other.name[0]
            new.volatile[nvol_pos] = other.volatile[0]

        return new

    def __bool__(self):
        """Returns True if 0 is not in the status id's.

        Usage
        -----
            >>> 'bad' if some_pokemon.status else 'good'

        """
        return True if 0 not in self.id and len(self.id) == 1 else False

    def __eq__(self, other):
        return set(self.name) == set(other.name)

    def __hash__(self):
        """Returns the names as a set."""
        return set(self.name)

    def remove(self, which_status):
        """Remove the given status. `which_status` can be a valid status
        id, or a valid status name. If no instances of `which_status` is
        found, removes nothing.

        """

        if which_status in list(self.name):
            # There should be at most 1 occurance.
            mask = self.name != which_status
        elif which_status in list(self.id):
            mask = self.id != which_status
        else:
            mask = self.name == self.name
            print('Warning: Status({}) is not in the list. '
                  'Nothing is removed.'.format(which_status))

        self.id = self.id[mask]
        self.name = self.name[mask]
        self.duration = self.duration[mask]
        self.volatile = self.volatile[mask]

    def reduce(self):
        """Subtract 1 from all durations."""
        self.duration -= 1
        if 0 in self.duration:
            mask = self.duration != 0
            self.name = self.name[mask]
            self.id = self.id[mask]
            self.volatile = self.volatile[mask]
            self.duration = self.duration[mask]


def test():

    poison = Status(5)
    leech_seed = Status(18, 5)
    combined = leech_seed + poison
    burn = Status(4)
    combined += burn
    nightmare = Status(9, 5)
    new_combined = poison + nightmare + combined
    new_combined.reduce()
    new_combined.reduce()

    res = [new_combined.name, new_combined.id, new_combined.duration,
           new_combined.volatile]

    for i in res:
        print(i)

    print(0 in Status(0))
    print('poison' in new_combined)
    new_combined.remove(4)
    print(new_combined.duration)
    print([3 if new_combined else 5])
    print([Status(x) for x in range(4)])
    print(set(new_combined))


# test()
