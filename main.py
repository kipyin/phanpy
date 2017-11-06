#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 14:22:39 2017

@author: Kip
"""

import numpy as np
from numpy.random import binomial


def priorities(p1, p1_move, p2, p2_move):
    """Determines the order of attack.

    # FIXME: need to take effects into account, e.g.
    trick-room, quick-claw.
    """

    if p1_move.priority > p2_move.priority:
        # If the moves' priorities are different, use the moves'
        # prioirties.
        f1, f2, m1, m2 = p1, p2, p1_move, p2_move

    elif p1_move.priority < p2_move.priority:
        f1, f2, m1, m2 = p2, p1, p2_move, p1_move

    else:
        # If the moves' priorities are the same, determine the
        # priorities based on the Pokémons' speeds.
        if p1.current.speed >= p2.current.speed:
            f1, f2, m1, m2 = p1, p2, p1_move, p2_move
        else:
            f1, f2, m1, m2 = p2, p1, p2_move, p1_move

    return f1, f2, m1, m2


def is_mobile(f, m):
    """Checks if a pokemon is able to make a move in this turn or not.

    Not be able to move if suffer from:
        {status: freeze},
        {status: sleep} (unless the move is 'sleep-talk' or 'snore'),
        {status: paralysis} (w.p. 0.25),
        {status: flinch} (need to be added to `status.py` and
            `move_meta_ailments.csv`),
        {status: infatuation} (w.p. 0.5),
        {status: semi-invulnerable} (need to be added to
            `move_meta_ailments.csv`),
        {status: taking-in-sunlight} (need to be added),
        {status: withdrawing} (need to be added).
    """

    statuses = f.status.name

    __absolutely_immobile = {'flinch', 'taking-in-sunlight', 'withdrawing'}

    if __absolutely_immobile & set(statuses):
        # Cases where `f` is surely immobile
        return False

    elif f.status.semi_invulnerable:
        # If `f` is semi-invulnerable, it cannot move.
        return False

    else:
        # Cases where `f` is conditionally immobile:
        if 'paralysis' in statuses:
            return bool(binomial(1., 0.25))

        elif 'infatuation' in statuses:
            return bool(binomial(1., 0.5))

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

    return True


def hit_indicator(f1, m1, f2):
    """Returns 1 if a move is hit else 0."""

    if 'taking-aim' in f2.status.name:
        # If the target has been aimed at in the previous turn, the
        # attacker's move will not miss. 'taking-aim' should be have a
        # life time of 1.
        # Moves that induce 'taking-aim' status are 'mind-reader' and
        # 'lock-on'.
        return 1

    elif f2.status.semi_invulnerable:
        # FIXME: best way to do this? This works.
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
            return 0

    if not np.isnan(m1.accuracy):
        # If the move's accuracy is not nan, use the regular hit rate
        # formula P = move's accuracy * user's accuracy / opponent's
        # evasion.
        pr = m1.accuracy/100. * f1.stage_facotr.accuracy/f2.stage_factor.evasion
        return binomial(1., pr)

    elif m1.effect_id == 18:
        # If the move never misses
        return 1




def attack(f1, m1, f2):
    """f1 uses m1 to attack f2.

    Given f1 is mobile. Given f1 attacks first.

    Moves with different meta-categories have different behaviors.
    There are 14 different meta-categories according to veekun.com.
    """

    # Determine if the move is hit or not.

    if m1.meta_category_id in [0, 4, 6, 7, 8]:
        pass
