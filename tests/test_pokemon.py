#!/usr/bin/env python3
import pytest

import os
import sys

file_path = os.path.dirname(os.path.abspath(__file__))
root_path = file_path.replace('/mechanisms/tests', '')
sys.path.append(root_path) if root_path not in sys.path else None

from mechanisms.core.pokemon import Pokemon, Trainer
from mechanisms.data import tables as tb


class TestPokemon():

    def test_pokemon_id_over_10000(self):
        p = Pokemon(10001)
        assert p.name == 'deoxys-attack'

    def test_pokemon_types_single(self):
        p = Pokemon(10001)
        assert p.types == [14]

    def test_pokemon_types_double(self):
        p = Pokemon(10004)
        assert p.types == [7, 5]

    def test_pokemon_effort_values_sum(self):
        p = Pokemon(10001)
        assert sum(p.ev.values) == 510

    def test_pokemon_nature_id_assignment(self):
        p = Pokemon(10001)
        p.nature.id = 18  # lax nature, decrease 5, increase 3.
        assert p.nature.id == 18

    def test_pokemon_nature_modifier_increase(self):
        p = Pokemon(10001)
        p.set_nature(18)
        assert p.nature_modifier.defense == 1.1
        assert p.nature_modifier.specialDefense == 0.9
