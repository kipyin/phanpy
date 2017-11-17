#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import os, sys

file_path = os.path.dirname(os.path.abspath(__file__))
root_path = file_path.replace('/phanpy/tests', '')
sys.path.append(root_path) if root_path not in sys.path else None

from phanpy.core.effects import Effect

class TestEffects():

    def test_effect_init(self):
        effect = Effect(6)
        assert effect.short_desc == "Has a $effect_chance% chance to freeze the target."
        assert effect.desc == "Inflicts regular-damage.  Has a $effect_chance% chance to freeze the target."
        assert effect.moves == frozenset(['ice-punch', 'ice-beam', 'powder-snow'])
