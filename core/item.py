#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 18:35:24 2017

@author: Kip
"""
import numpy as np
from pandas import Series, DataFrame

from mechanisms.core.status import Status
from mechanisms.data.tables import (items, item_fling_effects,
                                    item_flags, item_flag_map)


class Item():
    """A class for items.
    """

    def __init__(self, which_item):

        if str(which_item).isnumeric():
            # If which_item is a valid item id, get its name from the
            # table.
            if which_item not in items.id.values:
                raise KeyError("Invalid item id.")
            else:
                __subset = items[items["id"] == which_item]
                __name = __subset["identifier"].values[0]
                __id = which_item

        else:
            if which_item in items.identifier.values:
                # If which_item is a valid item namem, get the item id
                # from the table.
                __subset = items[items["identifier"] == which_item]
                __id = __subset["id"].values[0]
            else:
                # Otherwise, set the id to a random 6-digit number.
                __id = np.random.randint(100000, 199999)
            __name = which_item

        __label = __id - 1

        self.id = __id
        self.name = __name

        self.category_id = items.loc[__label, "category_id"]
        self.fling_power = items.loc[__label, "fling_power"]

        __effect_id = items.loc[__label, "fling_effect_id"]
        __subset = item_fling_effects[item_fling_effects["id"] == __effect_id]
        __effect_name = __subset["identifier"].values

        if np.isnan(__effect_id):
            # If there is no effect...
            __effect_id = 0
            __effect_name = 'no-effect'

        self.fling_effect = Series(index=["id", "name"],
                                   data=[__effect_id, __effect_name])

        __subset = item_flag_map[item_flag_map["item_id"] == self.id]
        __flag_id = DataFrame({"id": __subset.item_flag_id})
        self.flag = item_flags.merge(__flag_id, how="inner",
                                     on="id")
        self.flag.columns = ["id", "name"]

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def fling(self, other):
        """"Flings the item to the opponent.
        Activates the item's effect.
        """

        fling_id = self.fling_effect.id

        if fling_id == 1:
            other.status += Status('badly-poison')

        elif fling_id == 2:
            other.status += Status('burn')

        elif fling_id == 3:
            # XXX: ...somehow uses f1's item on f2.
            pass

        elif fling_id == 4:
            # XXX: ...somehow uses f1's herb on f2
            pass

        elif fling_id == 5:
            other.status += Status('paralysis')

        elif fling_id == 6:
            other.status += Status('poison')

        else:
            # XXX: flinch if the opponent has not gone this turn.
            pass
