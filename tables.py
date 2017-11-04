#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 17:20:44 2017

@author: Kip
"""
import pandas as pd

from assistive_functions import which_version


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
    pokemon = pd.read_csv(csv_file)

with open(path + 'types.csv') as csv_file:
    types = pd.read_csv(csv_file)


VERSION_GROUP_ID, REGION_ID, VERSION_ID = which_version('platinum')

__condition = pokemon_moves["version_group_id"] == VERSION_GROUP_ID
pokemon_moves = pokemon_moves[__condition]

__condition = moves["generation_id"] <= REGION_ID
moves = moves[__condition]
