#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Instances of all effects.
"""
from os import sys, path
sys.path.append(path.abspath('.'))

import re
import phanpy.core.tables as tb


class Effect():
    """A parent class for all the effects.
    """

    def __init__(self, id_):

        short_desc_raw = tb.sub(tb.move_effect_prose, "move_effect_id", id_)[0]
        desc_raw = tb.sub(tb.moves, "effect_id", id_)[0]

        # Strip "[", "]" and everything in between.
        brackets = re.compile('\[.*?\]|\{.*?:|\}')
        self.id = id_

        self.short_desc = brackets.sub('', short_desc_raw)
        self.desc = brackets.sub('', desc_raw)
        self.moves = frozenset(moves_with_this_effect["identifier"].values)
