#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import os, sys

file_path = os.path.dirname(os.path.abspath(__file__))
root_path = file_path.replace('/phanpy/tests', '')
sys.path.append(root_path) if root_path not in sys.path else None

from phanpy.core.objects import Item, Move, Pokemon, Status
from phanpy.core.tables import which_ability
from phanpy.core.algorithms import attacking_order


def test_compare_priorities():
    """quick-attack is of priority +1 and snatch is of priority +4.
    snatch will attack first.
    """

    p1 = Pokemon(123)
    p2 = Pokemon(345)

    p1.moves[1] = Move('quick-attack')
    p2.moves[1] = Move('snatch')

    p1_move = p1.moves[1]
    p2_move = p2.moves[1]

    p1.stage.speed = 6
    p2.stage.speed = -6

    f1, m1, f2, m2 = attacking_order(p1, p1_move, p2, p2_move)

    assert p1.current.speed > p2.current.speed
    assert p2 == f1
    assert p1 == f2
    assert p1.order == 2
    assert p2.order == 1

def test_same_priority_faster_attacks_first():
    """If both pokemon use moves with the same priority (regardless of
    the level of the priority), their speeds are compared.
    """

    p1 = Pokemon('shuckle')  # has the lowest speed among all.
    p2 = Pokemon('deoxys-speed') # has the highest speed.
    p1.ability, p2.ability = 1, 1  # ``stench``

    p1.moves[1] = Move('snatch')
    p2.moves[1] = Move('snatch')

    p1_move = p1.moves[1]
    p2_move = p2.moves[1]

    f1, m1, f2, m2 = attacking_order(p1, p1_move, p2, p2_move)

    assert p1.current.speed < p2.current.speed
    assert p2 == f1
    assert p1 == f2

def test_both_holding_quick_claw_pass():
    """Assign the same item for both shuckle and deoxys-speed form.
    The result should be identical to the """
    p1 = Pokemon('shuckle')
    p2 = Pokemon('deoxys-speed')
    p1.ability, p2.ability = 1, 1

    p1.moves[1] = Move('snatch')
    p2.moves[1] = Move('snatch')

    p1_move = p1.moves[1]
    p2_move = p2.moves[1]

    p1.item = Item('quick-claw')
    p2.item = Item('quick-claw')

    f1, m1, f2, m2 = attacking_order(p1, p1_move, p2, p2_move)

    assert p2 == f1
    assert p1 == f2

def test_holding_lagging_tail_moves_last():
    p1 = Pokemon('shuckle')
    p2 = Pokemon('deoxys-speed')
    p1.ability, p2.ability = 1, 1

    p1.moves[1], p2.moves[1] = Move('snatch'), Move('snatch')

    p1_move, p2_move = p1.moves[1], p2.moves[1]

    p1.item = Item(0)
    p2.item = Item('lagging-tail')

    f1, m1, f2, m2 = attacking_order(p1, p1_move, p2, p2_move)

    assert p1 == f1
    assert p2 == f2

def test_pokemon_with_stall_ability_moves_last():
    p1 = Pokemon('shuckle')
    p2 = Pokemon('deoxys-speed')

    p1.ability = 1
    p2.ability = which_ability('stall')

    p1_move, p2_move = Move('snatch'), Move('snatch')

    f1, m1, f2, m2 = attacking_order(p1, p1_move, p2, p2_move)

    assert p1 == f1
    assert p2 == f2

def test_ability_override_field_effects():
    p1 = Pokemon('shuckle')
    p2 = Pokemon('deoxys-speed')

    p1.ability = which_ability('stall')
    p2.ability = 1

    p1_move, p2_move = Move('snatch'), Move('snatch')

    p1.status += Status('trick-room')
    p2.status += Status('trick-room')

    f1, m1, f2, m2 = attacking_order(p1, p1_move, p2, p2_move)

    assert p1 == f2
    assert p2 == f1


def test_trick_room_reverses_the_order():
    p1 = Pokemon('shuckle')
    p2 = Pokemon('deoxys-speed')

    p1_move, p2_move = Move('snatch'), Move('snatch')

    p1.status += Status('trick-room', 5)
    p2.status += Status('trick-room', 5)

    f1, m1, f2, m2 = attacking_order(p1, p1_move, p2, p2_move)

    assert p1 == f1
    assert p2 == f2
