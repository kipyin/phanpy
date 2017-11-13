#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import os, sys

file_path = os.path.dirname(os.path.abspath(__file__))
root_path = file_path.replace('/phanpy/tests', '')
sys.path.append(root_path) if root_path not in sys.path else None

from phanpy.core.move import Move
from phanpy.core.pokemon import Pokemon
from phanpy.main import attacking_order


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

    p1.moves[1] = Move('snatch')
    p2.moves[1] = Move('snatch')

    p1_move = p1.moves[1]
    p2_move = p2.moves[1]

    f1, m1, f2, m2 = attacking_order(p1, p1_move, p2, p2_move)

    assert p1.current.speed < p2.current.speed
    assert p2 == f1
    assert p1 == f2
