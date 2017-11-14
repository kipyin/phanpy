#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import os, sys

file_path = os.path.dirname(os.path.abspath(__file__))
root_path = file_path.replace('/phanpy/tests', '')
sys.path.append(root_path) if root_path not in sys.path else None

import numpy as np
from phanpy.core.objects import Status, Item, Move, Pokemon, Trainer


class TestItems():

    def test_no_item(self):
        item = Item(0)
        assert item.name == 'no-item'
        assert item.category_id == 23
        assert item.fling.power == 0
        assert item.fling.effect_id == 0
        assert item.fling.effect_name == 'no-effect'
        assert list(item.flags.id.values) == []

    def test_flags_id_and_name_map(self):
        item = Item(1)
        assert sorted(item.flags.id.values) == sorted([1, 2, 4, 5])
        assert sorted(item.flags.name.values) == sorted(['countable', 'consumable',
                                                         'usable-in-battle',
                                                         'holdable'])

    def test_instantiate_item_with_undefined_fling_effects(self):
        item = Item(1)
        assert item.name == 'master-ball'
        assert item.category_id == 34
        assert item.fling.power == 0
        assert item.fling.effect_id == 0
        assert item.fling.effect_name == 'no-effect'

    def test_instantiate_item_with_defined_fling_effects(self):
        item = Item(126)
        assert item.name == 'cheri-berry'
        assert item.category_id == 3
        assert item.fling.power == 10
        assert item.fling.effect_id == 3
        assert item.fling.effect_name == 'berry-effect'
        assert item.flags.id.values == [7]


class TestStatusInstantiation():

    def test_declare_a_status_by_id_from_the_table(self):
        assert Status(5).name[0] == 'poison'

    def test_declare_a_status_with_a_timer(self):
        assert Status(5, 5).duration[0] == 5

    def test_declare_a_status_by_name_from_the_table(self):
        assert Status('poison').id[0] == 5

    def test_declare_a_custom_status(self):
        trick_room = Status('trick-room', 5)
        assert trick_room.id[0] >= 100000
        assert trick_room.duration[0] == 5
        assert trick_room.volatile[0] == True

    def test_status_volatility(self):
        assert Status(20).volatile[0] == True
        assert Status(0).volatile[0] == False


@pytest.fixture(scope='function')
def setUpStatus():
    poison = Status(5)
    burn = Status('burn')
    confused = Status('confused', 5)
    disabled = Status('disabled', 4)
    yield poison, burn, confused, disabled


class TestStatusAddition():

    def test_add_two_non_volatile(self, setUpStatus):

        poison, burn, __, __ = setUpStatus
        non_volatile = poison + burn  # burn should override poison
        assert non_volatile.name == ['burn']
        # Check if the original ones are mutated or not.
        assert poison.name == ['poison']
        assert burn.name == ['burn']

    def test_add_a_volatile_to_non_volatile(self, setUpStatus):

        poison, __, confused, __ = setUpStatus
        mixed = poison + confused
        assert sorted(mixed.name) == sorted(['poison', 'confused'])
        assert sorted(mixed.duration) == sorted([float('inf'), 5])

    def test_add_two_volatile_statuses(self, setUpStatus):
        __, __, confused, disabled = setUpStatus
        volatile = confused + disabled
        assert sorted(volatile.name) == sorted(['confused', 'disabled'])
        assert sorted(volatile.duration) == sorted([5, 4])

    def test_add_a_status_to_a_mixed(self, setUpStatus):

        poison, __, confused, disabled = setUpStatus
        volatile = confused + disabled
        mixed2 = volatile + poison
        assert sorted(mixed2.name) == sorted(['confused', 'disabled', 'poison'])
        assert sorted(mixed2.volatile) == sorted([True, True, False])

    def test_add_multiple_in_one_line(self, setUpStatus):
        __, burn, confused, disabled = setUpStatus
        mixed = burn + confused + disabled
        assert sorted(mixed.name) == sorted(['burn', 'confused', 'disabled'])


class TestStatusMethods():

    def test_remove_an_existing_status_by_name(self, setUpStatus):
        poison, __, confused, disabled = setUpStatus
        combined = poison + confused + disabled
        combined.remove('poison')
        assert sorted(combined.name) == sorted(['confused', 'disabled'])
        assert sorted(combined.duration) == sorted([5, 4])
        assert sorted(combined.volatile) == sorted([True, True])

    def test_remove_an_existing_status_by_id(self, setUpStatus):
        poison, __, confused, disabled = setUpStatus
        combined = poison + confused + disabled
        combined.remove(5)
        assert sorted(combined.name) == sorted(['confused', 'disabled'])
        assert sorted(combined.duration) == sorted([5, 4])
        assert sorted(combined.volatile) == sorted([True, True])

    def test_remove_the_only_status(self):
        poison = Status(5)
        poison.remove('poison')
        assert poison.id == np.array([0])
        assert poison.name == np.array(['normal'])
        assert poison.duration == np.array([float('inf')])
        assert poison.volatile == np.array([False])

    def test_remove_a_non_existing_status(self):
        poison = Status(5)
        with pytest.raises(KeyError):
            poison.remove('burn')

    def test_reduce_duration_by_1(self, setUpStatus):
        __, burn, confused, disabled = setUpStatus
        mixed = burn + confused + disabled
        mixed.reduce()
        assert sorted(mixed.duration) == sorted([float('inf'), 4, 3])

    def test_reduce_the_duration_by_1_where_the_duration_was_1(self):
        burn = Status('burn', 1)
        confused = Status('confused', 5)
        mixed = burn + confused
        mixed.reduce()
        assert mixed.name == ['confused']
        assert mixed.duration == [4]
        assert mixed.volatile == [True]


@pytest.fixture(scope='function')
def setUpPokemon():
    p = Pokemon(10001)
    yield p


class TestPokemon():

    def test_id_over_10000(self, setUpPokemon):
        p = setUpPokemon
        assert p.name == 'deoxys-attack'

    def test_types_single(self, setUpPokemon):
        p = setUpPokemon
        assert p.types == [14]

    def test_types_double(self):
        p = Pokemon(10004)
        assert p.types == [7, 5]

    def test_effort_values_sum(self, setUpPokemon):
        p = setUpPokemon
        assert sum(p.ev.values) == 510

    def test_nature_id_assignment(self, setUpPokemon):
        p = setUpPokemon
        p.set_nature(18)  # lax nature, decrease 5, increase 3.
        assert p.nature.id == 18

    def test_set_nature_by_name(self, setUpPokemon):
        p = setUpPokemon
        p.set_nature('lax')  # 18
        assert p.nature.id == 18

    def test_nature_modifier(self, setUpPokemon):
        p = setUpPokemon
        p.set_nature(18)
        assert p.nature_modifier.defense == 1.1
        assert p.nature_modifier.specialDefense == 0.9

    def test_set_iv(self, setUpPokemon):
        p = setUpPokemon
        p.set_iv([31. for x in range(6)])
        assert p.iv.defense == 31.

    def test_set_ev(self, setUpPokemon):
        p = setUpPokemon
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

    def test_stage_factor_changes_when_stage_changes(self, setUpPokemon):
        p = setUpPokemon
        p.stage.attack += 3  # the factor should be multiplied by 2.5
        assert p.stage_factor.attack == 2.5

    def test_current_stats_change_when_factors_change(self, setUpPokemon):
        p = setUpPokemon
        p.stage.attack += 3
        assert p.current.attack == np.floor(p.stats.attack * 2.5)

    def test_add_received_damage(self, setUpPokemon):
        p = setUpPokemon
        p.history.damage.appendleft(288)
        p.history.damage.appendleft(199)
        assert p.history.damage[0] == 199

    def test_add_stage(self, setUpPokemon):
        p = setUpPokemon
        p.history.stage += 5
        assert p.history.stage == 5

    def test_set_moves(self, setUpPokemon):
        p = setUpPokemon
        first_4_moves = [Move(x) for x in range(1, 5)]
        p.moves = first_4_moves
        for i in range(4):
            assert p.moves[i].name == first_4_moves[i].name

    def test_set_pp_and_power(self, setUpPokemon):
        p = setUpPokemon
        p.moves[0] = Move(33)  # tackle, power 40, pp 35, accuracy 100.
        p.moves[0].pp -= 4
        p.moves[0].power *= 2
        assert p.moves[0].pp == 31
        assert p.moves[0].power == 80
        assert p.moves[0].power != Move(33).power

    def test_holding_item303_changes_critical_stage(self, setUpPokemon):
        p = setUpPokemon
        p.item = Item(303)
        assert p.stage.critical == 1.

    def test_dual_abilities_successfully_initiated(self):
        p = Pokemon(19)
        assert p.ability in [50, 62]

    def test_single_ability_successfully_initiated(self):
        p = Pokemon(1)
        assert p.ability == 65

    def test_reset_current_stats(self, setUpPokemon):
        p = setUpPokemon
        p.stage += 3
        p.reset_current()
        assert p.current.attack == p.stats.attack

    def test_two_pokemons_are_equal(self, setUpPokemon):
        p = setUpPokemon
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
