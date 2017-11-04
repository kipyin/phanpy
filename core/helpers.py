#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 17:33:44 2017

@author: Kip
"""
from functools import reduce

import pandas as pd


path = './data/csv/'

with open(path + 'version_group_regions.csv') as csv_file:
    version_group_regions = pd.read_csv(csv_file)

with open(path + 'versions.csv') as csv_file:
    versions = pd.read_csv(csv_file)

with open(path + 'type_efficacy.csv') as csv_file:
    type_efficacy = pd.read_csv(csv_file)

type_efficacy = type_efficacy['damage_factor'
                              ''].values.reshape(18, 18)[:-1, :-1]/100.


def efficacy(atk_type, tar_types):
    """Returns an `int` that represents the type efficacy between the
    attack type and the target type(s).

    Usage
    -----
        >>> efficacy(4,9)  # How effective is poison (4) against
        ...                  steel (9)?
        0  # poison moves have no effect on steel-type Pokémons.

        >>> efficacy(17, [2, 14]]) # How effective is dark (17) against
        ...     a Pokémon with a fighting (2) and psychic (14) type?
        1  # Because dark is 1/2 effective against fighting and twice as
        ...     effective against psychic.

    Parameters
    ----------
        atk_type : int
            The attacker's type. Up to Gen.6 this can only be one `int`.
        tar_types : array-like objects
            Theoretically, the length of the array is not limited.
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


def which_version(identifier):
    """Returns a triple VERSION_GROUP_ID, REGION_ID, VERSION_ID

    Usage
    -----
        >>> VERSION_GROUP_ID, REGION_ID, VERSION_ID =
        ...     which_version('firered')
        >>> print(VERSION_GROUP_ID, REGION_ID, VERSION_ID)
        (7, 1, 10)

    Parameters
    ----------
        identifier : The official name of a game;
        should be in the following list:
            red, blue, yellow, gold, silver, crystal,
            ruby, sapphire, emerald, firered, leafgreen,
            diamond, pearl, platinum, heartgold, soulsilver,
            black, white, black-2, white-2,
            x, y, omega-ruby, alpha-sapphire, sun, moon,

    """
    try:

        __condition = versions["identifier"] == identifier
        version_group_id = int(versions[__condition]["version_group_id"])

        __condition = versions["identifier"] == identifier
        version_id = int(versions[__condition]["id"])

        __v_g_r = version_group_regions
        __condition = __v_g_r["version_group_id"] == int(version_group_id)
        region_id = int(__v_g_r[__condition]["region_id"])

        return version_group_id, region_id, version_id

    except TypeError:

        raise TypeError(
                        "The game name should be one of the following"
                        " list:\nred, blue, yellow, gold, silver, "
                        "crystal,\nruby, sapphire, emerald, firered, "
                        "leafgreen,\ndiamond, pearl, platinum, "
                        "heartgold, soulsilver,\nblack, white, "
                        "black-2, white-2,\nx, y, omega-ruby, "
                        "alpha-sapphire, sun, moon."
                        )
