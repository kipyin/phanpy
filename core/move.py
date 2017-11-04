#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 16:08:21 2017

@author: Kip
"""

import numpy as np

from mechanisms.tables import moves, move_meta, move_meta_stat_changes


class Move():
    """A basic class for all move objects.

    Usage
    -----
        >>> m = Move(4)
        >>> m
        comet-punch
        >>> m.power
        18.0
        >>> Move('natural-gift').id
        363

    Properties
    ----------
        id : int
            The id of the given move.
        identifier : str
            The name of the move. Equivalent to ``name``.
        damage_class_id : {1, 2, 3}
            Mapping: {1: 'status', 2: 'physical', 3: 'special'}.
        effect_chance : int
            If the move comes with an effect, ``efect_chance`` is the
            probability of triggering such an effect, multiplied by
            100.
        category_id : int
            See the file ``move_meta_categories.csv`` for the mapping.
        drain : int
            A possitive number means draining from the opponent's HP.
            A negative number means such a move has a chance to cause
            the user a certain damage.
        crit_rate : int
            If this number is not 0, then that means there is a chance
            that this move will increase (+) or decrease (-) the user's
            critical stage.
    """

    def __init__(self, which_move):

        try:
            if type(which_move) is str:
                move_id = int(moves[moves["identifier"] == which_move].id)

            elif str(which_move).isnumeric():
                move_id = which_move

        except TypeError:
            raise TypeError("Move(x) where x is either a move_id"
                            " or a move_name")

        label = moves.index.values[np.where(moves.id.values == move_id)]

        self.id = moves.loc[label, "id"].values[0]
        self.identifier = moves.loc[label, "identifier"].values[0]
        self.generation_id = moves.loc[label, "generation_id"].values[0]
        self.type_id = moves.loc[label, "type_id"].values[0]
        self.power = moves.loc[label, "power"].values[0]
        self.pp = moves.loc[label, "pp"].values[0]
        self.accuracy = moves.loc[label, "accuracy"].values[0]
        self.priority = moves.loc[label, "priority"].values[0]
        self.target_id = moves.loc[label, "target_id"].values[0]
        self.damage_class_id = moves.loc[label, "damage_class_id"].values[0]
        self.effect_id = moves.loc[label, "effect_id"].values[0]
        self.effect_chance = moves.loc[label, "effect_chance"].values[0]

        self.category_id = move_meta.loc[label, "meta_category_id"].values[0]
        self.ailment_id = move_meta.loc[label, "meta_ailment_id"].values[0]
        self.min_hits = move_meta.loc[label, "min_hits"].values[0]
        self.max_hits = move_meta.loc[label, "max_hits"].values[0]
        self.min_turns = move_meta.loc[label, "min_turns"].values[0]
        self.max_turns = move_meta.loc[label, "max_turns"].values[0]
        self.drain = move_meta.loc[label, "drain"].values[0]
        self.healing = move_meta.loc[label, "healing"].values[0]
        self.crit_rate = move_meta.loc[label, "crit_rate"].values[0]
        self.ailment_chance = move_meta.loc[label, "ailment_chance"].values[0]
        self.flinch_chance = move_meta.loc[label, "flinch_chance"].values[0]
        self.stat_chance = move_meta.loc[label, "stat_chance"].values[0]

        if move_id in move_meta_stat_changes.move_id.values:

            __condition = move_meta_stat_changes["move_id"] == self.id

            self.stat_change = move_meta_stat_changes[__condition]

        self.name = self.identifier

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
