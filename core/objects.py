#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import sys, path
sys.path.append(path.abspath('.'))

from collections import deque, defaultdict
from copy import deepcopy
from functools import reduce

import numpy as np
from pandas import Series, DataFrame
import phanpy.core.tables as tb


class Status():
    """A class containing all current statuses of a Pokémon.
    Status conditions, also referred to as status problems or status
    ailments, affect a Pokémon's ability to battle. There are three
    kinds of status. The first are non-volatile, the second are
    volatile, and the third lasts while a Pokémon is in battle. For our
    purposes, there is no point to make distinctions to the last two,
    so we combine them and call them 'volatile'.

    The csv files call it an 'ailment'.

    A ``non-volatile`` status is one of the following: paralysis, sleep,
    freeze, burn, poison, badly-poisoned, and normal. Non-volatile
    statuses cannot stack; one Pokémon can only have one non-volatile
    status each time.

    A ``volatile`` status is the one that does not exist out side of a
    battle. Some classic examples would be confusion, ingrain,
    infatuation, etc. One can have multiple volatile statuses.

    Note that one can declare any kind of status he/she wants.

    Parameters
    ----------
    status : int or str
        This parameter can be a valid status id or a valid status
        name defined in the csv tables. If no valid status is
        found in the tables, a custom status will be created, using
        the given parameter. In this case, a random id will be
        assigned to this status.

    duration : float, default to float('inf')
        The duration of the status. If none is given, it will be
        set to infinity.

    Usage
    -----
        >>> poison = Status(5)
        >>> leech_seed = Status(18, 5)
        >>> combined = poison + leech_seed
        >>> combined.duration
        array([ inf,   5.])

    Attributes
    ----------
    id : numpy.array, dtype='int64'
        The ``ailment_id`` in ``move_meta_ailments.csv``. If no
        match is found, then randomly generate a pseudo-id.

    name : numpy.array, dtype='<U24'
        The name of the status(es).

    volatile : numpy.array, dtype='bool'
        True for volatile statuses, and False for non-volatile
        statuses (id in 0~5).

    duration : numpy.array, dtype='float64'
        ``duration`` represents how long the status condition is
        going to last.

    Methods
    =======

    __add__(self, other)
        It is possible for a Pokemon to have multiple status
        conditions. This can be achieved by adding a new status
        condition to the existing status conditioin(s).
        Note that the right hand side of the plus sign should
        always be a none-compounded status.

    __len__(self)
        ``len(some_status)`` returns how many statuses are
        compounded.

    __iter__(self)
        Iterating a ``Status`` object is equivalent to
        iterating through the names.

    __contaions__(self)
        Checking 'something' is in a ``Status`` object
        is in effect checking if 'something' is in the list of the
        status names.

    __bool__(self)
        Return ``True`` if a Pokemon has some kind of status
        (other than normal).

    __eq__(self)
        If two statuses have the exact same set of names,
        then they are consideredt to be equal.

    remove(...)
        remove(which_status)

        Remove the given status from the existing status conditions.

    reduce(...)
        reduce()

        Reduce all durations by 1. If a status has a duration of 0,
        remove the status from the list.

    References
    ----------
        https://bulbapedia.bulbagarden.net/wiki/Status_condition
    """

    def __init__(self, status=None, duration=float('inf')):

        if status in list(tb.ailments.id.values):
            # If the input is a valid id, get the status name from the
            # table.
            cond = tb.ailments["id"] == status
            name = tb.ailments[cond]["identifier"].values[0]
            status_id = status

        elif status in tb.ailments.identifier.values:
            # Else if the input is a valid status name, get the id
            # from the table.
            cond = (tb.ailments["identifier"] == status)
            name = status
            status_id = tb.ailments[cond]["id"].values[0]

        else:
            # If the input is neither, then that means it is a custom-
            # defined Status. The status' name is the input, and the
            # id is set to be a random 6-digit number in order to
            # distinguish it from all the other status id's.
            name = str(status)
            status_id = np.random.randint(100000, 199999)

        # The status is of volatile type if its id is not in range(0,6).
        # Otherwise, it is a non-volatile type.
        volatile = status_id not in range(0, 6)

        self.id = np.array([status_id], dtype='int64')
        # The dtype '<U24' means that it is a little-endian unicode
        # with a length of 24. In other words, it supports a maximum
        # of 24-character name.
        #
        # For example, if I define a Status as follows:
        #
        # >>> my_status = Status('123456789012345678901234567890')
        #
        # i.e. it is defined to have a 30-char name, but dtype='<U24'
        # limits it to 24 chars. Therefore, if then we do
        #
        # >>> my_status += Status('freeze')
        # >>> my_status.name
        #
        # We will only get array(['freeze', '123456789012345678901234'],
        # dtype='<U24').
        # 24-char should be enought, as the longest statuses in game is
        # 'whipping-up-a-whirlwind' (23-chars).
        self.name = np.array([name], dtype='<U24')
        self.volatile = np.array([volatile], dtype='bool')
        self.duration = np.array([duration], dtype='float64')

        # A counter for __next__
        self.__current = 0

    def __repr__(self):
        return ', '.join(self.name)

    def __len__(self):
        return len(self.name)

    def __iter__(self):
        """Iterate through the statuses' names.

        Usage
        -----
            >>> for status in Pokemon(123).status
            ...     # do something

        """
        return self

    def __next__(self):

        if self.__current >= len(self.name):
            raise StopIteration

        else:
            self.__current += 1
            return list(self.name)[self.__current - 1]

    def __contains__(self, item):
        """
            >>> 'flinch' in Pokemon(123).status
            >>> 5 in Pokemon(123).status

        """
        if type(item) is str:
            return True if item in self.name else False

        elif str(item).isnumeric():
            return True if item in self.id else False

        else:
            return False

    def __add__(self, other):
        """Adds two statuses together.

        Append volatile statuses; replace non-volatile statuses.
        """
        new = Status(0)

        new.duration = deepcopy(self.duration)
        new.name = deepcopy(self.name)
        new.id = deepcopy(self.id)
        new.volatile = deepcopy(self.volatile)

        if self.volatile.all() or other.volatile.all():
            # As long as not both of them have a non-volatile status
            # at the same time...(double negative, sorry).
            new.duration = np.append(self.duration, other.duration)
            new.id = np.append(self.id, other.id)
            new.name = np.append(self.name, other.name)
            new.volatile = np.append(self.volatile, other.volatile)
        else:
            # If both of them have a non-volatile status at the same
            # time, replace `self`'s non-volatile status with that of
            # `other`'s.
            nvol_pos = np.where(~self.volatile)[0][0]

            new.duration[nvol_pos] = other.duration[0]
            new.id[nvol_pos] = other.id[0]
            new.name[nvol_pos] = other.name[0]
            new.volatile[nvol_pos] = other.volatile[0]

        return new

    def __bool__(self):
        """Returns True if 0 is not in the status id's.

        Usage
        -----
            >>> 'bad' if some_pokemon.status else 'good'

        """
        return True if 0 not in self.id and len(self.id) == 1 else False

    def __eq__(self, other):
        return set(self.name) == set(other.name)

    def __hash__(self):
        """Returns the names as a set."""
        return set(self.name)

    def remove(self, which_status):
        """Remove the given status. `which_status` can be a valid status
        id, or a valid status name. If no instances of `which_status` is
        found, removes nothing.

        """

        if which_status in list(self.name):
            # There should be at most 1 occurance.
            mask = self.name != which_status
        elif which_status in list(self.id):
            mask = self.id != which_status
        else:
            mask = self.name == self.name
            raise KeyError('Status({}) is not in the list. '
                           'Nothing is removed.'.format(which_status))

        self.id = self.id[mask]
        self.name = self.name[mask]
        self.duration = self.duration[mask]
        self.volatile = self.volatile[mask]
        # print(list(self.id) == np.ndarray(0, dtype='int64'))
        if list(self.id) == []:
            # If the only status gets removed, set it to normal.
            self.id = np.array([0])
            self.name = np.array(['normal'])
            self.duration = np.array([float('inf')])
            self.volatile = np.array([False])


    def reduce(self):
        """Subtract 1 from all durations."""
        self.duration -= 1
        if 0 in self.duration:
            mask = self.duration != 0
            self.name = self.name[mask]
            self.id = self.id[mask]
            self.volatile = self.volatile[mask]
            self.duration = self.duration[mask]


class Item():
    """A class for items.

    Parameters
    ----------
    which_item : int or str
        ``which_item`` can be a valid item id, or a valid item name,
        with dashes ('-') between words. It can also be set to 0,
        in which case it is equivalent to no item.

    Attributes
    ----------
    id : int
        A unique id for an item in the csv file. If a Pokemon is
        not holding any item, this will be 0.
    name : str
        The name of the item.
    """

    def __init__(self, which_item):

        if which_item == 0:
            id_ = 0
            name = 'no-item'
            # Define a subset regardless. It is needed for other
            # attributes.
            subset = tb.items[tb.items["id"] == which_item]

        elif which_item in list(tb.items.id.values):
            # If which_item is a valid item id, get its name from the
            # table.
            subset = tb.items[tb.items["id"] == which_item]
            name = subset["identifier"].values[0]
            id_ = which_item

        elif which_item in tb.items.identifier.values:
            # If which_item is a valid item namem, get the item id
            # from the table.
            subset = tb.items[tb.items["identifier"] == which_item]
            id_ = subset["id"].values[0]
            name = which_item

        else:
            raise KeyError("{} is not a valid item.".format(which_item))

        self.id = id_
        self.name = name

        category_id = subset["category_id"].values
        if list(category_id) == []:
            category_id = [23]
        self.category_id = category_id[0]

        fling_power = subset["fling_power"].values
        if list(fling_power) == []:
            fling_power = [0]
        elif np.isnan(fling_power[0]):
            fling_power = [0]

        fling_effect_id = subset["fling_effect_id"].values  # Can be empty
        if list(fling_effect_id) == []:
            fling_effect_id = [0]
        elif np.isnan(fling_effect_id[0]):
            fling_effect_id = [0]

        fling_power = fling_power[0]
        fling_effect_id = fling_effect_id[0]

        condition = tb.item_fling_effects["id"] == fling_effect_id
        subset = tb.item_fling_effects[condition]
        fling_effect_name = subset["identifier"].values
        if list(fling_effect_name) == []:
            fling_effect_name = 'no-effect'

        self.fling = Series(index=["effect_id", "effect_name", "power"],
                            data=[fling_effect_id, fling_effect_name,
                                  fling_power])

        subset = tb.item_flag_map[tb.item_flag_map["item_id"] == self.id]
        flag_id = DataFrame({"id": subset.item_flag_id})
        self.flags = tb.item_flags.merge(flag_id, how="inner", on="id")
        self.flags.columns = ["id", "name"]


    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def flingat(self, other):
        """"Fling the item to the opponent.

        Activate the item's effect.
        """

        fling_id = self.fling.effect_id

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

        elif fling_id == 7:
            # XXX: flinch if the opponent has not gone this turn.
            pass

        else:
            pass


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
                move_id = int(tb.moves[tb.moves["identifier"] == which_move].id)

            elif str(which_move).isnumeric():
                move_id = which_move

        except TypeError:
            raise TypeError("Move(x) where x is either a move_id"
                            " or a move_name")

        condition1 = tb.moves['id'] == move_id
        condition2 = tb.move_meta['move_id'] == move_id
        moves_subset = tb.moves[condition1]
        moves_meta_subset = tb.move_meta[condition2]

        self.id = moves_subset["id"].values[0]
        self.identifier = moves_subset["identifier"].values[0]
        self.generation_id = moves_subset["generation_id"].values[0]
        self.type = moves_subset["type_id"].values[0]
        self.power = moves_subset["power"].values[0]
        self.pp = moves_subset["pp"].values[0]
        self.accuracy = moves_subset["accuracy"].values[0]
        self.priority = moves_subset["priority"].values[0]
        self.target_id = moves_subset["target_id"].values[0]
        self.damage_class_id = moves_subset["damage_class_id"].values[0]
        self.effect_id = moves_subset["effect_id"].values[0]
        self.effect_chance = moves_subset["effect_chance"].values[0]

        self.meta_category_id = moves_meta_subset["meta_category_id"].values[0]
        self.meta_ailment_id = moves_meta_subset["meta_ailment_id"].values[0]
        self.min_hits = moves_meta_subset["min_hits"].values[0]
        self.max_hits = moves_meta_subset["max_hits"].values[0]
        self.min_turns = moves_meta_subset["min_turns"].values[0]
        self.max_turns = moves_meta_subset["max_turns"].values[0]
        self.drain = moves_meta_subset["drain"].values[0]
        self.healing = moves_meta_subset["healing"].values[0]
        self.crit_rate = moves_meta_subset["crit_rate"].values[0]
        self.ailment_chance = moves_meta_subset["ailment_chance"].values[0]
        self.flinch_chance = moves_meta_subset["flinch_chance"].values[0]
        self.stat_chance = moves_meta_subset["stat_chance"].values[0]

        condition = tb.move_flag_map["move_id"] == self.id
        self.flag = tb.move_flag_map[condition]

        if move_id in tb.move_meta_stat_changes.move_id.values:

            condition = tb.move_meta_stat_changes["move_id"] == self.id
            self.stat_change = tb.move_meta_stat_changes[condition]
        else:
            self.stat_change = 0

        self.name = self.identifier

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


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
            condition = tb.pokemon['id'] == which_pokemon

        elif which_pokemon in tb.pokemon.identifier.values:
            # Else if `which_pokemon` is a valid Pokémon name
            condition = tb.pokemon['identifier'] == which_pokemon

        else:
            raise KeyError("`pokemon` has to be an integer"
                           " or a pokemon's name.")

        # Get a subset of ``pokemon`` based on the condition.
        # Get the pokemon id from the subset.
        pokemon = tb.pokemon[condition]
        pokemon_id = pokemon['id']

        # ------------ Initialization from `pokemon.csv` ------------- #

        self.id = pokemon["id"].values[0]
        self.identifier = pokemon["identifier"].values[0]
        self.weight = pokemon['weight'].values[0]
        self.species_id = pokemon['species_id'].values[0]
        # -------- Initialization from `pokemon_species.csv` --------- #

        condition = tb.pokemon_species['id'] == self.species_id
        p_species = tb.pokemon_species[condition]

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
        condition = tb.pokemon_types["pokemon_id"] == self.id
        self.types = list(tb.pokemon_types[condition]["type_id"])

        # Checks if `level` is valid.
        if level in np.arange(1, 101):
            self.level = level

        else:
            raise TypeError("`level` has to be an integer"
                            " or an integer string.")

        # ----------- BASE STAT, IV, & EV Initialization ------------- #

        # Set the Pokémon's base stats.
        condition = tb.pokemon_stats["pokemon_id"] == self.id
        pokemon_base_stat = tb.pokemon_stats[condition]["base_stat"].values
        self.base = Series(data=pokemon_base_stat,
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
        marks = np.append([np.random.uniform(0, 1) for x in range(5)], 1.)

        # Add endpoints.
        marks = np.append(0., marks)

        # Multiply marks by 510, we get the cumulative EV of a pokemon.
        cumulative_ev = np.floor(np.sort(marks) * 510.)

        # Calculate the difference between consecutive elements
        __ev = np.ediff1d(cumulative_ev)

        self.ev = Series(data=__ev, index=self.STAT_NAMES)

        # ------------------ NATURE Initialization ------------------- #

        # Randomly assign a nature to the Pokémon.
        id_ = np.random.randint(1, 25)
        nature_subset = tb.natures[tb.natures['id'] == id_]

        # Set the relevant info with respect to the Pokémon's nature.
        self.nature = Series(index=["id", "name"],
                             data=[id_,
                                   nature_subset["identifier"].values[0]])

        # The nature affects one's stats. The nature usually raises one
        # stat by 1.1 and lowers another by 0.9.
        decreased_stat = np.array([0. for x in range(6)])
        increased_stat = np.array([0. for x in range(6)])


        for x in range(1, 7):

            if x == nature_subset["decreased_stat_id"].values[0]:
                decreased_stat[x-1] -= 0.1

            if x == nature_subset["increased_stat_id"].values[0]:
                increased_stat[x-1] += 0.1

        nature_modifier = (increased_stat + decreased_stat) + 1.
        self.nature_modifier = Series(data=nature_modifier,
                                      index=self.STAT_NAMES)

        # ------------------ ABILITY Initialization ------------------ #

        # TODO: hidden abilities?
        # TODO: possibilities for multiple abilities?
        # Set the Pokémon's abilities.
        cond = ((tb.pokemon_abilities["pokemon_id"] == self.id) &
                (tb.pokemon_abilities["is_hidden"] == 0))
        sample_space = tb.pokemon_abilities[cond]["ability_id"]
        self.ability = np.random.choice(sample_space)

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
        received_damage = deque([], maxlen=5)

        self.history = Series(data=np.array([received_damage, 0]),
                              index=["damage", "stage"])

        # ------------------ Moves Initialization -------------------- #

        # A Pokemon defaults to learn the last 4 learnable moves at its
        # current level.
        condition = ((tb.pokemon_moves["pokemon_id"] == self.id) &
                     (tb.pokemon_moves.level < self.level + 1))

        self._all_moves = tb.pokemon_moves[condition]["move_id"].values

        num_of_moves = np.clip(a=4,
                               a_max=len(self._all_moves),
                               a_min=1)

        _default_moves = ([Move(x) for x in
                          np.random.choice(self._all_moves,
                                           size=num_of_moves,
                                           replace=False)])

        self.moves = _default_moves

        # --------------------- Miscellaneous ------------------------ #

        # Any miscellaneous flag and its duration a Pokémon might have,
        # such as {'stockpile': 1.}, where the meaning of the value(s)
        # depends on the flag.
        self.flags = defaultdict()

        self._item = Item(0)

        self.trainer = None

        # 1 if this pokemon moves first, 2 if it moves second, and so on.
        # 0 if this pokemon is not in a battle.

        self.order = 0

        # Set a unique id for each Pokemon.
        self.unique_id = np.random.randint(100000, 999999)

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
        if ((self.iv.values == other.iv.values).all()
            and (self.unique_id == other.unique_id)):
            return True
        else:
            return False

    @property
    def stats(self):
        """Stats determination.

        `inner` is common for both HP and other stats calculations.
        """

        inner = (2. * self.base + self.iv + self.ev//4.) * self.level//100.

        # For all the stats other than HP:
        calculated_stats = np.floor(inner + 5.) * self.nature_modifier//1.

        # For HP:
        calculated_stats.hp = np.floor(inner.hp) + self.level + 10.

        # Shedinja always has at most 1 HP.
        if self.name == 'shedinja':
            calculated_stats.hp = 1.

        # Reindex the stats dataframe to conform with the indices on
        # the table.
        return calculated_stats.reindex(self.STAT_NAMES)

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
        return Series(index=self.CURRENT_STAT_NAMES,
                      data=np.floor(current))

    @property
    def item(self):
        return self._item

    @item.setter
    def item(self, item):
        if item.id in [303, 209]:
            self.stage.critical = 1

        elif ((self.id == 83 and item.id == 236) or
              (self.id == 113 and item.id == 233)):
            self.stage.critical = 2

        self._item = item

    def reset_current(self):
        """The current stats should be reset after each battle,
        after changes made by leveling-up.
        """
        # Reset the stage should automatically reset the current stats.
        self.stage = Series(index=self.CURRENT_STAT_NAMES,
                            data=np.zeros(len(self.CURRENT_STAT_NAMES)))

    def set_nature(self, which_nature):
        """Set the nature given its id or name."""
        if which_nature in list(tb.natures.identifier.values):
            # If given the nature's name
            name = which_nature
            id_ = tb.natures[tb.natures['identifier'] == name]['id'].values[0]

        elif which_nature in list(tb.natures.id.values):
            # If given the nature's id
            id_ = which_nature
            name = tb.natures[tb.natures['id'] == id_]['identifier'].values[0]

        else:
            raise KeyError("{} is not a valid nature reference."
                           "".format(which_nature))

        nature_subset = tb.natures[tb.natures['id'] == id_]

        self.nature = Series(index=["id", "name"],
                             data=[id_, name])

        # The nature affects one's stats. The nature usually raises one
        # stat by 1.1 and lowers another by 0.9.
        decreased_stat = np.array([0. for x in range(6)])
        increased_stat = np.array([0. for x in range(6)])

        for x in range(1, 7):

            if x == nature_subset["decreased_stat_id"].values[0]:
                decreased_stat[x-1] -= 0.1

            if x == nature_subset["increased_stat_id"].values[0]:
                increased_stat[x-1] += 0.1

        nature_modifier = (increased_stat + decreased_stat) + 1.
        self.nature_modifier = Series(data=nature_modifier,
                                      index=self.STAT_NAMES)

    def set_ev(self, iterable):
        """Assign ev's from the iterable.

        Note that this can even set illegal ev's.
        """
        if len(iterable) != 6:
            raise ValueError("The iterable must have a length of 6.")

        for i in range(6):
            self.ev[i] = iterable[i]

        return self.ev

    def set_iv(self, iterable):
        """Assign iv's from the iterable.

        Note that this can even set illegal iv's.
        """
        if len(iterable) != 6:
            raise ValueError("The iterable must have a length of 6.")

        for i in range(6):
            self.iv[i] = iterable[i]

        return self.iv


class Trainer():
    """Some awesome introductions.
    """

    def __init__(self, name=None, num_of_pokemon=3):

        self.id = np.random.randint(0, 65535)

        if name:
            self.name = name
        else:
            self.name = str(self.id)

        party = [Pokemon(x) for x in np.random.choice(a=np.arange(1, 494),
                                                      size=num_of_pokemon)]

        for pokemon in party:
            pokemon.trainer = self

        self._party = party

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
            return self._party[self.counter-1]

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def party(self, slot=None):
        """
        Get the Pokemone names in the party if no slot is selected.
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
