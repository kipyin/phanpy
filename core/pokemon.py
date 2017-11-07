#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 15:56:47 2017

@author: Kip
"""
from collections import deque, defaultdict

from pandas import Series, DataFrame
import numpy as np

from mechanisms.core.item import Item
from mechanisms.core.move import Move
from mechanisms.core.status import Status
from mechanisms.data import tables as tb


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

    """

    STAT_NAMES = ['hp', 'attack', 'defence',
                  'specialAttack', 'specialDefence', 'speed']

    CURRENT_STAT_NAMES = ['hp', 'attack', 'defence', 'specialAttack',
                          'specialDefence', 'speed', 'accuracy', 'evasion']

    def __init__(self, which_pokemon, level=50):
        # XXX: the try-except clause does nothing..?

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

        # -------- Initialization from `pokemon_species.csv` --------- #

        p_species = tb.pokemon_species

        self.generation_id = p_species.loc[LABEL, "generation_id"]
        self.gender_rate = p_species.loc[LABEL, "gender_rate"]
        self.base_happiness = p_species.loc[LABEL, "base_happiness"]
        self.gender_differences = p_species.loc[LABEL, "has_"
                                                "gender_differences"]
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

        # ----------- BASE STAT, IV, & EV Initialization ------------- #

        # Set the Pokémon's base stats.
        __condition = tb.pokemon_stats["pokemon_id"] == self.id
        __pokemon_base_stat = tb.pokemon_stats[__condition]["base_stat"].values
        self.base = Series(data=__pokemon_base_stat,
                           index=self.STAT_NAMES)

        # Pokémon's individual values are randomly generated.
        # Each value is uniformly distributed between 1 and 31.
        self.iv = Series(
                    data=[np.random.random_integers(1, 32) for i in range(6)],
                    index=self.STAT_NAMES
                        )

        # Set the actual EV the Pokémon has. Defaults to 0.
        # Needed for stats calculation.
        self.ev = Series(data=[0. for x in range(6)],
                         index=self.STAT_NAMES)

        # ------------------ NATURE Initialization ------------------- #

        # Randomly assign a nature to the Pokémon.
        self.nature_id = np.random.randint(1, 25)

        # Set the relevant info with respect to the Pokémon's nature.
        # TODO: flavors are not needed in a battle, so I might remove
        # them in the future.
        __id = self.nature_id
        self.nature = Series(index=["id", "name",
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
        self.nature_modifier = Series(data=__nature_modifier,
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

        # Shedinja always has at most 1 HP.
        if self.name == 'shedinja':
            self.stats.hp = 1.

        # Reindex the stats dataframe to conform with the indices on
        # the table.
        self.stats = self.stats.reindex(self.STAT_NAMES)

        # ------------------ ABILITY Initialization ------------------ #

        # TODO: hidden abilities?
        # TODO: possibilities for multiple abilities?
        # Set the Pokémon's abilities.
        __cond = ((tb.pokemon_abilities["pokemon_id"] == self.id) &
                  (tb.pokemon_abilities["is_hidden"] == 0))
        __sample_space = tb.pokemon_abilities[__cond]["ability_id"]
        self.ability = np.random.choice(__sample_space)

        # ------- IN-BATTLE STATS and CONDITION Initialization --------#

        # Set the in-battle only stats.
        # Each stat has a stage and a value. We can calculate the values
        # based on the stages every round.
        self.current = Series(index=self.CURRENT_STAT_NAMES,
                              data=list(self.stats) + [100., 100.])

        __stage_stat_name = self.CURRENT_STAT_NAMES + ['critical']
        self.stage = Series(index=__stage_stat_name,
                            data=[0 for x in range(9)])

        # These are the numbers that the current stats get multiplied
        # by based on the stages.
        # In some sense,
        # self.current = self.stats.values * self.stage_facotr.values
        # except for 'critical' and 'hp', as 'hp's damage is a dummy
        # var.
        self.stage_factor = Series(index=__stage_stat_name,
                                   data=[1 for x in range(9)])

        # Set the Pokémon's status. Detaults to None.
        self.status = Status(0)

        # ------------------ Moves Initialization -------------------- #

        # A Pokemon defaults to learn the last 4 learnable moves at its
        # current level.
        ___condition = ((tb.pokemon_moves["pokemon_id"] == self.id) &
                        (tb.pokemon_moves["pokemon_move_method_id"] == 1) &
                        (tb.pokemon_moves.level < self.level + 1))

        __all_moves = tb.pokemon_moves[___condition]["move_id"]
        _default_moves = deque([Move(x) for x in __all_moves.values[-4:]])

        self.moves = _default_moves

        # --------------------- Miscellaneous ------------------------ #

        # Any miscellaneous flags a Pokémon might have, such as
        # 'critical-rate-changed'.
        self.flags = defaultdict()

        # Should items have their own class? Probably not?
        self.item = Item(0)

        self.trainer_id = np.random.randint(0, 65535)

        # 1 if this pokemon moves first, 2 if it moves second, and so on.
        # 0 if this pokemon is not in a battle.

        self.order = 0

        # -------------------------- END ----------------------------- #

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def reset_current(self):
        """The current stats should be reset after each battle,
        after changes made by leveling-up.
        """
        # Reset the in-battle stats after switching out | after a battle.
        self.current = Series(index=self.CURRENT_STAT_NAMES,
                              data=list(self.stats) + [100., 100.])

        self.stage = Series(index=self.__stage_stat_name,
                            data=[0 for x in range(9)])

        # self.status = Status(0)


class Trainer():
    """Some awesome introductions.
    """
    global turn

    def __init__(self, name=None, num_of_pokemon=3):

        self.id = np.random.randint(0, 65535)

        if name:
            self.name = name
        else:
            self.name = str(self.id)

        __party = [Pokemon(x) for x in np.random.choice(a=np.arange(1, 494),
                                                        size=num_of_pokemon)]

        for pokemon in __party:
            pokemon.trainer_id = self.id

        self._party = __party

        event_names = [
                       'order',
                       'move_id', 'item_id', 'switch_to_id',
                       'damage_to_opponent', 'damage_to_self',
                       'status_to_opponent', 'status_to_self',
                       'attack_to_opponent', 'attack_to_self',
                       'defence_to_opponent', 'defence_to_self',
                       'specialAttack_to_opponent', 'specialAttack_to_self',
                       'specialDefence_to_opponent', 'specialDefence_to_self',
                       'speed_to_opponent', 'speed_to_self',
                       'accuracy_to_opponent', 'accuracy_to_self',
                       'evasion_to_opponent', 'evasion_to_self',
                       'critical_to_opponent', 'critical_to_self'
                       ]

        # The _events property is predefined to have 100 rows. This is
        # a bit faster than adding rows on the fly.
        self._events = DataFrame(index=np.arange(1, 101),
                                 columns=event_names,
                                 data=np.zeros((100, len(event_names))))

        self.__counter = 0  # a counter for `__next__`

    def __iter__(self):

        return self

    def __next__(self):
        """Iterating a Trainer object is the same as iterating through
        the Pokemon objects in its party.
        """

        if self.__counter >= len(self._party):
            raise StopIteration

        else:
            self.__counter += 1
            return self._party[self.__counter-1]

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def party(self, slot=None):
        """
        Gets the Pokemone names in the party if no slot is selected.
        Returns the Pokemon specified by `slot` if one has been chosen.
        """

        if slot:
            return self._party[slot-1]
        else:
            return self._party

    def set_pokemon(self, slot, pokemon):

        pokemon.trainer_id = self.id
        self._party[slot-1] = pokemon

        print("{} is added to slot {}.".format(pokemon.name, slot))

    def events(self, event_name=None, value=None):

        if event_name and value:
            self._events.loc[turn, event_name] = value
        else:
            return self._events
