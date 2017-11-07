
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 17:01:58 2017

@author: Kip

Naming conventions (I'm trying my best to stick to it):

    variables : lower_with_underlines
    functions, Series, DataFrames : lowerCamelCase
    classes : UpperCamelCase
    class constants : UPPER_WITH_UNDERLINES

Use revesed naming as you can.
"""
from collections import deque
from functools import reduce

import pandas as pd
import numpy as np

# ------------------------------ Files Import ------------------------------- #

PATH = './csv/'

with open(PATH + 'experience.csv') as csv:

    experience = pd.read_csv(csv)

with open(PATH + 'moves.csv') as csv:

    moves = pd.read_csv(csv)

with open(PATH + 'natures.csv') as csv:

    natures = pd.read_csv(csv)

with open(PATH + 'pokemon_abilities.csv') as csv:

    pokemonAbilities = pd.read_csv(csv)

with open(PATH + 'pokemon_evolution.csv') as csv:

    pokemonEvolution = pd.read_csv(csv)

with open(PATH + 'move_meta.csv') as csv:

    moveMeta = pd.read_csv(csv)

with open(PATH + 'move_meta_ailments.csv') as csv:

    moveMetaAilments = pd.read_csv(csv)

with open(PATH + 'move_meta_stat_changes.csv') as csv:

    moveMetaStatChanges = pd.read_csv(csv)

with open(PATH + 'pokemon_moves.csv') as csv:

    pokemonMoves = pd.read_csv(csv)

with open(PATH + 'pokemon_species.csv') as csv:

    pokemonSpecies = pd.read_csv(csv)

with open(PATH + 'pokemon_stats.csv') as csv:

    pokemonStats = pd.read_csv(csv)

with open(PATH + 'pokemon_types.csv') as csv:

    pokemonTypes = pd.read_csv(csv)

with open(PATH + 'pokemon.csv') as csv:

    pokemon = pd.read_csv(csv)

with open(PATH + 'types.csv') as csv:

    types = pd.read_csv(csv)

with open(PATH + 'type_efficacy.csv') as csv:

    typeEfficacy = pd.read_csv(csv)

with open(PATH + 'version_group_regions.csv') as csv:

    versionGroupRegions = pd.read_csv(csv)

with open(PATH + 'versions.csv') as csv:

    versions = pd.read_csv(csv)


CUSTOM_PATH = './csv/custom/'

with open(CUSTOM_PATH + 'move_natural_gift.csv') as csv:

    naturalGift = pd.read_csv(csv)

with open(CUSTOM_PATH + 'event_log.csv') as csv:

    eventLogOriginal = pd.read_csv(csv)

# ----------------------------- Files Clean-up ------------------------------ #


def which_version(identifier):
    """Returns a triple VERSION_GROUP_ID, REGION_ID, VERSION_ID

    Usage
    -----
        >>> VERSION_GROUP_ID, REGION_ID, VERSION_ID = which_version('firered')
        >>> print(VERSION_GROUP_ID, REGION_ID, VERSION_ID)
        (7, 1, 10)

    Parameters
    ----------
        identifier : The official name of a game;
        should be in the following list:
            red, blue, yellow, gold, silver, crystal,
            ruby, sapphire, emerald, firered, leafgreen,
            diamond, pearl, platinum, heartgold, soulsilver,
            black, white, black-2, white-2,
            x, y, omega-ruby, alpha-sapphire, sun, moon,

    """
    try:

        __condition = versions["identifier"] == identifier

        version_group_id = int(versions[__condition]["version_group_id"])

        version_id = int(versions[versions["identifier"] == identifier]["id"])

        vrsnGrpRgns = versionGroupRegions

        __condition = vrsnGrpRgns["version_group_id"] == int(version_group_id)

        region_id = int(vrsnGrpRgns[__condition]["region_id"])

        return version_group_id, region_id, version_id

    except TypeError:

        raise TypeError("The game name should be one of the following list:\n"
                        "red, blue, yellow, gold, silver, crystal,\n"
                        "ruby, sapphire, emerald, firered, leafgreen,\n"
                        "diamond, pearl, platinum, heartgold, soulsilver,\n"
                        "black, white, black-2, white-2,\n"
                        "x, y, omega-ruby, alpha-sapphire, sun, moon.")


VERSION_GROUP_ID, REGION_ID, VERSION_ID = which_version('platinum')

__condition = pokemonEvolution["evolution_trigger_id"] == 1

pokemonEvolution = pokemonEvolution[__condition]

__condition = pokemonMoves["version_group_id"] == VERSION_GROUP_ID

pokemonMoves = pokemonMoves[__condition]

__condition = moves["generation_id"] <= REGION_ID

moves = moves[__condition]

typeEfficacy = typeEfficacy['damage_factor'].reshape(18, 18)[:-1, :-1]/100.

# -------------------------- Assistive Functions ---------------------------- #


def efficacy(atk_type, tar_types):
    """Returns an `int` that represents the type efficacy between the attack
    type and the target type(s).

    Usage
    -----
        >>> efficacy(4,9)  # How effective is poison (4) against steel (9)?
        0  # poison moves have no effect on steel-type Pokémons.

        >>> efficacy(17, [2, 14]]) # How effective is dark (17) against a
        ...     Pokémon with a fighting (2) and psychic (14) type?
        1  # Because dark is 1/2 effective against fighting and twice as
        ...     effective against psychic.

    Parameters
    ----------
        atk_type : int
            The attacker's type. Up to Gen.VI this can only be one `int`.
        tar_types : array-like objects
            Theoretically, the length of the array is not limited. But for
            our purposes (calculating in-battle effectiveness), this is no
            more than two. Although no limitation is forced.

    Returns
    -------
        efficacy : float
            The function returns a `float`, which is the multiplicative
            effectiveness of atk_type to tar_types.

    """

    __efficacies = map(lambda x: typeEfficacy[atk_type-1, x-1], tar_types)

    return reduce(lambda x, y: x * y, __efficacies)

# ---------------------------- Class Definitions ---------------------------- #


class Move(object):  # Should also be able to be define by the move's name.

    def __init__(self, move):

        try:
            if issubclass(type(move), int):
                move_id = move

            elif type(move) is str:
                move_id = int(moves[moves['identifier'] == move].id)

        except:
            raise TypeError("`move` should be an integer or"
                            "a move's name.")

        label = move_id - 1

        # ---------------- Initializations from `moves.csv` ----------------- #

        self.id = moves.loc[label, "id"]
        self.identifier = moves.loc[label, "identifier"]
        self.generation_id = moves.loc[label, "generation_id"]
        self.type_id = moves.loc[label, "type_id"]
        self.power = moves.loc[label, "power"]
        self.pp = moves.loc[label, "pp"]
        self.accuracy = moves.loc[label, "accuracy"]
        self.priority = moves.loc[label, "priority"]
        self.target_id = moves.loc[label, "target_id"]
        self.damage_class_id = moves.loc[label, "damage_class_id"]
        self.effect_id = moves.loc[label, "effect_id"]
        self.effect_chance = moves.loc[label, "effect_chance"]

        # -------------- Initializations from `move_meta.csv` --------------- #

        self.meta_category_id = moveMeta.loc[label, "meta_category_id"]
        self.meta_ailment_id = moveMeta.loc[label, "meta_ailment_id"]
        self.min_hits = moveMeta.loc[label, "min_hits"]
        self.max_hits = moveMeta.loc[label, "max_hits"]
        self.min_turns = moveMeta.loc[label, "min_turns"]
        self.max_turns = moveMeta.loc[label, "max_turns"]
        self.drain = moveMeta.loc[label, "drain"]
        self.healing = moveMeta.loc[label, "healing"]
        self.crit_rate = moveMeta.loc[label, "crit_rate"]
        self.ailment_chance = moveMeta.loc[label, "ailment_chance"]
        self.flinch_chance = moveMeta.loc[label, "flinch_chance"]
        self.stat_chance = moveMeta.loc[label, "stat_chance"]

        if move_id in list(moveMetaStatChanges.move_id):

            __condition = moveMetaStatChanges["move_id"] == self.id

            self.stat_change = moveMetaStatChanges[__condition]

        self.name = self.identifier

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class Item(object):
    pass


class Pokemon(object):
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
            if issubclass(type(which_pokemon), int):
                pokemon_id = which_pokemon

            elif type(which_pokemon) is str:
                __condition = pokemon['identifier'] == which_pokemon
                pokemon_id = int(pokemon[__condition].id)

        except:
            raise TypeError("`pokemon` has to be an integer"
                            " or a pokemon's name.")

        LABEL = list(pokemon[pokemon["id"] == pokemon_id].index)[0]

        # ---------------- Initialization from `pokemon.csv` ---------------- #

        self.id = pokemon.loc[LABEL, "id"]
        self.identifier = pokemon.loc[LABEL, "identifier"]
        self.species_id = pokemon.loc[LABEL, "species_id"]
        self.height = pokemon.loc[LABEL, "height"]
        self.weight = pokemon.loc[LABEL, "weight"]
        self.base_experience = pokemon.loc[LABEL, "base_experience"]
        self.order = pokemon.loc[LABEL, "order"]
        self.is_default = pokemon.loc[LABEL, "is_default"]

        # ------------ Initialization from `pokemon_species.csv` ------------ #

        pkmnSpcs = pokemonSpecies

        self.generation_id = pkmnSpcs.loc[LABEL, "generation_id"]
        self.evolves_from = pkmnSpcs.loc[LABEL, "evolves_from_species_id"]
        self.evolution_chain_id = pkmnSpcs.loc[LABEL, "evolution_chain_id"]
        self.color_id = pkmnSpcs.loc[LABEL, "color_id"]
        self.shape_id = pkmnSpcs.loc[LABEL, "shape_id"]
        self.gender_rate = pkmnSpcs.loc[LABEL, "gender_rate"]
        self.capture_rate = pkmnSpcs.loc[LABEL, "capture_rate"]
        self.base_happiness = pkmnSpcs.loc[LABEL, "base_happiness"]
        self.is_baby = pkmnSpcs.loc[LABEL, "is_baby"]
        self.gender_differences = pkmnSpcs.loc[LABEL, "has_gender_differences"]
        self.growth_rate_id = pkmnSpcs.loc[LABEL, "growth_rate_id"]
        self.forms_switchable = pkmnSpcs.loc[LABEL, "forms_switchable"]

        self.name = self.identifier

        # If `self.gender_rate` is -1, then `self` is genderless (3).
        # `self.gender_rate` divided by 8 is the probability of `self` being
        # a female.
        if self.gender_rate == -1:
            self.gender = 3
        elif not np.random.binomial(1, self.gender_rate/8):
            self.gender = 2
        else:
            self.gender = 1

        self.happiness = self.base_happiness

        __condition = pokemonTypes["pokemon_id"] == self.id

        self.types = list(pokemonTypes[__condition]["type_id"])

        try:
            self.level = level

        except:
            raise TypeError("`level` has to be an integer"
                            " or an integer string.")

        if self.level not in range(1, 101):
            raise ValueError("Level should be in range(1,101).")

        __condition = (experience["growth_rate_id"] == self.growth_rate_id) &\
                      (experience["level"] == self.level)

        self.exp = experience[__condition]["experience"]

        # --------------- BASE STAT, IV, & EV Initialization ---------------- #

        __condition = pokemonStats["pokemon_id"] == self.id

        __pokemon_base_stat = pokemonStats[__condition]["base_stat"].values

        self.base = pd.Series(data=__pokemon_base_stat,
                              index=self.STAT_NAMES)

        self.iv = pd.Series(data=[np.random.randint(1, 31) for i in range(6)],
                            index=self.STAT_NAMES)

        _cond = pokemonStats["pokemon_id"] == self.id

        self.effort = pd.Series(data=list(pokemonStats[_cond]["effort"]),
                                index=self.STAT_NAMES)

        self.ev = pd.Series(data=[0 for x in range(6)],
                            index=self.STAT_NAMES)

        # ---------------------- NATURE Initialization ---------------------- #

        self.nature_id = np.random.randint(1, 25)

        __id = self.nature_id

        self.nature = pd.Series(index=["id", "name",
                                       "likes_flavor_id", "hates_flavor_id"],
                                data=[self.nature_id,
                                      natures.loc[__id, "identifier"],
                                      natures.loc[__id, "likes_flavor_id"],
                                      natures.loc[__id, "hates_flavor_id"]])

        self.nature.name = self.nature.iloc[1]

        if x == natures.loc[self.nature_id, "decreased_stat_id"]:
            __decreased_stat = np.array([0.9 for x in range(1, 7)])

        else:
            __decreased_stat = np.array([1 for x in range(1, 7)])

        if x == natures.loc[self.nature_id, "increased_stat_id"]:
            __increased_stat = np.array([1.1 for x in range(1, 7)])

        else:
            __increased_stat = np.array([1 for x in range(1, 7)])

        __nature_modifier = __increased_stat * __decreased_stat

        self.nature_modifier = pd.Series(data=__nature_modifier,
                                         index=self.STAT_NAMES)

        # ---------------------- STATS Initialization ---------------------- #

        __inner = (2 * self.base + self.iv + np.floor(self.ev/4)) * self.level

        __left_factor = np.floor(__inner/100) + 5

        self.stats = np.floor(__left_factor * self.nature_modifier)

        self.stats.hp = np.floor(__inner.hp/100) + self.level + 10

        if self.name == 'shedinja':
            self.stats.hp = 1

        self.stats = self.stats.reindex(self.STAT_NAMES)

        # ---------------------- ABILITY Initialization --------------------- #

        __cond = (pokemonAbilities["pokemon_id"] == self.id) & \
                 (pokemonAbilities["is_hidden"] == 0)

        self.ability = np.random.choice(pokemonAbilities[__cond]["ability_id"])

        # ----------- IN-BATTLE STATS and CONDITION Initialization -----------#

        self.current = pd.Series(index=self.CURRENT_STAT_NAMES,
                                 data=list(self.stats) + [100., 100.])

        self.stage = pd.Series(index=self.CURRENT_STAT_NAMES + ['critical'],
                               data=[0 for x in range(9)])

        self.status = pd.Series(index=["ailment", "volatile"],
                                data=[0., deque()])

        self.status_timer = pd.Series(index=["ailment", "volatile"],
                                      data=[0., deque()])

        self.held_item = 0

        self.critical_stage_changed = 0

        # ---------------------- MOVES Initialization ----------------------- #

        ___condition = (pokemonMoves["pokemon_id"] == self.id) & \
                       (pokemonMoves["pokemon_move_method_id"] == 1) & \
                       (pokemonMoves.level < self.level + 1)

        __all_moves = pokemonMoves[___condition]["move_id"]

        __num_of_moves = np.clip(a=len(__all_moves.values),
                                 a_max=4,
                                 a_min=0)

        # `__num_of_moves` should cap at 4; added 1 to 5 to count for the
        # upper bound of `range()`.

        self.moves = pd.Series(index=[x for x in range(1, __num_of_moves+1)],
                               data=[Move(x) for x in __all_moves.values[-4:]])

        # ------------------------------ END -------------------------------- #

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def reset_current(self):
        """The current stats should be reset after each battle,
        after changes made by leveling-up.
        """
        self.current = pd.Series(index=self.CURRENT_STAT_NAMES,
                                 data=list(self.stats) + [100., 100.])

        self.stage = pd.Series(index=self.CURRENT_STAT_NAMES + ['critical'],
                               data=[0 for x in range(9)])

        self.status.volatile = deque()

    def level_up(self):
        """Changes the stats if leveling-up's condition is met.

        Changes include:

            :level: increase by 1.
            :stats: recalculate based on the current ev's and
                    the current level.
            :evolvution: if the evolution condition is met, evolve.
            :moves: if a new move is learnable, make a choice of
                    whether to learn it or not.

        In this order.
        """

        self.level += 1  # TODO: should be determined by exp.

        __inner = (2 * self.base + self.iv + np.floor(self.ev/4)) * self.level

        __left_factor = np.floor(__inner/100) + 5

        self.stats = np.floor(__left_factor * self.nature_modifier)

        self.stats.hp = np.floor(__inner.hp * self.level/100) + self.level + 10

        self.stats = self.stats.reindex(self.STAT_NAMES)

    def ismobile(self):
        pass


# ---------------------------- Battle Mechanisms ---------------------------- #


def report():
#    if None in event.values():
#        raise ValueError("The event log is incomplete."
#                         " Some entries are missing.")
#    else:
     event_log.loc[turn_num] = event


def hit_rate(f1, m1, f2):
    """Some awesome hit rate explanations.
    """

    if not np.isnan(m1.accuracy) and m1.meta_category_id != 9:

        __hit_stage = f1.stage.accuracy - f2.stage.evasion
        __hit_stage = np.clip(a=__hit_stage, a_max=6, a_min=-6)

        hit_stage_chances = {
                             -6: 3./9., 6: 9./3.,
                             -5: 3./8., 5: 8./3.,
                             -4: 3./7., 4: 7./3.,
                             -3: 3./6., 3: 6./3.,
                             -2: 3./5., 2: 5./3.,
                             -1: 3./4., 1: 4./3.,
                             0: 3./3.
                             }

        hit_modifier_stage = hit_stage_chances[__hit_stage]

        # TODO. Holding certain items will increase
        # or decrease the hit rate.
        hit_modifier_item = 1

        # TODO. Having certain abilities will increase the hit rate.
        hit_modifier_ability = 1

        hit_threshold = (m1.accuracy * hit_modifier_stage *
                         hit_modifier_item * hit_modifier_ability)

        # Participates in the damage calculation.
        # If the move misses, then `modifier_hit` = 0.
        modifier_hit = 1

        if np.random.randint(1, 100) > hit_threshold:

            modifier_hit = 0

            print("{} has missed the attack!".format(f1.name))

    # Moves that surely hits.
    elif np.isnan(m1.accuracy):

        modifier_hit = 1  # XXX: is this how it works?

    # One-hit Kill Hit Rate Determination.
    elif m1.meta_category_id == 9:

        modifier_hit = ohko_hit_rate(f1, f2)

    return modifier_hit


def ohko_hit_rate(f1, f2):

    if ((f2.level > f1.level) or
            (f2.ability == 5) or
            (np.random.randint(1, 100) >= (30 + f1.level - f2.level))):

        modifier_hit = 0

    else:
        modifier_hit = 1

    return modifier_hit


def set_damage_moves(f1, m1, f2):

    if m1.name == 'sonic-boom':
        damage = 20

    elif m1.name == 'dragon-rage':
        damage = 40

    elif m1.name in ['seismic-toss', 'night-shade']:
        damage = f2.level

    elif m1.name == 'psywave':
        damage = f1.level * (np.random.random_sample() + 0.5)

    elif m1.name == 'super-fang':
        damage = f2.level * 0.5

    elif m1.name == 'endeavor':
        damage = np.clip(a=f2.current.hp - f1.current.hp,
                         a_min=0,
                         a_max=f2.current.hp)

    elif m1.name == 'counter':  # FIXME:
        damage = 404

    elif m1.name == 'mirror-coat':  # FIXME:
        damage = 404

    elif m1.name == 'bide':  # FIXME:
        damage = 404

    elif m1.name == 'metal-burst':  # FIXME:
        damage = 404

    elif m1.name == 'final-gambit':
        damage = f1.current.hp

    elif m1.name == 'natures-madness':  # FIXME:
        damage = 404

    try:
        return damage

    except NameError:
        raise NameError("Some cases have not been covered")


def direct_damage(f1, m1, f2):

    if m1.damage_class_id == 2:

        A = f1.current.attack
        D = f2.current.defence

    elif m1.damage_class_id == 3:

        A = f1.current.specialAttack
        D = f2.current.specialDefence

    # Very Special Cases

    # Gyro-ball: The slower the user, the greater the damage.
    if m1.name == 'gyro-ball':

        m1.power = np.clip(a=25 * f2.current.speed / f1.current.speed,
                           a_max=150,
                           a_min=0)

    # Natural Gift: The user draws power to attack by using its held Berry.
    # The Berry determines its type and power.
    elif m1.name == 'natural-gift':

        if f1.held_item in naturalGift.item_id.values:

            __index = naturalGift["item_id"] == f1.held_item

            m1.power = naturalGift[__index].power.values
            m1.type_id = naturalGift[__index].type_id.values

        else:
            m1.power = 0
            print("{}'s attack has failed.".format(f1.name))

    # Beat Up: 面倒くさい...
    elif m1.name == 'beat-up':
        m1.power = 10

    # Hit Rate Determination,
    modifier_hit = hit_rate(f1, m1, f2)
    event["move_succeed"] = modifier_hit

    # Set-damage Moves Damage Determination
    if m1.name in ['sonic-boom', 'dragon-rage', 'seismic-toss',
                   'night-shade', 'psywave', 'super-fang', 'endeavor',
                   'counter', 'mirror-coat', 'bide', 'metal-burst',
                   'final-gambit', 'natures-madness']:

        # `modifier_type_immune` is 0 if the efficacy
        # is 0, otherwise it's 1.
        modifier_type_immune = 1 if efficacy(m1.type_id, f2.types) else 0

        damage = set_damage_moves(f1, m1, f2)

        damage *= modifier_type_immune
        modifier_critical = 1
        modifier_type = 1

    elif m1.meta_category_id == 9:
        damage = f2.current.hp

    else:
        # Damage Determination

        # 1. Raise/lower the critical stage.
            # TODO: Move Dire Hits => 'use_an_item()`.

        if not f1.critical_stage_changed:

            if f1.held_item in [303, 209]:

                f1.stage.critical = 1

            elif ((f1.id == 83 and f1.held_item == 236) or
                  (f1.id == 113 and f1.held_item == 233)):

                f1.stage.critical = 2

            f1.critical_stage_changed = 1

        f1.stage.critical += m1.crit_rate

        # 2. Calculate various modifiers.
        # 2.1 The critical modifier is determined based on the stage.

        __critical_chances = {0: 1/16,
                              1: 1/8,
                              2: 1/4,
                              3: 1/3,
                              4: 1/2}

        __critical_pr = __critical_chances[f1.stage.critical]

        __critial_random_var = np.random.binomial(1, __critical_pr)

        modifier_critical = 2 if __critial_random_var == 1 else 1

        # 2.2 The type modifier is the same as the type effectiveness.
        modifier_type = efficacy(m1.type_id, f2.types)

        # 2.3 The STAB modifier is 1.5. If the ability is
        # 'Adaptibility', then 2.
        if m1.type_id in f1.types:
            modifier_stab = 2 if f1.ability == 91 else 1.5

        else:
            modifier_stab = 1

        # 2.4 The random modifier is uniformly distributed in [.85, 1].
        modifier_random = np.random.random_sample() * 0.15 + 0.85

        # 2.5 If the move is a special move, and the ability is not guts,
        # and the user Pokémon is burnt, then half the damage.
        if ((f1.status.ailment == 4) and (f1.ability != 62) and
                (m1.damage_class_id == 2)):

            modifier_burn = 0.5

        else:

            modifier_burn = 1

        # Multiply all the modifiers.
        modifier_damage = (modifier_type * modifier_stab *
                           modifier_random * modifier_critical *
                           modifier_burn * modifier_hit)

        damage = (np.floor((((2*f1.level/5 + 2) * m1.power * A/D)/50 + 2) *
                           modifier_damage))

    # Cannot deal more damage than the opponent's current HP.
    damage = np.clip(a_max=f2.current.hp,
                     a_min=0,
                     a=damage)

    # Remove the amount of damage from the opponent's HP.
    f2.current.hp -= damage

    event["damage_to_opponent"] = damage

    # If, in addition, the move drains HP from the opponent:
    if m1.meta_category_id == 8:

        recovery = damage * m1.drain/100
        f1.current.hp = np.clip(a=f1.current.hp + recovery,
                                a_max=f1.stats.hp,
                                a_min=0)

        event["damage_to_self"] = -recovery

        if damage != 0:
            print("{} has recovered {} HP "
                  "from absorbing!".format(f1.name, damage))

    if modifier_hit == 1:

        if modifier_critical == 2:
            print("A critical hit!")
        if modifier_type >= 2:
            print("Very effective!")
        elif modifier_type <= 0.5:
            print("Not very effective...")

        print("{0} deals {2} damage to {1}.\n"
              "{0}'s HP: {3}\n{1}'s HP: {4}\n"
              "".format(f1.name, f2.name, damage,
                        f1.current.hp, f2.current.hp))


def stat_changer(f, m):

    __stage_multipliers = {-6: 2./8., 6: 8./2.,
                           -5: 2./7., 5: 7./2.,
                           -4: 2./6., 4: 6./2.,
                           -3: 2./5., 3: 5./2.,
                           -2: 2./4., 2: 4./2.,
                           -1: 2./3., 1: 3./2.,
                           0: 1.
                           }

    if np.isnan(m.effect_chance):
        m.effect_chance = 100.

    if np.random.binomial(1, m.effect_chance/100.) == 1:

        for __index, __stat_name in enumerate(f.CURRENT_STAT_NAMES):

            if __index + 1 in m.stat_change.stat_id.values:

                __condition = m.stat_change["stat_id"] == __index + 1

                __index = m.stat_change[__condition].index[0]

                __stage_incr = m.stat_change.change[__index]

                f.stage[__stat_name] += __stage_incr

                f.stage[__stat_name] = np.clip(a=f.stage[__stat_name],
                                               a_max=6,
                                               a_min=-6)

                if __stat_name not in ['hp', 'accuracy', 'evasion']:
                    f.current[__stat_name] = (f.stats[__stat_name] *
                                              __stage_multipliers[__index + 1])

                event["stat_change_to_self_id"].append(__index + 1)
                event["stat_change_to_self_stage"].append(__stage_incr)

                print("{}'s {} is raised!".format(f.name, __stat_name))


def battle_finished(f1, f2):

    if np.isnan(f1.current.hp) or np.isnan(f2.current.hp):

        print("Someone's HP is nan. Something's wrong.")

    return (f1.current.hp <= 0 or
            f2.current.hp <= 0 or
            np.isnan(f1.current.hp) or
            np.isnan(f2.current.hp))


def ismobile(f):
    """Checks if the Pokémon `f` is able to move in this turn or not.

    Should return two values: [is_mobile, ailment_id]
    is_mobile : Boolean
        True if Pokémon `f` is able to make a move in this turn. Else, False.
    """
    is_mobile = True

    return is_mobile


def priorities(p1, p1_move, p2, p2_move):

    if p1_move.priority > p2_move.priority:
        f1, f2, m1, m2 = p1, p2, p1_move, p2_move

    elif p1_move.priority < p2_move.priority:
        f1, f2, m1, m2 = p2, p1, p2_move, p1_move

    else:
        if p1.current.speed >= p2.current.speed:
            f1, f2, m1, m2 = p1, p2, p1_move, p2_move
        else:
            f1, f2, m1, m2 = p2, p1, p2_move, p1_move

    return f1, f2, m1, m2


# ------------------------------ Menu Options ------------------------------- #

def make_a_move(f1, m1, f2):
    """Some awesome damage calculation explanations.
    """
    print("{} uses {}!\n".format(f1.name, m1.name))

    # Everything that deals direct damage.
    if m1.meta_category_id in [0, 4, 6, 7, 8, 9]:

        direct_damage(f1, m1, f2)

    # Moves that ail the *opponent* pokemon.
    if m1.meta_category_id in [1, 4, 5]:

        if np.random.binomial(1, m1.ailment_chance/100) == 1:

            f2.status.ailment = m1.meta_ailment_id

            __ailment = moveMetaAilments.loc[m1.meta_ailment_id + 1,
                                             "identifier"]

            print("{} is {}!".format(f2.name, __ailment))

    # Moves that raises the user's stats
    if m1.meta_category_id in [2, 7]:

        stat_changer(f1, m1)

    # Moves that lowers the opponent's stats
    # FIXME: add changes on `current.stats`.
    if m1.meta_category_id in [5, 6]:

        stat_changer(f2, m1)

    # Moves that heals the user.
    if m1.meta_category_id == 3:

        recovery = f1.stats.hp * (m1.healing/100 + 1)
        f1.current.hp = np.clip(a=recovery,
                                a_max=f1.stats.hp,
                                a_min=0)

        event["damage_to_self"] = -recovery
        print("{} has recovered health!".format(f1.name))


def use_an_item():
    pass


def empty_event():
    return pd.Series({
                     "round": None, "order": None, "pokemon_id": None,
                     "option": None, "move_id": None, "item_id": None,
                     "change_to_pokemon_id": None, "damage_to_opponent": None,
                     "damage_to_self": None, "ailment_to_opponent": None,
                     "ailment_to_self": None,
                     "volatile_to_opponent": deque(),
                     "volatile_to_self": deque(),
                     "stat_change_to_self_id": deque(),
                     "stat_change_to_self_stage": deque(),
                     "stat_change_to_opponent_id": deque(),
                     "stat_change_to_opponent_stage": deque(),
                     "weather": None
                     })


def battle(p1, p2):
    """Simulates a battle.

    Parameters
    ----------
    p1, p2 : any two Pokémons.
    """
    # Initializing global constants
    global round_num, turn_num, event_log, event, weather

    round_num = 1
    turn_num = 1

    event_log = eventLogOriginal

    event = empty_event()

    print("A level {} {} fights a level {} {}!!"
          "".format(p1.level, p1.name, p2.level, p2.name))
    print("No.{} {}'s stats:\n{}\nmoves:\n{}\n"
          "".format(p1.id, p1.name, p1.stats, p1.moves))
    print("No.{} {}'s stats:\n{}\nmoves:\n{}\n"
          "".format(p2.id, p2.name, p2.stats, p2.moves))

    # TODO: the weather_id of the weather on the field.
    weather = 0

    while True:  # The only exit is through fainting.

        p1_move_index = np.random.randint(1, len(p1.moves))
        p1_move = p1.moves[p1_move_index]
        p2_move_index = np.random.randint(1, len(p2.moves))
        p2_move = p2.moves[p2_move_index]

        # Compare priorities. f1, f2 = first_hand, second_hand.
        # f1 always attacks first.
        f1, f2, m1, m2 = priorities(p1, p1_move, p2, p2_move)

        # ------------------------- THE MAIN BATTLE ------------------------- #

        event["weather"] = 0

        # f1's turn. Uses m1.

        event["round"] = round_num
        event["order"] = 1
        event["pokemon_id"] = f1.id
        event["option"] = 'move'
        event["move_id"] = m1.id
        event["item_id"] = 0
        event["change_to_pokemon_id"] = 0

        if ismobile(f1):
            make_a_move(f1, m1, f2)
        else:
            print("{} cannot move due to {}"
                  "".format(f1.name, f1.status.ailment))
        report()
        event = empty_event()

        turn_num += 1

        if battle_finished(f1, f2):
            break

        # f2's turn. Uses m2.

        event["round"] = round_num
        event["order"] = 2
        event["pokemon_id"] = f2.id
        event["option"] = 'move'
        event["move_id"] = m2.id
        event["item_id"] = 0
        event["change_to_pokemon_id"] = 0

        if ismobile(f2):

            make_a_move(f2, m2, f1)

        else:

            print("{} cannot move due to {}"
                  "".format(f2.name, f2.status.ailment))
        report()
        event = empty_event()

        turn_num += 1

        if battle_finished(f1, f2):
            break

        round_num += 1

    # Who won?
    if f1.current.hp == 0:  # f2 wins.
        f2.ev += f1.effort
        print("{} has won!!".format(f2.name))
    else:  # f1 wins.
        f1.ev += f2.effort
        print("{} has won!!".format(f1.name))

    # After battle events

    p1.reset_current()
    p2.reset_current()


battle(Pokemon(np.random.randint(1, 493)), Pokemon(np.random.randint(1, 493)))


# ------------------------------- Simulations ------------------------------- #
def randPokemon():

    bob = Pokemon(np.random.randint(1, 493), level=np.random.randint(1, 100))
    return bob

# randPokemon()


# ---------------------------- Helper Functions ---------------------------- #

def classHelper(dataFrame):

    with open('tempOut.txt', "w+") as output:
        for name in list(dataFrame):
            output.write('self.{0} = moveMeta.loc[label,"{0}"]\n'.format(name))

# classHelper(moveMeta)
