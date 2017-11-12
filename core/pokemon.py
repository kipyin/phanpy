#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 15:56:47 2017

@author: Kip
"""
from collections import deque, defaultdict

from pandas import Series
import numpy as np

from mechanisms.core.item import Item
from mechanisms.core.move import Move
from mechanisms.core.status import Status
from mechanisms.data import tables as tb


# XXX: finish the doc string
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
        defense           105.0
        specialAttack     165.0
        specialDefense    110.0
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

    STAT_NAMES = ['hp', 'attack', 'defense',
                  'specialAttack', 'specialDefense', 'speed']

    CURRENT_STAT_NAMES = ['hp', 'attack', 'defense', 'specialAttack',
                          'specialDefense', 'speed', 'accuracy', 'evasion',
                          'critical']

    def __init__(self, which_pokemon, level=50):

        if which_pokemon in list(tb.pokemon.id.values):
            # If `which_pokemon` is a valid id.
            __condition = tb.pokemon['id'] == which_pokemon

        elif which_pokemon in tb.pokemon.identifier.values:
            # Else if `which_pokemon` is a valid Pokémon name
            __condition = tb.pokemon['identifier'] == which_pokemon

        else:
            raise KeyError("`pokemon` has to be an integer"
                           " or a pokemon's name.")

        # Get a subset of ``tb.pokemon`` based on the condition.
        # Get the pokemon id from the subset.
        pokemon = tb.pokemon[__condition]
        pokemon_id = pokemon['id']

        # ------------ Initialization from `pokemon.csv` ------------- #

        self.id = pokemon["id"].values[0]
        self.identifier = pokemon["identifier"].values[0]
        self.weight = pokemon['weight'].values[0]
        self.species_id = pokemon['species_id'].values[0]
        # -------- Initialization from `pokemon_species.csv` --------- #

        __condition = tb.pokemon_species['id'] == self.species_id
        p_species = tb.pokemon_species[__condition]

        self.generation_id = p_species["generation_id"].values[0]
        self.gender_rate = p_species["gender_rate"].values[0]
        self.base_happiness = p_species["base_happiness"].values[0]
        self.gender_differences = p_species["has_gender_differences"].values[0]
        self.forms_switchable = p_species["forms_switchable"].values[0]

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
        if level in np.arange(1, 101):
            self.level = level

        else:
            raise TypeError("`level` has to be an integer"
                            " or an integer string.")

        # ----------- BASE STAT, IV, & EV Initialization ------------- #

        # Set the Pokémon's base stats.
        __condition = tb.pokemon_stats["pokemon_id"] == self.id
        __pokemon_base_stat = tb.pokemon_stats[__condition]["base_stat"].values
        self.base = Series(data=__pokemon_base_stat,
                           index=self.STAT_NAMES)

        # Pokémon's individual values are randomly generated.
        # Each value is uniformly distributed between 1 and 31.
        self.iv = Series(
                    data=[np.random.randint(1, 32) for i in range(6)],
                    index=self.STAT_NAMES
                        )

        # Set the actual EV the Pokémon has.
        # Needed for stats calculation.
        # Insert marks to 5 randomly selected positions.
        __marks = np.append([np.random.uniform(0, 1) for x in range(5)], 1.)

        # Add endpoints.
        __marks = np.append(0., __marks)

        # Multiply __marks by 510, we get the cumulative EV of a pokemon.
        __cumulative_ev = np.floor(np.sort(__marks) * 510.)

        # Calculate the difference between consecutive elements
        __ev = np.ediff1d(__cumulative_ev)

        self.ev = Series(data=__ev, index=self.STAT_NAMES)

        # ------------------ NATURE Initialization ------------------- #

        # Randomly assign a nature to the Pokémon.
        __id = np.random.randint(1, 25)
        __nature_subset = tb.natures[tb.natures['id'] == __id]

        # Set the relevant info with respect to the Pokémon's nature.
        self.nature = Series(index=["id", "name"],
                             data=[__id,
                                   __nature_subset["identifier"].values[0]])

        # The nature affects one's stats. The nature usually raises one
        # stat by 1.1 and lowers another by 0.9.
        __decreased_stat = np.array([0. for x in range(6)])
        __increased_stat = np.array([0. for x in range(6)])


        for x in range(1, 7):

            if x == __nature_subset["decreased_stat_id"].values[0]:
                __decreased_stat[x-1] -= 0.1

            if x == __nature_subset["increased_stat_id"].values[0]:
                __increased_stat[x-1] += 0.1

        __nature_modifier = (__increased_stat + __decreased_stat) + 1.
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

        self.stage = Series(index=self.CURRENT_STAT_NAMES,
                            data=np.zeros(len(self.CURRENT_STAT_NAMES)))

        # Set the Pokémon's status. Detaults to None.
        self.status = Status(0)

        # Records the received damages. Has a memory of 5 turns.
        # If its length is over 5, delete the oldest damage.
        # Always use `appendleft()` to append a new damage.
        __received_damage = deque([], maxlen=5)

        self.history = Series(data=np.array([__received_damage, 0]),
                              index=["damage", "stage"])

        # ------------------ Moves Initialization -------------------- #

        # A Pokemon defaults to learn the last 4 learnable moves at its
        # current level.
        ___condition = ((tb.pokemon_moves["pokemon_id"] == self.id) &
                        (tb.pokemon_moves["pokemon_move_method_id"] == 1) &
                        (tb.pokemon_moves.level < self.level + 1))

        __all_moves = tb.pokemon_moves[___condition]["move_id"]

        num_of_moves = np.clip(a=4,
                               a_max=len(__all_moves),
                               a_min=1)

        _default_moves = ([Move(x) for x in
                          np.random.choice(__all_moves.values,
                                           size=num_of_moves,
                                           replace=False)])

        self.moves = _default_moves

        # --------------------- Miscellaneous ------------------------ #

        # Any miscellaneous flag and its duration a Pokémon might have,
        # such as {'stockpile': 1.}, where the meaning of the value(s)
        # depends on the flag.
        # XXX Change the flags' type to ``namedtuple``?
        self.flags = defaultdict()

        # Should items have their own class? Probably not?
        self.item = Item(0)

        if self.item.id in [303, 209]:

            self.stage.critical = 1

        elif ((self.id == 83 and self.item.id == 236) or
              (self.id == 113 and self.item.id == 233)):

            self.stage.critical = 2

        self.trainer = None

        # 1 if this pokemon moves first, 2 if it moves second, and so on.
        # 0 if this pokemon is not in a battle.

        self.order = 0

        # -------------------------- END ----------------------------- #

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        """Assert equal between two pokemons.
        If they have the same individual values and they have the
        same name, then they are considered to be the same pokemon.
        """
        if (self.iv.values == other.iv.values).all():
            return True
        else:
            return False

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

    def set_nature(self, which_nature):
        """Set the nature given its id or name."""
        if str(which_nature) in tb.natures.identifier.values:
            # If given the nature's name
            __name = which_nature
            __id = tb.natures[tb.natures['identifier'] == __name]['id'].values[0]

        elif which_nature in tb.natures.id.values:
            # If given the nature's id
            __id = which_nature
            __name = tb.natures[tb.natures['id'] == __id]['identifier'].values[0]

        else:
            raise KeyError("{} is not a valid nature reference."
                           "".format(which_nature))

        __nature_subset = tb.natures[tb.natures['id'] == __id]

        self.nature = Series(index=["id", "name"],
                             data=[__id, __name])

        # The nature affects one's stats. The nature usually raises one
        # stat by 1.1 and lowers another by 0.9.
        __decreased_stat = np.array([0. for x in range(6)])
        __increased_stat = np.array([0. for x in range(6)])

        for x in range(1, 7):

            if x == __nature_subset["decreased_stat_id"].values[0]:
                __decreased_stat[x-1] -= 0.1

            if x == __nature_subset["increased_stat_id"].values[0]:
                __increased_stat[x-1] += 0.1

        __nature_modifier = (__increased_stat + __decreased_stat) + 1.
        self.nature_modifier = Series(data=__nature_modifier,
                                      index=self.STAT_NAMES)

    @property
    def stage_factor(self):
        """These are the numbers that the current stats get multiplied
        by based on the stages.
        In some sense,
        self.current.values = (self.stats.values
                               * self.stage_facotr.values)
        except for 'hp', as hp's damage is a dummy var.
        """
        stage_to_factor = {
                       -6: 2./8., 6: 8./2.,
                       -5: 2./7., 5: 7./2.,
                       -4: 2./6., 4: 6./2.,
                       -3: 2./5., 3: 5./2.,
                       -2: 2./4., 2: 4./2.,
                       -1: 2./3., 1: 3./2.,
                       0: 1.
                           }

        factors = np.ones(len(self.CURRENT_STAT_NAMES))
        for i, stage in enumerate(self.stage):
            factors[i] *= stage_to_factor[stage]

        return Series(index=self.CURRENT_STAT_NAMES, data=factors)

    @property
    def current(self):
        """Calcuate the in-battle stats based on the pokemon's
        calcualted stats and its stage factors.
        """
        # Set the baseline
        current = deque(self.stats.values)
        current.extend([100., 100., 100.])
        current = np.array(current)
        current *= self.stage_factor.values
        return Series(index=self.CURRENT_STAT_NAMES, data=current)


class Trainer():
    """Some awesome introductions.
    """

    def __init__(self, name=None, num_of_pokemon=3):

        self.id = np.random.randint(0, 65535)

        if name:
            self.name = name
        else:
            self.name = str(self.id)

        __party = [Pokemon(x) for x in np.random.choice(a=np.arange(1, 494),
                                                        size=num_of_pokemon)]

        for pokemon in __party:
            pokemon.trainer = self

        self._party = __party

        self.__counter = 0  # a counter for `__next__`

    def __iter__(self):

        return self

    def __next__(self):
        """Iterating a Trainer object is the same as iterating through
        the Pokemon objects in its party.

        >>> satoshi = Trainer('Satoshi')
        >>> for pokemon in satoshi:
        ...    # do something

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

        self._party[slot-1] = pokemon
        self._party[slot-1].trainer = self

        print("{} is added to slot {}.".format(pokemon.name, slot))


def test():
#    a = Trainer()
#    b = Trainer()
    p1 = Pokemon(123)
    p2 = Pokemon(246)
    p1.status += Status(4)
    # print(set(p1.status))

    print(sum(p1.ev), p2.ev)
#    p1 = a.party(2)
#    p2 = b.party(2)
    m1 = p1.moves[1]
    m2 = p2.moves[1]

    print(p1.moves)
    # attack(p1, m1, p2, m2)
#    a.set_pokemon(1, ad)
#    b.set_pokemon(1, Pokemon(123))
#    print(a.party(1) == b.party(1))
#    print(a, b)
#    print(s.trainer, ad.trainer)


# test()
