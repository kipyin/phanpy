#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 17:20:44 2017

@author: Kip
"""
import pandas as pd

path = './data/csv/'

with open(path + 'experience.csv') as csv_file:
    experience = pd.read_csv(csv_file)

with open(path + 'moves.csv') as csv_file:
    moves = pd.read_csv(csv_file)

with open(path + 'move_meta.csv') as csv_file:
    move_meta = pd.read_csv(csv_file)

with open(path + 'move_meta_stat_changes.csv') as csv_file:
    move_meta_stat_changes = pd.read_csv(csv_file)

with open(path + 'natures.csv') as csv_file:
    natures = pd.read_csv(csv_file)

with open(path + 'pokemon_abilities.csv') as csv_file:
    pokemon_abilities = pd.read_csv(csv_file)

with open(path + 'pokemon_moves.csv') as csv_file:
    pokemon_moves = pd.read_csv(csv_file)

with open(path + 'pokemon_species.csv') as csv_file:
    pokemon_species = pd.read_csv(csv_file)

with open(path + 'pokemon_stats.csv') as csv_file:
    pokemon_stats = pd.read_csv(csv_file)

with open(path + 'pokemon_types.csv') as csv_file:
    pokemon_types = pd.read_csv(csv_file)

with open(path + 'pokemon.csv') as csv_file:
    pokemon_data = pd.read_csv(csv_file)

with open(path + 'types.csv') as csv_file:
    types = pd.read_csv(csv_file)

with open(path + 'type_efficacy.csv') as csv_file:
    type_efficacy = pd.read_csv(csv_file)

with open(path + 'version_group_regions.csv') as csv_file:
    version_group_regions = pd.read_csv(csv_file)

with open(path + 'versions.csv') as csv_file:
    versions = pd.read_csv(csv_file)


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


VERSION_GROUP_ID, REGION_ID, VERSION_ID = which_version('platinum')


__condition = pokemon_moves["version_group_id"] == VERSION_GROUP_ID
pokemon_moves = pokemon_moves[__condition]


__condition = moves["generation_id"] <= REGION_ID
moves = moves[__condition]
