# pokemon-battle-mechanisms
The battle mechanisms for Pokémon games.

## Package Overview
This section explains the functionality of each module in this package.

* `./data/csv/`
(Almost) all data come from here. The data is provided by veekun:

<https://github.com/veekun/pokedex.git>

There is also a `custom` folder among the csv files. Files in this
folder is all created my me, to make up for some missing pieces.

* `assistive_function.py`
This contains all functions that I do not know where to put. It include:

    1. `efficacy(atk_type, tar_types)` computes the type effectiveness
    of `atk_type` against `tar_types` (`0x`, `0.25x`, `0.5x`,
    `1x`, `1.5x`, `2x`), where `atk_type` is an `int` and `tar_types`
    can be a list of `int`'s.

* `tables.py`
This module imports all relative tables.

