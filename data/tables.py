#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 17:20:44 2017

@author: Kip
"""
from pandas import read_csv

from mechanisms.config import VERSION_GROUP_ID, REGION_ID, DATA_PATH


path = DATA_PATH

# FIXME: make these tables generation-friendly.

with open(path + 'experience.csv') as csv_file:
    experience = read_csv(csv_file)

with open(path + 'items.csv') as csv_file:
    items = read_csv(csv_file)

with open(path + 'item_flags.csv') as csv_file:
    item_flags = read_csv(csv_file)

with open(path + 'item_flag_map.csv') as csv_file:
    item_flag_map = read_csv(csv_file)

with open(path + 'item_fling_effects.csv') as csv_file:
    item_fling_effects = read_csv(csv_file)

with open(path + 'moves.csv') as csv_file:
    moves = read_csv(csv_file)

    __condition = moves["generation_id"] <= REGION_ID
    moves = moves[__condition]

with open(path + 'move_meta.csv') as csv_file:
    move_meta = read_csv(csv_file)

with open(path + 'move_meta_ailments.csv') as csv_file:
    ailments = read_csv(csv_file)

with open(path + 'move_meta_stat_changes.csv') as csv_file:
    move_meta_stat_changes = read_csv(csv_file)

with open(path + 'natures.csv') as csv_file:
    natures = read_csv(csv_file)

with open(path + 'pokemon_abilities.csv') as csv_file:
    pokemon_abilities = read_csv(csv_file)

with open(path + 'pokemon_moves.csv') as csv_file:
    pokemon_moves = read_csv(csv_file)

    __condition = pokemon_moves["version_group_id"] == VERSION_GROUP_ID
    pokemon_moves = pokemon_moves[__condition]

with open(path + 'pokemon_species.csv') as csv_file:
    pokemon_species = read_csv(csv_file)

with open(path + 'pokemon_stats.csv') as csv_file:
    pokemon_stats = read_csv(csv_file)

if REGION_ID <= 5:
    with open(path + 'pokemon_types.csv') as csv_file:
        pokemon_types = read_csv(csv_file)
else:
    with open(path + 'pokemon_types_gen_6.csv') as csv_file:
        pokemon_types = read_csv(csv_file)

with open(path + 'pokemon.csv') as csv_file:
    pokemon = read_csv(csv_file)

with open(path + 'types.csv') as csv_file:
    types = read_csv(csv_file)


custom_path = DATA_PATH + 'custom/'

with open(custom_path + 'move_flag_map.csv') as csv_file:
    move_flag_map = read_csv(csv_file)

with open(custom_path + 'move_natural_gift.csv') as csv_file:
    move_natural_gift = read_csv(csv_file)
