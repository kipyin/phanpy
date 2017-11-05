# [WIP] pokemon-battle-mechanisms
The battle mechanisms for Pokémon games.

## Package Overview
This section explains the functionality of each module in this package.

* `./data/csv/`

(Almost) all data come from here. The data is provided by veekun:

<https://github.com/veekun/pokedex.git>

There is also a `custom` folder among the csv files. Files in this

folder is all created my me, to make up for some missing pieces.

* `helpers.py`

This contains all functions that I do not know where to put. Let me

know if you have any suggestions.

* `tables.py`



This module imports all relative tables.

## Full Battle Flow

Each party chooses 1 Pokémon to participate in the battle. The party with no usable Pokémon loses.

1. For each party:

    .0 This party will (randomly) make a choice, where a choice is one of

        ["make_a_move", "use_an_item", "switch_pokemon"].

    .1 If this party chooses to make a move, the program should first determine if one is able to use a move at all.

    Then, this party will (randomly/using an algorithm) choose which move to make. If all moves' PP is 0, then use the move "struggle".

    After this party has successfully chosen a move, end the turn.

    .2 If this party chooses to use an item, choose which item to use. Then, if applicable, choose which Pokémon to apply the item.

    In the actual game, there is a possibility that using an item has no effect. In this case, the player is able to redo step 1. However, this should not happen in our program, hence we will ignore this possibility.

    The effect of the item kicks in immediately; the party does not need to wait for the other party to make a choice.

    **Issue**: Heal block?

    Once the item is applied, end the turn.

    .3 If the party chooses to switch to another Pokémon, the program should first check if such a choice is legal (probably by defining a function called `switchable()` which checks the party's status).

    Once a choice is made, the switched Pokémon will receive any effect that it will possibly get due to some field effects. After the effects kick in, end the turn.

2. The exact same process applies to the other party.

3. After both parties have made their choices, the algorithm will determine if there is a battle or not.

If the choices are any two of the following (with replacement):

    not able to make a move, using an item, switching to another Pokémon

there will be no battle. Otherwise, do:

    battle(p1, m1, p2, m2)

4. Once a battle has ended, go back to step 1.

