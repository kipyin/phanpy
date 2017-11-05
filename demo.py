#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 10:14:22 2017

@author: Kip
"""

import os
import sys

from collections import deque
import numpy as np
import pandas as pd

pkg_path = os.path.dirname(os.path.abspath(__file__))

if pkg_path not in sys.path:
    sys.path.append(pkg_path)

print(pkg_path)

from core.helpers import which_version, efficacy
from core.pokemon import Pokemon
from core.status import Status
from core.move import Move
import tables as tb


event_log = tb.event_log


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


def hit_rate(f1, m1, f2):
    """Some awesome hit rate explanations.
    """

    if not np.isnan(m1.accuracy) and m1.category_id != 9:

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
    elif m1.category_id == 9:

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

        if f1.held_item in tb.move_natural_gift.item_id.values:

            __index = tb.move_natural_gift["item_id"] == f1.held_item

            m1.power = tb.move_natural_gift[__index].power.values
            m1.type_id = tb.move_natural_gift[__index].type_id.values

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

    elif m1.category_id == 9:
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
        if ((4 in f1.status.id) and (f1.ability != 62) and
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
    if m1.category_id == 8:

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


def is_mobile(f):
    """Checks if the Pokémon `f` is able to move in this turn or not.

    Returns
    -------
        is_mobile : Boolean
            True if Pokémon `f` is able to make a move in this turn.
            Else, False.
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


def make_a_move(f1, m1, f2):
    """Some awesome damage calculation explanations.
    """
    global event
    print("{} uses {}!\n".format(f1.name, m1.name))

    # Everything that deals direct damage.
    if m1.category_id in [0, 4, 6, 7, 8, 9]:

        direct_damage(f1, m1, f2)

    # Moves that ail the *opponent* pokemon.
    if m1.category_id in [1, 4, 5]:

        if np.random.binomial(1, m1.ailment_chance/100) == 1:

            f2.status.ailment = m1.ailment_id

            __ailment = tb.ailments.loc[m1.ailment_id + 1, "identifier"]

            print("{} is {}!".format(f2.name, __ailment))

    # Moves that raises the user's stats
    if m1.category_id in [2, 7]:

        stat_changer(f1, m1)

    # Moves that lowers the opponent's stats
    # FIXME: add changes on `current.stats`.
    if m1.category_id in [5, 6]:

        stat_changer(f2, m1)

    # Moves that heals the user.
    if m1.category_id == 3:

        recovery = f1.stats.hp * (m1.healing/100 + 1)
        f1.current.hp = np.clip(a=recovery,
                                a_max=f1.stats.hp,
                                a_min=0)

        event["damage_to_self"] = -recovery
        print("{} has recovered health!".format(f1.name))


def battle(p1, m1, p2, m2):
    """Simulates a battle, given Pokémons and moves."""

    global round_num, event, turn_num

    def report():
        event_log.loc[turn_num] = event

    # Compare priorities. f1, f2 = first_hand, second_hand.
    # f1 always attacks first.
    f1, f2, m1, m2 = priorities(p1, m1, p2, m2)

    # --------------------- THE MAIN BATTLE ---------------------- #

    event["weather"] = 0

    # f1's turn. Uses m1.

    event["round"] = round_num
    event["order"] = 1
    event["pokemon_id"] = f1.id
    event["option"] = 'move'
    event["move_id"] = m1.id
    event["item_id"] = 0
    event["change_to_pokemon_id"] = 0

    if is_mobile(f1):
        make_a_move(f1, m1, f2)
    else:
        print("{} cannot move due to {}"
              "".format(f1.name, f1.status.ailment))
    report()
    event = empty_event()

    turn_num += 1

    if battle_finished(f1, f2):
        return

    # f2's turn. Uses m2.

    event["round"] = round_num
    event["order"] = 2
    event["pokemon_id"] = f2.id
    event["option"] = 'move'
    event["move_id"] = m2.id
    event["item_id"] = 0
    event["change_to_pokemon_id"] = 0

    if is_mobile(f2):

        make_a_move(f2, m2, f1)

    else:

        print("{} cannot move due to {}"
              "".format(f2.name, f2.status.ailment))
    report()
    event = empty_event()

    turn_num += 1

    if battle_finished(f1, f2):
        return


def main():
    """Single-battle Flow:
        Single Battle means each party chooses 1 Pokémon to participate
        in the battle. The party with no usable Pokémon loses.

        1. For each party:
            1.0 This party will (randomly) make a choice, where a choice
            is one of ["make_a_move", "use_an_item", "switch_pokemon"].

            1.1 If this party chooses to make a move, the program should
            first determine if one is able to use a move at all.
            Then, this party will (randomly/using an algorithm) choose
            which move to make. If all moves' PP is 0, then use the move
            "struggle".
            After this party has successfully chosen a move, end the
            turn.

            1.2 If this party chooses to use an item, choose which item
            to use. Then, if applicable, choose which Pokémon to
            apply the item.
            In the actual game, there is a possibility that using an
            item has no effect. In this case, the player is able to
            redo step 1. However, this should not happen in our program,
            hence we will ignore this possibility.
            The effect of the item kicks in immediately; the party
            does not need to wait for the other party to make a choice.
            Issue: Heal block?
            Once the item is applied, end the turn.

            1.3 If the party chooses to switch to another Pokémon, the
            program should first check if such a choice is legal
            (probably by defining a function called `switchable()` which
            checks the party's status).
            Once a choice is made, the switched Pokémon will receive
            any effect that it will possibly get due to some field
            effects. After the effects kick in, end the turn.

        2. The exact same process applies to the other party.

        3. After both parties have made their choices, the algorithm
        will determine if there is a battle or not.
        If the choices are any two of the following (with replacement):
            not able to make a move, using an item, switching to
            another Pokémon
        there will be no battle. Otherwise, do:
            battle(p1, m1, p2, m2)

        4. Once a battle has ended, go back to step #1.
    """
    global round_num, event, turn_num

    event = empty_event()

    PartyA = [Pokemon(np.random.randint(1, 493)) for x in range(6)]
    PartyB = [Pokemon(np.random.randint(1, 493)) for x in range(6)]

    p1 = PartyA[0]
    p2 = PartyB[0]

    print("A level {} {} fights a level {} {}!!"
          "".format(p1.level, p1.name, p2.level, p2.name))
    print("No.{} {}'s stats:\n{}\nmoves:\n{}\n"
          "".format(p1.id, p1.name, p1.stats, p1.moves))
    print("No.{} {}'s stats:\n{}\nmoves:\n{}\n"
          "".format(p2.id, p2.name, p2.stats, p2.moves))

    round_num = 1
    turn_num = 1

    while True:
        choiceA = 'move'
        if is_mobile(p1):
            m1 = p1.moves[np.random.randint(1, len(p1.moves))]

        choiceB = 'move'
        if is_mobile(p2):
            m2 = p2.moves[np.random.randint(1, len(p2.moves))]

        battle(p1, m1, p2, m2)
        round_num += 1

    # Who won?
    if p1.current.hp == 0:  # f2 wins.
        p2.ev += p1.effort
        print("{} has won!!".format(p2.name))
    else:  # f1 wins.
        p1.ev += p2.effort
        print("{} has won!!".format(p1.name))

    # After battle events

    p1.reset_current()
    p2.reset_current()


if __name__ == '__main__':
    main()
