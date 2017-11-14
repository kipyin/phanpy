#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys
import pytest

file_path = os.path.dirname(os.path.abspath(__file__))
root_path = file_path.replace('/phanpy/tests', '')
sys.path.append(root_path) if root_path not in sys.path else None

from phanpy.core.tables import which_ability, efficacy

def test_ability_id_to_name():
    assert which_ability(10001) == 'mountaineer'

def test_ability_name_to_id():
    assert which_ability('steelworker') == 200

def test_ability_keyerror():
    with pytest.raises(KeyError):
        which_ability('some_random_string')

def test_all_efficacy():
    assert efficacy(4,[9]) == 0
    assert efficacy(17, [2, 14]) == 1
