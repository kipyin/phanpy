#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 14:22:39 2017

@author: Kip
"""

from numpy.random import binomial


def priorities(p1, p1_move, p2, p2_move):
    """Determines the order of attack.

    Need to take effects into account, e.g. trick-room, quick-claw.
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

    __absolutely_immobile = ['freeze', 'flinch', 'semi-invulnerable',
                             'taking-in-sunlight', 'withdrawing']

    for status in __absolutely_immobile:
        # Cases where `f` surely immobile:
        if status in statuses:
            return False
    else:
        # Cases where `f` is conditionally immobile:
        if 'paralysis' in statuses:
            return bool(binomial(1, 0.25))

        elif 'infatuation' in statuses:
            return bool(binomial(1, 0.5))

        elif (('sleep' in statuses) and
              (m.name not in ['sleep-talk', 'snore'])):
            return False

    return True


def attack(f1, m1, f2):
    """f1 uses m1 to attack f2.

    Given f1 is mobile. Given f1 attacks first.

    Moves with different meta-categories have different behaviors.
    There are 14 different meta-categories according to veekun.com.
    """


