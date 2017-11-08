#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 11:08:19 2017

@author: Kip
"""
import os

from collections import namedtuple

from pandas import read_csv

turn = 1

FILE_PATH = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = FILE_PATH.replace('/mechanisms', '')
CORE_PATH = FILE_PATH + '/core'
DATA_PATH = FILE_PATH + '/data/csv/'


with open(DATA_PATH + 'version_group_regions.csv') as csv_file:
    version_group_regions = read_csv(csv_file)

with open(DATA_PATH + 'versions.csv') as csv_file:
    versions = read_csv(csv_file)


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


VERSION_GROUP_ID, REGION_ID, VERSION_ID = which_version('platinum')
