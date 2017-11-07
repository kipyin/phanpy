#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 17:33:44 2017

@author: Kip
"""
from functools import reduce

from pandas import read_csv

from mechanisms.config import DATA_PATH, REGION_ID

path = DATA_PATH

with open(path + 'type_efficacy.csv') as csv_file:
    type_efficacy = read_csv(csv_file)

if REGION_ID <= 5:
    # `fairy` type is added from Gen.6 onward.
    type_efficacy = type_efficacy['damage_factor'
                                  ''].values.reshape(18, 18)[:-1, :-1]/100.


def efficacy(atk_type, tar_types):
    """Returns an `int` that represents the type efficacy between the
    attack type and the target type(s).

    Usage
    -----
        >>> efficacy(4,[9])  # How effective is poison (4) against
        ...                  steel (9)?
        0  # poison moves have no effect on steel-type Pokémons.

        >>> efficacy(17, [2, 14]) # How effective is dark (17) against
        ...     a Pokémon with a fighting (2) and psychic (14) type?
        1  # Because dark is 1/2 effective against fighting and twice as
        ...     effective against psychic.

    Parameters
    ----------
        atk_type : int
            The attacker's type. Up to Gen.6 this can only be one `int`.
        tar_types : array-like objects
            Technically, the length of the array is not limited.
            But for our purposes (calculating in-battle effectiveness),
            this is no more than two. Although no limitation is forced.

    Returns
    -------
        efficacy : float
            The function returns a `float`, which is the multiplicative
            effectiveness of atk_type to tar_types.

    """

    __efficacies = map(lambda x: type_efficacy[atk_type-1, x-1], tar_types)

    return reduce(lambda x, y: x * y, __efficacies)
