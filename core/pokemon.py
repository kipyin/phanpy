#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 15:56:47 2017

@author: Kip
"""
from collections import deque

import pandas as pd
import numpy as np

from move import Move
from status import Status
import mechanisms.tables as tb


# TODO: finish the doc string
# FIXME: make the doc string PEP8-friendly
class Pokemon():
    """A well-defined object capturing all relevant information about a
    pokémon regarding to battle simulation. Does not take abilities
    into account for now.

    Usage
    -----
        >>> foo = Pokemon(150) # Summons a mewtwo.
        >>> foo.name
        'mewtwo'
        >>> foo.stats
        hp                 62.0
        attack            127.0
        defence           105.0
        specialAttack     165.0
        specialDefence    110.0
        speed             135.0
        dtype: float64
        >>> foo.iv.specialAttack
        21

    Parameters
    ----------
        pokemon_id : int
            The national ID of a Pokémon.
              | Generation | Max Index No. |
              |      1     |       151     |
              |      2     |       251     |
              |      3     |       386     |
              |      4     |       493     |
              |      5     |       649     |
              |      6     |       721     |
              |      7     |       802     |
        level : int, default 50
            The desired level of the summoned Pokémon.
            Range from 1 to 100, endpoints included.

    Properties
    ----------
        :id                      : A unique number for each Pokémon including
                                   all the forms and variations.
        :identifier              : Alias name; the species name of the Pokémon.
        :species_id              : The Pokédex id of the Pokémon.
        :weight                  : Needed for some damage calculations.
        :base_experience         : Used for calculating experience gain in
                                   battle.
        :order                   : ???
        :is_default              : ???
        :generation_id           : See `which_version` function.
        :evolves_from_species_id : Needed for determining evolutions.
        :evolution_chain_id      : A unique id for each evolution family.
        :capture_rate            : Might not be needed.
        :base_happiness          : The default happiness level of a newly-met
                                   Pokémon. Needed for some evolution
                                   determinations.
        :growth_rate_id          : Determines the experience-gaining speed,
                                   hence the growth rate.
        :name                    : An alias for property `identifier`.
        :gender                  : WIP. ``{1: 'male', 2: 'female',
                                           3: 'genderless'}``.
        :happiness               : The current level of happiness.
        :types                   : A `list` of type_id (`int`) of all the
                                   types of the Pokémon.
        :base                    : A `pandas` `Series` with all 6 base stats.
                                   Can directly call each stat by using
                                   `Pokemon(x).base.{:stat_name:}`.
        :iv                      : A `pandas` Series` with randomly generated
                                   individual values for all stats. Can
                                   directly call each stat by using
                                   `Pokemon(x).iv.{:stat_name:}`.
        :effort                  : The effort value will be GAINED upon
                                   defeating such a Pokémon.

    """

    STAT_NAMES = ['hp', 'attack', 'defence',
                  'specialAttack', 'specialDefence', 'speed']

    CURRENT_STAT_NAMES = ['hp', 'attack', 'defence', 'specialAttack',
                          'specialDefence', 'speed', 'accuracy', 'evasion']

    def __init__(self, which_pokemon, level=50):

        try:
            if str(which_pokemon).isnumeric():
                # If `which_pokemon` is a number between 1 and 802
                __condition = tb.pokemon['id'] == which_pokemon

            elif type(which_pokemon) is str:
                # Else if `which_pokemon` is a valid Pokémon name
                __condition = tb.pokemon['identifier'] == which_pokemon

            # Set the id depending on the case.
            pokemon_id = int(tb.pokemon[__condition].id)

        except TypeError:
            raise TypeError("`pokemon` has to be an integer"
                            " or a pokemon's name.")

        # Set the label corresponds to the given id in the DataFrame.
        LABEL = list(tb.pokemon[tb.pokemon["id"] == pokemon_id].index)[0]

        # ------------ Initialization from `pokemon.csv` ------------- #

        self.id = tb.pokemon.loc[LABEL, "id"]
        self.identifier = tb.pokemon.loc[LABEL, "identifier"]
        self.species_id = tb.pokemon.loc[LABEL, "species_id"]
        self.height = tb.pokemon.loc[LABEL, "height"]
        self.weight = tb.pokemon.loc[LABEL, "weight"]
        self.base_experience = tb.pokemon.loc[LABEL, "base_experience"]
        self.order = tb.pokemon.loc[LABEL, "order"]
        self.is_default = tb.pokemon.loc[LABEL, "is_default"]

        # -------- Initialization from `pokemon_species.csv` --------- #

        p_species = tb.pokemon_species

        self.generation_id = p_species.loc[LABEL, "generation_id"]
        self.evolves_from = p_species.loc[LABEL, "evolves_from_species_id"]
        self.evolution_chain_id = p_species.loc[LABEL, "evolution_chain_id"]
        self.color_id = p_species.loc[LABEL, "color_id"]
        self.shape_id = p_species.loc[LABEL, "shape_id"]
        self.gender_rate = p_species.loc[LABEL, "gender_rate"]
        self.capture_rate = p_species.loc[LABEL, "capture_rate"]
        self.base_happiness = p_species.loc[LABEL, "base_happiness"]
        self.is_baby = p_species.loc[LABEL, "is_baby"]
        self.gender_differences = p_species.loc[LABEL, "has_"
                                                "gender_differences"]
        self.growth_rate_id = p_species.loc[LABEL, "growth_rate_id"]
        self.forms_switchable = p_species.loc[LABEL, "forms_switchable"]

        self.name = self.identifier

        # If `self.gender_rate` is -1, then `self` is genderless (3).
        # `self.gender_rate` divided by 8 is the probability of `self`
        # being a female.
        if self.gender_rate == -1:
            self.gender = 3
        elif not np.random.binomial(1, self.gender_rate/8):
            self.gender = 2
        else:
            self.gender = 1

        # Used in some damage calculations.
        self.happiness = self.base_happiness

        # Set the types of the Pokémon
        __condition = tb.pokemon_types["pokemon_id"] == self.id
        self.types = list(tb.pokemon_types[__condition]["type_id"])

        # Checks if `level` is valid.
        try:
            self.level = level

        except TypeError:
            raise TypeError("`level` has to be an integer"
                            " or an integer string.")

        if self.level not in range(1, 101):
            raise ValueError("Level should be in range(1,101).")

        # Set the current experience given its level and growth rate.
        # Not needed in battle, so I might remove this.
        __condition = ((tb.experience["growth_rate_id"] ==
                        self.growth_rate_id)
                       & (tb.experience["level"] == self.level))
        self.exp = tb.experience[__condition]["experience"]

        # ----------- BASE STAT, IV, & EV Initialization ------------- #

        # Set the Pokémon's base stats.
        __condition = tb.pokemon_stats["pokemon_id"] == self.id
        __pokemon_base_stat = tb.pokemon_stats[__condition]["base_stat"].values
        self.base = pd.Series(data=__pokemon_base_stat,
                              index=self.STAT_NAMES)

        # Pokémon's individual values are randomly generated.
        # Each value is uniformly distributed between 1 and 31.
        self.iv = pd.Series(data=[np.random.randint(1, 31) for i in range(6)],
                            index=self.STAT_NAMES)

        # Set the Pokémon's base effort value.
        # This is the amount the opponent would get upon defeating this
        # Pokémon.
        # Not needed in battle, but some holding items affect it.
        # TODO: Either remove these codes or modify the held-items
        # calculations.
        __cond = tb.pokemon_stats["pokemon_id"] == self.id
        self.effort = pd.Series(data=list(tb.pokemon_stats[__cond]["effort"]),
                                index=self.STAT_NAMES)

        # Set the actual EV the Pokémon has. Defaults to 0.
        # Needed for stats calculation.
        self.ev = pd.Series(data=[0. for x in range(6)],
                            index=self.STAT_NAMES)

        # ------------------ NATURE Initialization ------------------- #

        # Randomly assign a nature to the Pokémon.
        self.nature_id = np.random.randint(1, 25)

        # Set the relevant info with respect to the Pokémon's nature.
        # TODO: flavors are not needed in a battle, so I might remove
        # them in the future.
        __id = self.nature_id
        self.nature = pd.Series(index=["id", "name",
                                       "likes_flavor_id", "hates_flavor_id"],
                                data=[self.nature_id,
                                      tb.natures.loc[__id, "identifier"],
                                      tb.natures.loc[__id, "likes_flavor_id"],
                                      tb.natures.loc[__id, "hates_flavor_id"]])

        self.nature.name = self.nature.iloc[1]

        # The nature affects one's stats. The nature usually raises one
        # stat by 1.1 and lowers another by 0.9.
        __decreased_stat = np.array([1. for x in range(6)])
        __increased_stat = np.array([1. for x in range(6)])

        for x in range(1, 7):

            if x == tb.natures.loc[self.nature_id, "decreased_stat_id"]:
                __decreased_stat[x-1] = 0.9

            if x == tb.natures.loc[self.nature_id, "increased_stat_id"]:
                __increased_stat[x-1] = 1.1

        __nature_modifier = __increased_stat * __decreased_stat
        self.nature_modifier = pd.Series(data=__nature_modifier,
                                         index=self.STAT_NAMES)

        # ------------------ STATS Initialization -------------------- #

        # Stats determination.
        # `__inner` is common for both HP and other stats calculations.

        __inner = ((2. * self.base + self.iv + np.floor(self.ev/4.))
                   * self.level)/100.

        # For all the stats other than HP:
        self.stats = np.floor((np.floor(__inner) + 5.) * self.nature_modifier)

        # For HP:
        self.stats.hp = np.floor(__inner.hp) + self.level + 10.

        # Shedinja
        if self.name == 'shedinja':
            self.stats.hp = 1.

        self.stats = self.stats.reindex(self.STAT_NAMES)

        # ------------------ ABILITY Initialization ------------------ #

        __cond = ((tb.pokemon_abilities["pokemon_id"] == self.id) &
                  (tb.pokemon_abilities["is_hidden"] == 0))
        __sample_space = tb.pokemon_abilities[__cond]["ability_id"]
        self.ability = np.random.choice(__sample_space)

        # ------- IN-BATTLE STATS and CONDITION Initialization --------#

        self.current = pd.Series(index=self.CURRENT_STAT_NAMES,
                                 data=list(self.stats) + [100., 100.])

        self.stage = pd.Series(index=self.CURRENT_STAT_NAMES + ['critical'],
                               data=[0 for x in range(9)])

        self.status = Status(0)

        self.held_item = 0

        self.critical_stage_changed = 0

        self._moves = deque()

        # -------------------------- END ----------------------------- #

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    @property
    def moves(self):
        ___condition = ((tb.pokemon_moves["pokemon_id"] == self.id) &
                        (tb.pokemon_moves["pokemon_move_method_id"] == 1) &
                        (tb.pokemon_moves.level < self.level + 1))

        __all_moves = tb.pokemon_moves[___condition]["move_id"]

        # FIXME: this is resetting self._moves every time the moves
        # property is called.
        self._moves = deque([Move(x) for x in __all_moves.values[-4:]])

        return self._moves

    @moves.setter
    def moves(self, move):
        self._moves[0] = move
        self._moves.rotate()

    def reset_current(self):
        """The current stats should be reset after each battle,
        after changes made by leveling-up.
        """
        self.current = pd.Series(index=self.CURRENT_STAT_NAMES,
                                 data=list(self.stats) + [100., 100.])

        self.stage = pd.Series(index=self.CURRENT_STAT_NAMES + ['critical'],
                               data=[0 for x in range(9)])

        self.status.volatile = deque()

    def ismobile(self):
        pass

