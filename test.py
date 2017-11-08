#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import timeit as t

s = '''
import numpy as np
from mechanisms.main import order_of_attack, attack
from mechanisms.config import turn
from mechanisms.core.pokemon import Trainer, Pokemon
from mechanisms.core.move import Move

def test():

    iteration = 0

    while iteration < 6:

        red = Trainer('Red')
        green = Trainer('Green')
        turn = 1

        while turn <= 50:
            try:
                p1 = red.party(np.random.choice([1, 2, 3]))
                p2 = green.party(np.random.choice([1, 2, 3]))

                m1 = p1.moves[np.random.choice(np.arange(len(p1.moves)))]
                m2 = p2.moves[np.random.choice(np.arange(len(p2.moves)))]

                f1, m1, f2, m2 = order_of_attack(p1, m1, p2, m2)
                attack(f1, m1, f2, m2)
                turn += 1
            except Exception as e:
                raise Exception('Iteration: {}, Attacker: {}, Move: {},'
                                ' Effect: {}, '
                                'Exception: {}'.format(iteration,
                                                       p1.name, m1.name,
                                                       m1.effect_id, e))

        iteration += 1
'''


print(t.timeit('test()', setup=s, number=10))
