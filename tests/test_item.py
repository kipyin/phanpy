#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import os, sys

file_path = os.path.dirname(os.path.abspath(__file__))
root_path = file_path.replace('/phanpy/tests', '')
sys.path.append(root_path) if root_path not in sys.path else None

import numpy as np
from phanpy.core.objects import Item


def test_no_item():
    item = Item(0)
    assert item.name == 'no-item'
    assert item.category_id == 23
    assert item.fling.power == 0
    assert item.fling.effect_id == 0
    assert item.fling.effect_name == 'no-effect'
    assert list(item.flags.id.values) == []
    assert list(item.flags.name.values) == []


def test_instantiate_item_with_undefined_fling_effects():
    item = Item(1)
    assert item.name == 'master-ball'
    assert item.category_id == 34
    assert item.fling.power == 0
    assert item.fling.effect_id == 0
    assert item.fling.effect_name == 'no-effect'
    assert sorted(item.flags.id) == sorted([1, 2, 4, 5])
    assert sorted(item.flags.name) == sorted(['countable', 'consumable',
                                             'usable-in-battle', 'holdable'])

def test_instantiate_item_with_defined_fling_effects():
    item = Item(126)
    assert item.name == 'cheri-berry'
    assert item.category_id == 3
    assert item.fling.power == 10
    assert item.fling.effect_id == 3
    # assert item.fling.effect_name == 'no-effect'
