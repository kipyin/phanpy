#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 17:33:44 2017

@author: Kip
"""
from collections import namedtuple
from functools import reduce

from pandas import read_csv


path = './data/csv/'

with open(path + 'version_group_regions.csv') as csv_file:
    version_group_regions = read_csv(csv_file)

with open(path + 'versions.csv') as csv_file:
    versions = read_csv(csv_file)

with open(path + 'type_efficacy.csv') as csv_file:
    type_efficacy = read_csv(csv_file)

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


def which_version(identifier=None,
                  VERSION_GROUP_ID=None,
                  REGION_ID=None,
                  VERSION_ID=None):
    """Returns a tuple (VERSION_GROUP_ID, REGION_ID, VERSION_ID)

    Usage
    -----
        >>> VERSION_GROUP_ID, REGION_ID, VERSION_ID =
        ...     which_version('firered')
        >>> print(VERSION_GROUP_ID, REGION_ID, VERSION_ID)
        (7, 1, 10)

    Parameters
    ----------
        identifier : str
            The official name of a game; should be in the following
            list:
            red, blue, yellow, gold, silver, crystal,
            ruby, sapphire, emerald, firered, leafgreen,
            diamond, pearl, platinum, heartgold, soulsilver,
            black, white, black-2, white-2,
            x, y, omega-ruby, alpha-sapphire, sun, moon,

    """
    __vgr = version_group_regions

    if identifier:
        try:

            __filter = versions["identifier"] == identifier
            VERSION_GROUP_ID = int(versions[__filter]["version_group_id"])

            __filter = versions["identifier"] == identifier
            VERSION_ID = int(versions[__filter]["id"])

            __filter = __vgr["version_group_id"] == int(VERSION_GROUP_ID)
            REGION_ID = int(__vgr[__filter]["region_id"])

        except Exception:

            raise ValueError(
                        "The game name should be one of the following"
                        " list:\nred, blue, yellow, gold, silver, "
                        "crystal,\nruby, sapphire, emerald, firered, "
                        "leafgreen,\ndiamond, pearl, platinum, "
                        "heartgold, soulsilver,\nblack, white, "
                        "black-2, white-2,\nx, y, omega-ruby, "
                        "alpha-sapphire, sun, moon."
                            )

    elif VERSION_GROUP_ID:
        try:

            __filter = __vgr["version_group_id"] == int(VERSION_GROUP_ID)
            REGION_ID = int(__vgr[__filter]["region_id"])

            __filter = versions["version_group_id"] == VERSION_GROUP_ID
            VERSION_ID = int(versions[__filter]["id"])

        except Exception:

            raise ValueError("Incorrect version group id.")

    elif REGION_ID:
        try:

            __filter = __vgr["region_id"] == int(REGION_ID)
            VERSION_GROUP_ID = int(__vgr[__filter]["version_group_id"])

            __filter = versions["version_group_id"] == VERSION_GROUP_ID
            VERSION_ID = int(versions[__filter]["id"])

        except Exception:

            raise ValueError("Incorrect region id.")

    elif VERSION_ID:
        try:

            __filter = versions["id"] == VERSION_ID
            VERSION_GROUP_ID = int(versions[__filter]["version_group_id"])

            __filter = __vgr["version_group_id"] == VERSION_GROUP_ID
            REGION_ID = __vgr[__filter]["region_id"]

        except Exception:

            raise ValueError("Incorrect version id.")

    else:
        pass

    VersionInfo = namedtuple('VesionInfo', ['VERSION_GROUP_ID',
                                            'REGION_ID',
                                            'VERSION_ID'])
    try:
        return VersionInfo(VERSION_GROUP_ID, REGION_ID, VERSION_ID)

    except Exception:

        raise ValueError("There should be at least one argument.")
