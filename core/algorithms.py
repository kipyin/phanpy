#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''This file contains all the main algorithms in Pokemon battles.

attacking_order(...)
    attacking_order(pokemon1, move1, pokemon2, move2)

    Determine which pokemon takes the first move in a battle.

    ``move1`` and ``move2`` are ``pokemon1`` and ``pokemon2``'s
    moves respectively.

    These parameters are abbreviated to ``p1(2)`` and ``m1(2)``.


is_mobile(...)
    is_mobile(some_pokemon, some_move)

    Check if the given pokemon is able to make a move at the beginning
    of a turn.

    Not being able to move is spossibly casued by:

        - used a move require ``recharge`` in the following turn;
        - paralyzed (with 25% chance not being able to move);
        - freeze (unless used a move with a ``defrost`` tag);
        - flinch (if the pokemon moves second);
        - infatuation (50% not being able to make a move);
        - sleep (unless use ``sleep-talk`` or ``snore``).

    Returns
    -------
    is_mobile : bool


makes_hit(...)
    makes_hit(f1, m1, f2)
    makes_hit(user_pokemon, move, target_pokemon)

    Calculate if the the move user makes a hit or not.

    Generally, this is done by the following formula:

        p = move's accuracy * user's accuracy / target's evasion

    where ``p`` is the probability of making a hit. However, there are
    various exceptions, such as:

        - if the target pokemon has a status ``taking-aim`` (caused by
        the move ``mind-reader`` or ``lock-on``), then the move will
        surely hit, ignoring *everything* else.
        - if the target is ``semi-invulnerable``, i.e. if the target
        is in the effect of the move ``fly``, ``dig``, or ``dive``,
        then unless the move is some specific move, the user will surely
        miss the attack.

    * Note that all functions follow the convention of using ``f1`` to
    represent the user pokemon, and ``f2`` to represent the target
    pokemon. ``m1`` and ``m2`` are still ``f1`` and ``f2``'s moves
    respectively.

    Returns
    -------
    makes_hit : bool


critical(...), stab(...), and burn(...) are damage modifiers used in
    calculating the damage.


base_damage(...)
    base_damage(f1, m1, f2, m2)
    base_damage(user_pokemon, move1, target_pokemon, move2)

    a.k.a. regular damage.

    Calculate the base damage of a move. If a move's base damage cannot
    be calculated, nothing is returned.

    There are two types of damages. One is the regular damage, as
    discussed here. The other is the direct damage. This is discussed
    in ``calculated_damage(...)``.

    Most moves with set powers deal regular damages. The damage modifier
    functions ``critica(...)``, ``stab(...)``, and ``burn(...)`` are
    used here.

    Returns
    -------
    base_damage : int or floored float
        A value to be passed to ``calcualted_damage(...)``.


calculated_damage(...)
    calculated_damage(f1, m1, f2, m2)
    calculated_damage(user_pokemon, move1, target_pokemon, move2)

    Calculate the damage for both regular damages and direct damages.

    A lot of move's effects are discussed here.

    Returns
    -------
    damage : int or floored float
        The actual damage caused to the target, ignoring side effects
        such as absorption or recoil damage.


stat_changer(...)
    stat_changer(f1, m1, f2, m2)

    If ``m1`` causes stat chagnes, apply the effect on either ``f1`` or
    ``f2`` or both, depending on the effect. Return nothing.


ailment_inflictor(...)
    ailment_inflictor(f1, m1, f2, m2)

    If ``m`` inflicts ailments (a.k.a. status conditions), apply the
    effect. Return nothing.


status_damage(...)
    status_damage(f1, m1, f2, m2)

    At the end of a turn, if a pokemon has status conditions such as
    ``poison`` or ``burn``, apply the effect. Return nothing.


effect(...)
    effect(f1, m1, f2, m2)

    A catch-all function for all the effects. Apply the effect of ``m1``.
    Return nothing.


attack(...)
    attack(f1, m1, f2, m2)

    Apply the damage to ``f2`` (if makes a hit). Apply the move's effects
    and all the side-effects. Apply the status damage at the end.
    Return nothing.

'''

# ============ Activate these codes when import fails. =============== #
# Solution #1 (Should always work. Need to change the root path accordingly.)
import os
import sys

file_path = os.path.dirname(os.path.abspath(__file__))
root_path = file_path.replace('/phanpy/core', '')

sys.path.append(root_path) if root_path not in sys.path else None

# Solution #2 (Works for top-level files.)
# import os, sys
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Solution #3 (Works for top-level files.)
# from os import sys, path
# sys.path.append(path.abspath('.'))

from collections import deque
from functools import reduce
import numpy as np
from numpy.random import binomial, uniform, randint, choice

from phanpy.core.tables import efficacy
from phanpy.core.objects import Item, Status
import phanpy.core.tables as tb

move_natural_gift = tb.move_natural_gift
which_ability = tb.which_ability

def attacking_order(p1, p1_move, p2, p2_move):
    """Determine the attacking order based on the priorities of the
    mvoes, the speed of each pokemon, their held items, and their
    abilities (if applicable).

    The attacking order should comply with the following scheme:

        held-items -> abilities -> moves -> field-effects -> speeds

    1. held-items.
        - ``quick-claw``: The Pokemon holding a ``quick-claw`` has a
        20% chance to move first, ignoring the effect of ``trick-room``
        and abilities when activated. If, on rare occasions, two
        pokemons both hold ``quick-claw``'s, then the chance that the
        effects are both activated is 0.04, given that both pokemons
        hold ``quick-claw``. In this case, the effects are both ignored.

        - ``full-incense`` and ``lagging-tail``: The item-holder always
        moves last, unless both Pokemons are holding one of these items.
        In such a case, regular priorities are considered.

    2. abilities.
        - ``stall``: The Pokemon with this ability will move last. The
        rare situations stated above can also be applied here.

        - (GEN.VI+) ``gale-wings``: This ability increases the priority
        of Flying-type moves by one. Affected Flying-type attacks and
        offensive status moves can be blocked by ``quick-guard``.
        This ability does not increase the priority of Flying-type
        ``hidden-power``, ``natural-gift``, or ``judgment``, as they
        are treated as Normal-type moves before being used. Starting
        from GEN.VII, ``gale-wings`` works only if the user has full HP.

        - ``prankster``: This ability increases the priority of status
        moves by one.
        GEN.V: Any move that is increased in priority from Prankster
        is not blocked by ``quick-guard``.
        GEN.VI: Can be blocked by ``quick-guard`` (make up your mind,
        Nintendo).
        GEN.VII+: More changes, but they are not on the top of our list
        for now.

        - GEN.VII abilities: ``traige``, ``queenly-majesty``, ``dazzle``.

    3. moves.
        - All moves' priorities are recorded in ``~/data/csv/moves.csv``

        - ``quick-guard``: Quick Guard protects all Pokémon on the
        user's side of the field from moves that have increased priority
        during that turn, such as Quick Attack or Aqua Jet.
        It does not block moves that have been given an increased
        priority through Prankster that would not usually have one.

    4. field-effects.
        - ``trick-room``: Trick Room reverses the move order within each
        priority bracket so that Pokémon with a lower Speed stat attack
        first, while those with a higher Speed stat will attack last.

        - GEN.VII field-effects: move:``psychic-terrain``.
    """

    if p1.item.name == 'quick-claw' and p2.item.name == 'quick-claw':
        # If both pokemon are holding 'quick-claw', skip to the next
        # checker.
        pass

    elif p1.item.name == 'quick-claw' and bool(binomial(1, 0.2)):
        p1.order, p2.order = 1, 2
        return p1, p1_move, p2, p2_move

    elif p2.item.name == 'quick-claw' and bool(binomial(1, 0.2)):
        p1.order, p2.order = 2, 1
        return p2, p2_move, p1, p1_move
    else:
        pass

    laggers = ['lagging-tail', 'full-incense']

    # Check for laggers
    if p1.item.name in laggers and p2.item.name in laggers:
        pass

    elif p1.item.name in laggers:
        p1.order, p2.order = 2, 1
        return p2, p2_move, p1, p1_move

    elif p2.item.name in laggers:
        p1.order, p2.order = 1, 2
        return p1, p1_move, p2, p2_move
    else:
        pass

    # Check for ability:stall.
    if (p1.ability == which_ability('stall')
            and p2.ability == which_ability('stall')):
        pass

    elif p1.ability == which_ability('stall'):
        p1.order, p2.order = 2, 1
        return p2, p2_move, p1, p1_move

    elif p2.ability == which_ability('stall'):
        p1.order, p2.order = 1, 2
        return p1, p1_move, p2, p2_move
    else:
        pass

    # Move on to the moves' priority check.
    if p1_move.priority > p2_move.priority:
        # If the moves' priorities are different, use the moves'
        # prioirties.
        p1.order, p2.order = 1, 2
        f1, f2, m1, m2 = p1, p2, p1_move, p2_move

    elif p1_move.priority < p2_move.priority:
        p1.order, p2.order = 2, 1
        f1, f2, m1, m2 = p2, p1, p2_move, p1_move

    else:
        # If the moves' priorities are the same, determine the
        # priorities based on the Pokémons' speeds.
        if p1.current.speed >= p2.current.speed:

            p1.order, p2.order = 1, 2
            f1, f2, m1, m2 = p1, p2, p1_move, p2_move
        else:

            p1.order, p2.order = 2, 1
            f1, f2, m1, m2 = p2, p1, p2_move, p1_move

        if 'trick-room' in p1.status and 'trick-room' in p2.status:
            # If both pokemons suffer from trick-room effect, switch the
            # priority.
            f1, m1, f2, m2 = f2, m2, f1, m1

    return f1, m1, f2, m2


def is_mobile(f, m):
    """Return ``True`` if the Pokémon is able to **use** a selected move.

    Not be able to move if suffer from:
        # XXX: finish this.
    """

    statuses = f.status

    if 'recharge' in f.status:
        # `f` cannot make a move after using a move requiring
        # recharging.
        return False

    elif f.order == 2 and 'flinch' in statuses:
        # A Pokémon can only flinch if it is hit by another Pokémon's
        # move before using its move.
        return False

    elif 'paralysis' in statuses:
        return bool(binomial(1., 0.75))  # 75% chance not to be paralyzed.

    elif 'infatuation' in statuses:
        return bool(binomial(1., 0.5))  # 50% chance so it doesn't matter.

    elif (('sleep' in statuses) and
          (m.name not in ['sleep-talk', 'snore'])):
        # If the Pokémon is sleeping and not using sleep-talk or
        # snore.
        return False

    elif (('freeze' in statuses) and
          ('defrost' not in m.flag.name)):
        # If the Pokémon is frozen and not using a move with defrost
        # flag.
        return False

    elif 'confusion' in statuses:
        # The confused condition causes a Pokémon to sometimes hurt
        # itself in its confusion instead of executing a selected move.
        # From Generation I to VI, the chance to hurt itself is 50%;
        # in Generation VII, it is 33%. The damage is done as if the
        # Pokémon attacked itself with a 40-power typeless physical
        # attack (without the possibility of a critical hit).
        if binomial(1, 0.5):
            f1.current.hp -= 2 + (2 * (f1.level/5 + 1) * 40 * A/D) // 50
            return False
        else:
            return True

    return True


def makes_hit(f1, m1, f2):
    """Calculate if the the move user makes a hit or not."""

    if 'taking-aim' in f2.status:
        # If the target has been aimed at in the previous turn, the
        # attacker's move will not miss. 'taking-aim' should be have a
        # life time of 1.
        # Moves that induce 'taking-aim' status are 'mind-reader' and
        # 'lock-on'.
        return True

    elif 'semi-invulnerable' in f2.status:
        # XXX: best way to do this? This works.
        # If the opponent is semi-invulnerable, i.e. if the opponent
        # used bounce, fly, sky-drop, dig, or dive. Unless the user's
        # move is one of specific moves, the user's move surely won't
        # hit.
        #
        # See also:
        # https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_can_hit_semi-invulnerable_Pokémon
        if (
            ('flying-up-high' in f2.status) and
            (m1.name in ['gust', 'hurricane', 'sky uppercut', 'smack down',
                         'thousand arrows', 'thunder', 'twister',
                         'whirlwin'])
           ):

            # Does not exempt from the regular accuracy check.
            pass

        elif (('underground' in f2.status) and
              (m1.name in ['earthquake', 'magnitude', 'fissure'])):

            pass

        elif (('underwater' in f2.status) and
              (m1.name in ['surf', 'whirlpool'])):

            pass

        else:
            # If one of the conditions above is met, skip this `else`
            # statement and go through the regular accuracy check.
            return False

    if np.isnan(m1.accuracy):
        # I haven't found any cases where the accuracy is nan and still
        # has a chance to miss.
        # XXX do an exhaustive check on this.
        return True

    else:
        # If the move's accuracy is not nan, use the regular hit rate
        # formula P = move's accuracy * user's accuracy / opponent's
        # evasion.
        p = m1.accuracy/100. * f1.stage_factor.accuracy/f2.stage_factor.evasion
        return bool(binomial(1., p))


def critical(f1, m1):
    """Returns 2 if a hit is critical else 1 (Gen.II ~ Gen.V).

    # XXX: moves exempt from critical hit calculation?
    """
    f1.stage.critical += m1.crit_rate

    f1.stage.critical = np.clip(a=f1.stage.critical, a_max=4, a_min=0)

    critical_chances = {0: 1/16.,
                        1: 1/8.,
                        2: 1/4.,
                        3: 1/3.,
                        4: 1/2.}

    p = critical_chances[f1.stage.critical]

    critical_rv = binomial(1, p)

    # Since critical_rv is either 0 or 1, and we want the return either
    # 1 or 2, we can just add 1 to the random variable.
    return critical_rv + 1


def stab(f1, m1):
    """Return 1.5 if the move's type is one of the user's types,
    otherwise return 0, unless the user's ability is Adaptibility,
    in which case return 2.
    """
    if m1.type in f1.types:
        return 2 if f1.ability == 91 else 1.5

    else:
        return 1


def burn(f1, m1):
    """If the user is burned and trying to use a physical move, return
    0.5, otherwise return 1, unless the user's ability is Guts, in
    which case also return 1.
    """
    if (('burn' in f1.status) and (f1.ability != 62) and
            (m1.damage_class_id == 2)):
        return 0.5

    else:
        return 1


def base_damage(f1, m1, f2, m2):
    """Return the damage for all moves deals regular damage.
    """
    effect = m1.effect_id

    critical_modifier = critical(f1, m1)
    type_modifier = efficacy(m1.type, f2.types)
    random_modifier = uniform(0.85, 1.)
    stab_modifier = stab(f1, m1)
    burn_modifier = burn(f1, m1)
    weather_modifier = 1.
    other_modifier = 1.

    modifier_list = [critical_modifier, type_modifier, random_modifier,
                     stab_modifier, burn_modifier, weather_modifier,
                     other_modifier]

    modifiers = reduce(lambda x, y: x * y, modifier_list)

    if m1.damage_class_id == 2:
        A = f1.current.attack
        D = f2.current.defense
    else:
        A = f1.current.specialAttack
        D = f2.current.specialDefense

    if effect == 155:  # Beat-up
        # Inflicts {mechanic:typeless} {mechanic:regular-damage}.
        # Every Pokémon in the user's party, excepting those that have
        # fainted or have a {mechanic:major-status-effect}, attacks the
        # target.
        # Calculated stats are ignored; the base stats for the target
        # and assorted attackers are used instead.
        # The random factor in the damage formula is not used.
        # []{type:dark} Pokémon still get [STAB]{mechanic:stab}.
        modifiers /= random_modifier
        A = f1.stats.attack
        D = f2.stats.defense
        power = 40.

    elif effect == 100:
        # Inflicts [regular damage]{mechanic:regular-damage}.
        # Power varies inversely with the user's proportional remaining
        # [HP]{mechanic:hp}.
        #
        # 64 * current HP / max HP | Power
        # -----------------------: | ----:
        #  0– 1                    |  200
        #  2– 5                    |  150
        #  6–12                    |  100
        # 13–21                    |   80
        # 22–42                    |   40
        # 43–64                    |   20
        #
        # This table is not well-defined. Using the data from
        # https://bulbapedia.bulbagarden.net/wiki/Flail_(move)

        q = f1.current.hp / f1.stats.hp

        if q < 0.0417:
            power = 200

        elif q < 0.1042:
            power = 150

        elif q < 0.2083:
            power = 100

        elif q < 0.3542:
            power = 80

        elif q < 0.6875:
            power = 40

        else:
            power = 20

    elif effect == 122:
        # Inflicts [regular damage]{mechanic:regular-damage}.
        # Power increases with [happiness]{mechanic:happiness},
        # given by `happiness * 2 / 5`, to a maximum of 102.
        # Power bottoms out at 1.

        power = np.clip(a=f1.happiness * 2./5.,
                        a_max=102,
                        a_min=1)

    elif effect == 123:
        # Randomly uses one of the following effects.
        #
        # Effect                                             | Chance
        # -------------------------------------------------- | -----:
        # Inflicts {mechanic:regular-damage} with 40 power   |    40%
        # Inflicts {mechanic:regular-damage} with 80 power   |    30%
        # Inflicts {mechanic:regular-damage} with 120 power  |    10%
        # Heals the target for 1/4 its max {mechanic:hp}     |    20%

        q = uniform(0, 1)

        if q < .1:
            power = 120

        elif q < .4:
            power = 80

        elif q < .8:
            power = 40

        else:
            return -.25 * f2.stats.hp

    elif effect == 124:
        # Inflicts {mechanic:regular-damage}.
        # Power increases inversely with {mechanic:happiness}, given by
        # `(255 - happiness) * 2 / 5`, to a maximum of 102.
        # Power bottoms out at 1.

        power = np.clip(a=(255-f1.happiness) * 2./5.,
                        a_max=102,
                        a_min=1)

    elif effect == 127:
        # Inflicts [regular damage]{mechanic:regular-damage}.
        # Power is selected at random between 10 and 150, with an
        # average of 71:
        #
        # Magnitude | Power | Chance
        # --------: | ----: | -----:
        #         4 |    10 |     5%
        #         5 |    30 |    10%
        #         6 |    50 |    20%
        #         7 |    70 |    30%
        #         8 |    90 |    20%
        #         9 |   110 |    10%
        #        10 |   150 |     5%
        #
        # This move has double power against Pokémon currently
        # underground due to {move:dig}.

        q = uniform(0, 1)

        if q < .05:
            power = 10

        elif q < .15:
            power = 30

        elif q < .35:
            power = 50

        elif q < .65:
            power = 70

        elif q < .85:
            power = 90

        elif q < .95:
            power = 110

        else:
            power = 150

        if 'underground' in f2.status:
            power *= 2

    elif effect == 162:
        # Inflicts [regular damage]{mechanic:regular-damage}.
        # Power is equal to 100 times the amount of energy stored by
        # []{move:stockpile}.
        # XXX: Ignores the random factor in the damage formula.
        # Stored energy is consumed, and the user's {mechanic:defense}
        # and [Special Defense]{mechanic:special-defense} are reset to
        # what they would be if []{move:stockpile} had not been used.
        # If the user has no energy stored, this move will
        # {mechanic:fail}.
        # XXX: pass

        if 'stockpile' in f1.flags:
            energy = f1.flags.pop('stockpile')
            power = energy * 100.
            A = f1.flags.pop('defense_at_stockpile')
            D = f1.flags.pop('specialDefense_at_stockpile')

        else:
            power = 0

        modifiers /= random_modifier

    elif effect == 197:
        # Inflicts [regular damage]{mechanic:regular-damage}.
        # Power increases with the target's weight in kilograms, to a
        # maximum of 120.
        #
        # Target's weight | Power
        # --------------- | ----:
        # Up to 10kg      |    20
        # Up to 25kg      |    40
        # Up to 50kg      |    60
        # Up to 100kg     |    80
        # Up to 200kg     |   100
        # Above 200kg     |   120

        w = f2.weight

        if w <= 10:
            power = 20

        elif w <= 25:
            power = 40

        elif w <= 50:
            power = 60

        elif w <= 100:
            power = 80

        elif w <= 200:
            power = 100

        else:
            power = 120

    elif effect == 220:
        # Inflicts [regular damage]{mechanic:regular-damage}.
        # Power increases with the target's current {mechanic:speed}
        # compared to the user, given by
        # `1 + 25 * target Speed / user Speed`, capped at 150.

        power = np.clip(a=(1 + 25. * f2.current.speed/f1.current.speed),
                        a_max=150,
                        a_min=0)

    elif effect == 223:
        # Inflicts [regular damage]{mechanic:regular-damage}.
        # Power and type are determined by the user's held berry.
        # The berry is consumed.  If the user is not holding a berry,
        # this move will [fail]{mechanic:fail}.

        # The relevant info is stored in
        # `data/csv/custom/move_natural_gift.csv`.

        __cond = move_natural_gift["item_id"] == f1.item.id

        if __cond.any():
            # If there is at least one match
            __subset = move_natural_gift[__cond]
            m1.type = __subset["type_id"].values[0]

            power = __subset["power"].values[0]

            f1.item = Item(0)

        else:
            power = 0

    elif effect == 234:
        # Inflicts [regular damage]{mechanic:regular-damage}.
        # Power and type are determined by the user's
        # {mechanic:held-item}. The item is consumed.
        # If the user is not holding an item, or its item has no set
        # type and power, this move will [fail]{mechanic:fail}.
        #
        # This move ignores []{ability:sticky-hold}.
        #
        # If the user is under the effect of []{move:embargo},
        # this move will [fail]{mechanic:fail}.

        if 'embargo' not in f1.status:

            f1.item.flingat(f2)
            # Item().fling(target) activates the fling_effect to
            # the given `target`.
            # XXX: this method is incomplete. See item.py

            power = f1.item.fling.power

        else:
            power = 0

    elif effect == 236:
        # Inflicts [regular damage]{mechanic:regular-damage}.
        # Power is determined by the [PP]{mechanic:pp} remaining for
        # this move, after its [PP]{mechanic:pp} cost is deducted.
        # XXX: Ignores {mechanic:accuracy} and {mechanic:evasion} modifiers.
        #
        # PP remaining | Power
        # ------------ | ----:
        # 4 or more    |    40
        # 3            |    50
        # 2            |    60
        # 1            |    80
        # 0            |   200
        #
        # XXX: if this move is activated by another move, the activating
        # move's [PP]{mechanic:pp} is used to calculate power.

        pp = m1.pp - 1

        if pp >= 4:
            power = 40

        elif pp == 3:
            power = 50

        elif pp == 2:
            power = 60

        elif pp == 1:
            power = 80

        else:
            power = 200

    elif effect == 238:
        # Inflicts [regular damage]{mechanic:regular-damage}.
        # Power directly relates to the target's relative remaining
        # [HP]{mechanic:hp}, given by
        # `1 + 120 * current HP / max HP`,
        # to a maximum of 121.

        power = np.clip(a=(1. + 120. * f1.current.hp/f1.stats.hp),
                        a_max=121,
                        a_min=0)

    elif effect == 242:
        # If the target has selected a damaging move this turn, the
        # user will copy that move and use it against the target, with
        # a 50% increase in power.
        #
        # If the target moves before the user, this move will
        # [fail]{mechanic:fail}.
        #
        # This move cannot be copied by []{move:mirror-move}, nor
        # selected by []{move:assist}, []{move:metronome}, or
        # []{move:sleep-talk}.

        if f1.order == 2 and m2.damage_class_id != 1:
            power = m2.power * 1.5
            m1.type = m2.type
        else:
            power = 0

    elif effect == 246:
        # Inflicts [regular damage]{mechanic:regular-damage}.
        # Power starts at 60 and is increased by 20 for every
        # [stage]{mechanic:stage} any of the target's stats has been
        # raised, capping at 200.  [Accuracy]{mechanic:accuracy} and
        # [evasion]{mechanic:evasion} modifiers do not increase this
        # move's power.

        # Counting **only** stat increases.

        power = np.clip(a=f2.history.stage * 20 + 60,
                        a_max=200,
                        a_min=0)

    elif effect == 292:
        # Inflicts [regular damage]{mechanic:regular-damage}.
        # The greater the user's weight compared to the target's,
        # the higher power this move has, to a maximum of 120.
        #
        # User's weight                    | Power
        # -------------------------------- | ----:
        # Up to 2× the target's weight     |    40
        # Up to 3× the target's weight     |    60
        # Up to 4× the target's weight     |    80
        # Up to 5× the target's weight     |   100
        # More than 5× the target's weight |   120

        r = f1.weight/f2.weight

        if r <= 2:
            power = 40

        elif r <= 3:
            power = 60

        elif r <= 4:
            power = 80

        elif r <= 5:
            power = 100

        else:
            power = 120

    else:
        # All cases up to Gen.5 should be covered.
        power = m1.power

    base_damage = (2 + (2 * (f1.level/5 + 1) * power * A/D) // 50) * modifiers

    if not np.isnan(m1.min_hits):
        # If the move hits multiple times.
        # XXX: in the actual game, the critical modifier is determined
        # every time the move makes a hit.
        return base_damage * choice(np.arange(m1.min_hits,
                                              m1.max_hits+1))
    else:
        return base_damage


def calculate_damage(f1, m1, f2, m2):
    """Calculate the damage including the moves dealing direct damages
    and regular damages.
    """
    effect = m1.effect_id

    def immuned(damage):
        """A simple filter for damage that takes type-immunity into
        account.
        """
        return 0 if efficacy(m1.type, f2.types) == 0 else damage

    if effect == 27:
        # User waits for two turns.
        # On the second turn, the user inflicts twice the damage it
        # accumulated on the last Pokémon to hit it.  Damage inflicted
        # is [typeless]{mechanic:typeless}.
        #
        # This move cannot be selected by []{move:sleep-talk}.
        # XXX: group moves with `charge` flag into a new function.
        f1.flags += Status('bide', 2)
        return 0

    elif effect == 41:
        # Inflicts [typeless]{mechanic:typeless} damage equal to half
        # the target's remaining [HP]{mechanic:hp}.
        return f2.current.hp/2.

    elif effect == 42:
        # Inflicts 40 points of damage.
        return immuned(40.)

    elif effect == 88:
        # Inflicts damage equal to the user's level.  Type immunity
        # applies, but other type effects are ignored.
        return immuned(f1.level)

    elif effect == 89:
        # Inflicts [typeless]{mechanic:typeless} damage between 50% and
        # 150% of the user's level, selected at random in increments of
        # 10%.
        return f1.level * randint(5, 15)/10.

    elif effect == 90:
        # Targets the last opposing Pokémon to hit the user with a
        # physical move this turn.
        # Inflicts twice the damage that move did to the user.
        # If there is no eligible target, this move will fail.
        # Type immunity applies, but other type effects are ignored.

        if f1.order == 2:
            received_damage = f1.history.damage[0]
            if m2.damage_class_id == 2:
                return immuned(received_damage * 2)

        return 0

    elif effect == 131:
        # Inflicts exactly 20 damage.
        return immuned(20.)

    elif effect == 145:
        # Targets the last opposing Pokémon to hit the user with a
        # [special]{mechanic:special} move this turn.
        # Inflicts twice the damage that move did to the user.
        # If there is no eligible target, this move will
        # [fail]{mechanic:fail}.
        # Type immunity applies, but other type effects are ignored.

        if f1.order == 2:
            received_damage = f1.history.damage[0]
            if received_damage and m2.damage_class_id == 3:
                return immuned(received_damage * 2)

        return 0

    elif effect == 155:
        # Inflicts {mechanic:typeless} {mechanic:regular-damage}.
        # Every Pokémon in the user's party, excepting those that have
        # fainted or have a {mechanic:major-status-effect}, attacks the
        # target.
        # Calculated stats are ignored; the base stats for the target
        # and assorted attackers are used instead.
        # The random factor in the damage formula is not used.
        # []{type:dark} Pokémon still get [STAB]{mechanic:stab}.

        damage = 0
        for pokemon in f1.trainer.party():
            if pokemon.status.volatile.all():
                damage += regular_damage(pokemon, m1, f2, m2)
        return damage

    elif effect == 190:
        # Inflicts exactly enough damage to lower the target's
        # {mechanic:hp} to equal the user's.  If the target's HP is not
        # higher than the user's, this move has no effect.
        # Type immunity applies, but other type effects are ignored.
        # This effect counts as damage for moves that respond to damage.
        return immuned(np.clip(a=f2.current.hp - f1.current.hp,
                               a_min=0,
                               a_max=f2.current.hp))

    elif effect == 228:
        # Targets the last opposing Pokémon to hit the user with a
        # damaging move this turn.
        # Inflicts 1.5× the damage that move did to the user.
        # If there is no eligible target, this move will fail.
        # Type immunity applies, but other type effects are ignored.

        if f1.order == 2:
            received_damage = f1.history.damage[0]
            if m2.damage_class_id != 1:
                return immuned(received_damage * 1.5)

        return 0.

    elif effect == 321:
        # Inflicts damage equal to the user's remaining
        # [HP]{mechanic:hp}.  User faints.

        damage = f1.current.hp
        f1.current.hp = 0

        return damage

    else:
        # All cases up to Gen.5 should be covered.
        return regular_damage(f1, m1, f2, m2)


def stat_changer(f1, m1, f2, m2):
    """Activates m1's effects if it is **stat-change related**.

    The target is dependent upon m1's ``target_id``.
    """

    effect = m1.effect_id

    def whose_stat(p):
        """Changes p's stats."""
        chance = m1.effect_chance

        if np.isnan(chance):
            chance = 100.

        if binomial(1, chance/100.):
            for i, name in enumerate(p.CURRENT_STAT_NAMES):
                if i + 1 in m1.stat_change.stat_id:

                    change = m1.stat_change.change[i+1]
                    p.stage[name] += change

                    if i + 1 not in [7, 8] and change > 0:
                        # exclude accuracy and evasion.
                        p.history.stage += change

    if effect == 340:  # also effect 351
        # Raises the Attack and Special Attack of all []{type:grass}
        # Pokémon in battle.
        if 12 in f1.types:
            whose_stat(f1)

        if 12 in f2.types:
            whose_stat(f2)

    if m1.target_id in [3, 7, 13]:
        # Stats changes to the user.
        whose_stat(f1)

    elif m1.target_id in [9, 10, 11]:
        # Stats changes to the opponent.
        whose_stat(f2)


def ailment_inflictor(f1, m1, f2, m2):
    """Inflicts ailment to the selected target."""

    ailment_id = m1.meta_ailment_id
    ailment_chance = 100. if np.isnan(m1.ailment_chance) else m1.ailment_chance
    lasting_turns = None if np.isnan(m1.min_turns) else randint(m1.min_turns,
                                                                m1.max_turns+1)
    ailment = Status(ailment_id, lasting_turns)

    if binomial(1, ailment_chance/100.):
        if m1.target_id == 7:
            # Self-inflicted ailment
            f1.status += ailment
            if m1.effect == 38:
                # User sleeps for two turns, completely healing itself.
                # At the beginning of each round, ``is_mobile()``
                # should check if 'rest' is in ``f1.flags`` and if
                # 'sleep' is **not** in ``f1.status``. If both are
                # ``True``, then that means the user once slept and now
                # 'sleep' status has worn off.
                # Then restore all user's current hp. Heal the user and
                # remove the flag.

                f1.flags['rest'] = True

        elif m1.target_id == 14:
            # ailment inflicted to all pokemons.
            f1.status += ailment
            f2.status += ailment

        else:
            # ailment inflicted to the opponent
            f2.status += ailment


def status_damage(f1):
    """Takes the damage if the pokemon has certain statuses. The damage
    is effect **at the end of the turn**.
    """
    # XXX: add berries effects

    if 'burn' in f1.status and f1.ability != 'guts':
        f1.current.hp -= f1.stats.hp // 8.

    if {'poison', 'leech-seed'} & set(f1.status):

        f1.current.hp -= f1.stats.hp // 8.

    if {'ingrain', 'aqua-ring'} & set(f1.status):

        recovery = f1.stats.hp // 16.

        if f1.item.name == 'big-root':
            recovery = np.f1loor(1.3 * recovery)

        f1.current.hp += recovery

    if {'nightmare', 'sleep'} <= set(f1.status) or 'curse' in f1.status:

        f1.current.hp -= f1.stats.hp // 4.

    if 'trap' in f1.status:

        damage = f1.stats.hp // 16.

        if f1.item.name == 'binding-band':
            damage *= 2.

        f1.current.hp -= damage


def effect(f1, m1, f2, m2):
    """Activates m1's effect if it is a unique effect.

    Exceptions
    ----------
        Move id     | Effect id
       -------------|-----------
         18, 46     |   29
         54         |   47
         100        |   154
         113        |   36


    """

    effect = m1.effect_id
    if not np.isnan(m1.healing):
        # A positive heal cures the user; a negative heal damages
        # the user, based on the user's max hp.
        f1.current.hp += m1.healing * f1.stats.hp // 100.

    if not np.isnan(m1.flinch_chance) and f2.order == 2:  # oxymoron?
        # If the move makes the opponent flinch, then add `flinch`
        # to the opponent's status.
        if binomial(1, m1.flinch_chance/100.):
            f2.status += Status('flinch', 1)

    if not str(m1.stat_change).isnumeric():
        # stat-changers
        stat_changer(f1, m1, f2, m2)

    if m1.meta_category_id in[1, 5]:
        # moves that inflicts status conditions.
        ailment_inflictor(f1, m1, f2, m2)

    if effect == 26:
        # Removes [stat]{mechanic:stat}, [accuracy]{mechanic:accuracy},
        # and [evasion]{mechanic:evasion} modifiers from every Pokémon
        # on the [field]{mechanic:field}.
        #
        # This does not count as a stat reduction for the purposes of
        # []{ability:clear-body} or []{ability:white-smoke}.
        for f in [f1, f2]:
            for stat in f.STAT_NAMES:
                f.current[stat] = f.stats[stat]
            for stat in ['accuracy', 'evasion']:
                f.current[stat] = 100.

    elif effect == 58:
        # User copies the target's species, weight, type,
        # [ability]{mechanic:ability}, [calculated stats]{mechanic:
        # calculated-stats} (except [HP]{mechanic:hp}), and moves.
        # Copied moves will all have 5 [PP]{mechanic:pp} remaining.
        # [IV]{mechanic:iv}s are copied for the purposes of []{move:
        # hidden-power}, but stats are not recalculated.
        #
        # []{item:choice-band}, []{item:choice-scarf}, and []{item:
        # choice-specs} stay in effect, and the user must select a new
        # move.
        #
        # This move cannot be copied by []{move:mirror-move}, nor forced
        # by []{move:encore}.
        pass  # XXX: passed.

    elif effect == 83:
        # This move is replaced by the target's last successfully used
        # move, and its PP changes to 5.  If the target hasn't used a
        # move since entering the field, if it tried to use a move this
        # turn and [failed]{mechanic:fail}, or if the user already knows
        # the targeted move, this move will fail.  This effect vanishes
        # when the user leaves the field.
        #
        # If []{move:chatter}, []{move:metronome}, []{move:mimic},
        # []{move:sketch}, or []{move:struggle} is selected, this move
        # will [fail]{mechanic:fail}.
        #
        # This move cannot be copied by []{move:mirror-move}, nor
        # selected by []{move:assist} or []{move:metronome}, nor forced
        # by []{move:encore}.
        if 'last-successfully-used-move' in f2.flags:
            m1 = Move(f2.flags['last-successfully-used-move'])
            m1.pp = 5

    elif effect == 84:
        # Selects any move at random and uses it.
        # Moves the user already knows are not eligible.
        # Assist, meta, protection, and reflection moves are also not
        # eligible; specifically, []{move:assist}, []{move:chatter},
        # []{move:copycat}, []{move:counter}, []{move:covet},
        # []{move:destiny-bond}, []{move:detect}, []{move:endure},
        # []{move:feint}, []{move:focus-punch}, []{move:follow-me},
        # []{move:helping-hand}, []{move:me-first}, []{move:metronome},
        # []]{move:mimic}, []{move:mirror-coat}, []{move:mirror-move},
        # []{move:protect}, []{move:quick-guard}, []{move:sketch},
        # []{move:sleep-talk}, []{move:snatch}, []{move:struggle},
        # []{move:switcheroo}, []{move:thief}, []{move:trick}, and
        # []{move:wide-guard} will not be selected by this move.
        #
        # This move cannot be copied by []{move:mimic} or
        # []{move:mirror-move}, nor selected by []{move:assist},
        # []{move:metronome}, or []{move:sleep-talk}.

        ineligible_moves = deque([x.name for x in f1.moves])
        ineligible_moves.extend(['assist', 'chatter', 'copycat', 'counter',
                                 'covet', 'destiny-bond', 'detect', 'endure',
                                 'feint', 'focus-punch', 'follow-me',
                                 'helping-hand', 'me-first', 'metronome',
                                 'mimic', 'mirror-coat', 'mirror-move',
                                 'protect', 'quick-guard', 'sketch',
                                 'sleep-talk', 'snatch', 'struggle',
                                 'switcheroo', 'thief', 'trick', 'wide-guard'])

        all_moves = deque([x for x in tb.moves.identifier.values])
        eligible_moves = list(set(all_moves) - set(ineligible_moves))
        m1 = np.random.choice(eligible_moves)

    elif effect == 95:
        # If the user targets the same target again before the end of
        # the next turn, the move it uses is guaranteed to hit.
        # This move itself also ignores [accuracy]{mechanic:accuracy}
        # and [evasion]{mechanic:evasion} modifiers.
        #
        # One-hit KO moves are also guaranteed to hit, as long as the
        # user is equal or higher level than the target.  This effect
        # also allows the user to hit Pokémon that are off the field
        # due to moves such as []{move:dig} or []{move:fly}.
        #
        # If the target uses []{move:detect} or []{move:protect} while
        # under the effect of this move, the user is not guaranteed to
        # hit, but has a (100 - accuracy)% chance to break through the
        # protection.
        #
        # This effect is passed on by []{move:baton-pass}.

        # XXX: finish its counterpart in ``makes_hit``
        f2.status += Status('taking-aim', 2)

    elif effect == 101:
        # Lowers the PP of the target's last used move by 4.
        # If the target hasn't used a move since entering the [field]
        # {mechanic:field}, if it tried to use a move this turn and
        # [failed]{mechanic:failed}, or if its last used move has 0 PP
        # remaining, this move will fail.

        move_names = [x.name for x in f2.moves]
        try:
            last_move = f2.flags['last-successfully-used-move']
            index = np.where(move_names == last_move)[0][0]
            f2.moves[index].pp -= 4
        except KeyError:
            pass

    elif effect == 112:
        pass


# Order, move, and item should be determined before calling this function.
def attack(f1, m1, f2, m2):
    """f1 uses m1 to attack f2.

    Given f1 is mobile. Given f1 attacks first.

    Moves with different meta-categories have different behaviors.
    There are 14 different meta-categories according to veekun.com.

    Chekcing order:
        direct damage
        other damage
    """

    if makes_hit(f1, m1, f2):
        # Determine if the move is hit or not.

        f1.flags['last-successfully-used-move'] = m1.id
        if m1.damage_class_id in [2, 3]:
            # For all moves that deal damage.
            # `direct_damage` checks if a move deals direct damage,
            # and if not, then returns the regular damage.

            damage = np.floor(calculate_damage(f1, m1, f2, m2))

            # print("{} dealt {} to {}!\n".format(f1.name, damage, f2.name))

            if 'burn' in f1.status and m1.damage_class_id == 2:
                # if the attacker is burned and the move is a physical
                # move, the damage is halved.
                damage *= 0.5

            f2.current.hp -= damage
            # if this number is negative, then the move heals the
            # opponent.

            f2.history.damage.appendleft(damage)

            if not np.isnan(m1.drain):
                # A negative drain means a recoil damage.
                # A positive drain means absorbing from the opponent.
                f1.current.hp += m1.drain * damage // 100.
        else:
            # Append 0 if no damage is dealt.
            f2.history.damage.appendleft(0)

        effect(f1, m1, f2, m2)
        m1.pp -= 1
        status_damage(f1)

    else:
        pass
