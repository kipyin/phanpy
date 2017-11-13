#!/usr/bin/env python3
import pytest

import os, sys

file_path = os.path.dirname(os.path.abspath(__file__))
root_path = file_path.replace('/phanpy/tests', '')
sys.path.append(root_path) if root_path not in sys.path else None

import numpy as np
from phanpy.core.pokemon import Pokemon, Trainer
from phanpy.core.move import Move
from phanpy.core.item import Item

@pytest.fixture(scope='function')
def setup():
    p = Pokemon(10001)
    yield p


class TestPokemon():

    def test_id_over_10000(self, setup):
        p = setup
        assert p.name == 'deoxys-attack'

    def test_types_single(self, setup):
        p = setup
        assert p.types == [14]

    def test_types_double(self):
        p = Pokemon(10004)
        assert p.types == [7, 5]

    def test_effort_values_sum(self, setup):
        p = setup
        assert sum(p.ev.values) == 510

    def test_nature_id_assignment(self, setup):
        p = setup
        p.set_nature(18)  # lax nature, decrease 5, increase 3.
        assert p.nature.id == 18

    def test_set_nature_by_name(self, setup):
        p = setup
        p.set_nature('lax')  # 18
        assert p.nature.id == 18

    def test_nature_modifier(self, setup):
        p = setup
        p.set_nature(18)
        assert p.nature_modifier.defense == 1.1
        assert p.nature_modifier.specialDefense == 0.9

    def test_set_iv(self, setup):
        p = setup
        p.set_iv([31. for x in range(6)])
        assert p.iv.defense == 31.

    def test_set_ev(self, setup):
        p = setup
        p.set_ev([31. for x in range(6)])
        assert p.ev.defense == 31.

    def test_calculated_stats(self):
        """Using the example on
        https://bulbapedia.bulbagarden.net/wiki/Statistic#Determination_of_stats
        """
        p = Pokemon('garchomp', 78)
        p.set_nature('adamant')
        p.set_iv([24, 12, 30, 16, 23, 5])
        p.set_ev([74, 190, 91, 48, 84, 23])
        expected = [289, 278, 193, 135, 171, 171]
        for i in range(6):
            assert p.stats[i] == expected[i]

    def test_stage_factor_changes_when_stage_changes(self, setup):
        p = setup
        p.stage.attack += 3  # the factor should be multiplied by 2.5
        assert p.stage_factor.attack == 2.5

    def test_current_stats_change_when_factors_change(self, setup):
        p = setup
        p.stage.attack += 3
        assert p.current.attack == np.floor(p.stats.attack * 2.5)

    def test_add_received_damage(self, setup):
        p = setup
        p.history.damage.appendleft(288)
        p.history.damage.appendleft(199)
        assert p.history.damage[0] == 199

    def test_add_stage(self, setup):
        p = setup
        p.history.stage += 5
        assert p.history.stage == 5

    def test_set_moves(self, setup):
        p = setup
        first_4_moves = [Move(x) for x in range(1, 5)]
        p.moves = first_4_moves
        for i in range(4):
            assert p.moves[i].name == first_4_moves[i].name

    def test_set_pp_and_power(self, setup):
        p = setup
        p.moves[0] = Move(33)  # tackle, power 40, pp 35, accuracy 100.
        p.moves[0].pp -= 4
        p.moves[0].power *= 2
        assert p.moves[0].pp == 31
        assert p.moves[0].power == 80
        assert p.moves[0].power != Move(33).power

    def test_holding_item303_changes_critical_stage(self, setup):
        p = setup
        p.item = Item(303)
        assert p.stage.critical == 1.

    def test_reset_current_stats(self, setup):
        p = setup
        p.stage += 3
        p.reset_current()
        assert p.current.attack == p.stats.attack

    def test_two_pokemons_are_equal(self, setup):
        p = setup
        q = Pokemon(10001)
        assert p != q
        q.set_iv(p.iv.values)
        q.unique_id = p.unique_id
        assert p == q

    def test_trainer_set_pokemon(self):
        t = Trainer('Satoshi')
        t.set_pokemon(3, Pokemon(10005))
        assert t.party(3).name == 'wormadam-trash'

    def test_set_trainers_pokemons_moves(self):
        t = Trainer('Satoshi')
        t.set_pokemon(3, Pokemon(10001))
        t.party(1).moves[1] = Move(33)
        assert t.party(1).moves[1].name == 'tackle'
