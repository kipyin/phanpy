#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A simple user interface simulating Pokémon battles.

Currently only support 1-on-1 battle, and the Pokémons are limited
to Generation 3 & 4.
"""

from collections import OrderedDict
from os import path, sys, system
file_path = path.dirname(path.abspath(__file__))
root_path = file_path.replace('/phanpy', '')
sys.path.append(root_path) if root_path not in sys.path else None

import numpy as np

import phanpy.core.objects as ob
import phanpy.core.tables as tb
import phanpy.core.algorithms as al


def safe_input(msg, options=['y', 'n'], default=None):
    """Show up ``msg`` as long as the input is not in ``options``.

    If no ``default`` input is given, the first item in ``options``
    is used.

    Parameters
    ----------
    msg : str
        The displayed message.

    options : list
        A list of expected answers. Defaults to ['y', 'n'] if nothing is
        provided.

    default : str
        The default answer (when hitting 'Enter').

    Returns
    -------
    choice : str
        A value from ``options`` specified by the user.
    """
    if not default:
        default = options[0]

    choice = input(msg)
    if choice == '':
        choice = default

    while choice not in options:
        # If the options is a very long list, omit the details.
        if len(options) <= 5:

            # Separate the first few items from the last item.
            g1 = "', '".join(options[:-1])
            g2 = options[-1]
            choice = input("* Please enter either '{0}', or '{1}'. \n"
                           "{2}".format(g1, g2, msg))
            if choice == '':
                choice = default
        else:
            choice = input("* {0} is not a valid choice.\n"
                           "{1}".format(choice, msg))
    return choice


def config():
    """"Simulates a single round of game."""

    # load configuration?

    lang = 9

    # Game selection
    which_game = safe_input("Select a game:\n"
                            "[1]. FireRed/LeafGreen\n"
                            " 2 . Ruby/Sapphire/Emerald\n"
                            " 3 . Diamond/Pearl/Platinum\n"
                            ">>> ", ['1', '2', '3'])

    if which_game == '1':
        max_index = 151
        game_name = 'firered'

    elif which_game == '2':
        max_index = 386
        game_name = 'emerald'

    elif which_game in ['3']:
        max_index = 493
        game_name = 'platinum'

    tb.VERSION_GROUP_ID, tb.REGION_ID, tb.VERSION_ID = tb.which_version(game_name)

    # Pick a pokemon.
    # XXX: Pick opponent's pokemon
    random_pokemon = safe_input("Randomly select a Pokémon ([y]/n)? ")

    if random_pokemon == 'y':
        # If the user chooses to randomly select a Pokémon...

        user = ob.Pokemon(np.random.randint(1, max_index+1))
        ok = safe_input("Is No.{0.id} {0.name} ok ([y]/n)? ".format(user))

        while ok == 'n':
            user = ob.Pokemon(np.random.randint(1, max_index+1))
            ok = safe_input("Is No.{0.id} {0.name} ok ([y]/n)? ".format(user))

    elif random_pokemon == 'n':
        # If the user chooses to manually select a Pokémon...

        which_pokemon = input("Choose your Pokémon (you can enter either"
                              " the id or the name).\n>>> ")
        while True:
            # Ensure that a valid Pokémon is instantiated.

            try:
                # Instantiate the Pokémon if it is valid.
                if which_pokemon.isnumeric():
                    user = ob.Pokemon(int(which_pokemon))

                else:
                    user = ob.Pokemon(which_pokemon)

                # Give the user the option to confirm the choice.
                confirm = safe_input("Choose No.{0.id} {0.name} ([y]/n)? ".format(user))

                if confirm == 'y':
                    break

                else:
                    which_pokemon = input("Choose your Pokémon (you can enter either"
                                          " the id or the name).\n>>> ")
                    continue

            except KeyError:
                which_pokemon = input("Oops! '{}' is not a valid Pokémon.\n"
                                      "Choose again (remember, you can enter"
                                      " either the id or the name, but it "
                                      "has to be valid.\n>>> ".format(which_pokemon))
                continue

            break  # If a Pokémon is successfully instantiated, break out of the loop.

    # Option to randomly assgin moves.
    # When a Pokémon is instantiated, a random set of moves have already
    # been assigned. Choosing 'no' here will override these moves.
    random_moves = safe_input("Automatically assign moves for {0.name}"
                              " ([y]/n)? ".format(user))

    if random_moves == 'n':
        # If 'no' is chosen, present all learnable moves to the user,
        # and let the user manually set each move.

        print("Moves will be set manually.")

        template = "\n{:^5}|{:^15}|{:^6}|{:^6}|{:^40}"

        print(template.format("ID", "Move Name", "Power", "PP", "Effect"))
        print("{0:-^5}|{0:-^15}|{0:-^6}|{0:-^6}|{0:-^40}".format(""))

        mep = tb.move_effect_prose
        for i in set(sorted(user._all_moves)):
            # Print all learnable moves.

            m = ob.Move(i)

            condition = mep["move_effect_id"] == m.effect_id
            effect_prose = mep[condition]["short_effect"].values[0]
            effect_prose = effect_prose[:40]

            print("{0.id:^5}|{0.name:^15}|{0.power:^6}|{0.pp:^6}|"
                  "{1:<40}".format(m, effect_prose))

        # ordinal(n) converts a number to its ordinal form.
        # i.e. ordinal(1) == '1st', ordinal(2) == '2nd', etc.
        # Copied from https://stackoverflow.com/a/20007730/8902117
        ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])

        move_list = []

        for i in range(1, 5):
            # Set moves from the presented list.
            options = list(map(str, user._all_moves))
            move_id = safe_input("Set the {0} move: "
                                 "".format(ordinal(i)),
                                 options)

            while int(move_id) in move_list:
                move_id = safe_input("{2.name} already knows {1.name} ({1.id})!\n"
                                     "Set the {0} move: "
                                     "".format(ordinal(i), ob.Move(int(move_id)), user),
                                     options)

            move_list.append(int(move_id))

            print("{0.name}'s {1} move {2.name} ({2.id}) is set."
                  "".format(user, ordinal(i), ob.Move(int(move_id))))

        for i in range(4):
            user.moves[i] = ob.Move(move_list[i])

    op = ob.Pokemon(np.random.randint(1, max_index + 1))

    # Save this configuration?


    return user, op


def battle():
    """Simulate a battle."""

    user, op = config()

    def fight():
        """Fight"""

        choice = None

        while choice != 'q':

            print("Enter 'q' to go back.")

            for i, move in enumerate(user.moves, 1):
                print("{0} | {1.name:^20} | {1.power:^5} | {1.pp:^4} | {1.type:^2}".format(i, move))

            choice = input("Which move? ")

            if choice in [str(x) for x in range(1, len(user.moves)+1)]:
                choice = int(choice)
                user_move = user.moves[choice-1]
                break

            else:
                print("Invalid move. Choose again.")

        # Pick a move for the opponent, and run the main algorithm.
        op_move = op.moves[np.random.randint(len(op.moves))]

        f1, m1, f2, m2 = al.attacking_order(user, user_move, op, op_move)

        for (f, m, g, n) in zip([f1, f2], [m1, m2], [f2, f1], [m2, m1]):

            if al.is_mobile(f, m):
                print("{} uses {}!".format(f.name, m.name))
                al.attack(f, m, g, n)

        f1.status.reduce()
        f2.status.reduce()

    def switch():
        """Switch"""
        pass

    def bag():
        """Bag"""
        pass

    def run():
        """Run"""
        pass


    menu = OrderedDict([
        ('f', fight),
        ('s', switch),
        ('b', bag),
        ('r', run)
    ])

    def on_display(user, op):
        """Return a formatted string which contains the user's and the
        opponent's HP.

        """
        display = ("User:     [{0.status}] No.{0.id} {0.name}'s HP: {0.current.hp} / {0.stats.hp}\n"
                   "Opponent: [{1.status}] No.{1.id} {1.name}'s HP: {1.current.hp} / {1.stats.hp}"
                   "".format(user, op))

        return display

    auto_battle = safe_input("Battle automatically ([y]/n)? ")

    if auto_battle == 'y':
        print("Auto-battle enabled.")

    elif auto_battle == 'n':
        print("Auto-battle disabled.")

        choice = None
        while choice != 'q':

            print(on_display(user, op))
            print("Enter 'q' to quit.")

            for key, value in menu.items():
                print('{}) {}'.format(key, value.__doc__))

            choice = input('Action: ').lower().strip()

            if choice in menu:
                menu[choice]()

battle()



# This is a script I copied from the original 'main.py' as a reference
def debug(player=None, ai=None, display=True):
    """A quick prototype that simulates a battle. `player` and `ai` are
    both Trainer objects.
    Set `display` to False shut all display up.
    """

    from phanpy.core.pokemon import Trainer

    if not ai:
        # If the ai's pokemon is not specified, then randomize one
        ai = ob.Trainer('Shigeru')

    if not player:
        player = ob.Trainer('Satoshi')

    p1 = player.party(1)
    p2 = ai.party(1)

    if display:
        for (u, p) in zip([player, ai], [p1, p2]):
            print("{} chooses No.{} {}!\n".format(u.name, p.id, p.name),
                  "{}'s hp: {}\n".format(p.name, p.stats.hp))

    end = False

    turn = 1

    while not end:
        m1 = p1.moves[randint(0, len(p1.moves))]
        m2 = p2.moves[randint(0, len(p2.moves))]

        f1, m1, f2, m2 = attacking_order(p1, m1, p2, m2)

        if display:
            print("==============================")

        for (f, m, g, n) in zip([f1, f2], [m1, m2], [f2, f1], [m2, m1]):

            if is_mobile(f, m):
                if display:
                    print("{} uses {}!\n".format(f.name, m.name))
                    print("The move {}'s info:\n"
                          "Power: {}, Accuracy: {}\n".format(m.name,
                                                             m.power,
                                                             m.accuracy))
                attack(f, m, g, n)
                # print(g.history)
                if display:
                    print("{}'s hp: {}\n"
                          "{}'s hp: {}\n".format(f.name, f.current.hp,
                                                 g.name, g.current.hp))
            elif display:
                print("{} cannot use the move!\n".format(f.name))
                continue

            if f2.current.hp <= 0 or f1.current.hp <= 0:
                # 0 indicates that one side is fainting and the current
                # round is ended.
                if display:
                    print("The battle has ended")
                end = True
                break

        f1.status.reduce()
        f2.status.reduce()
        turn += 1


def test(n, d=True):
    for i in range(n):
        debug(display=d)


# test(10, False)
