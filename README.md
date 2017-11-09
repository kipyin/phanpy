# [WIP] pokemon-battle-mechanisms

The battle mechanisms for Pokémon games.

Required package:

- [ ] `pandas`

## Project Overview

The goal of this project is to reverse-engineer the turn-based Pokémon battle in the main series.
While eventually I'm hoping to cover all 7
generations of the main series games, generations 3 and 4 are at the top of the list, since many of the game designs have changed when generation 3 (Ruby and Sapphire) was released.

## Battle Style

The battle style this project is aiming at is much like that of the 3-on-3 single battle at [the Battle Tower](https://bulbapedia.bulbagarden.net/wiki/Battle_Tower_(Generation_III) ), where each player chooses 3 Pokemons with the same level at random. This battle style greatly reduces the number of variables, while retaining the important feature in the games.
The following features have been exempted from the battle:

- experience
- evolution
- effort values (though this can be easily added)

All other features for a normal Pokémon battle are preserved, including all the moves’ effects.

## Core Components
In order to reverse engineer the battle mechanisms, I’ve created a few basic classes to get the project started.

All the core components are under `~/core` folder.
### Class: Move
One can create a move by using the move’s id or its name, using lower cases with `-` among words.
The main properties of a `Move` object are:
- `Move.power`, `Move.accuracy`, and `Move.effect_id`. These properties are probably the most used in a Pokemon battle.
- `Move.meta_category_id`, `Move.target_id` are data from `move_meta.csv`, which along with all the other `csv` files, are copied from [veekun](https://github.com/veekun/pokedex). The details can be found under `~/data/csv/*_prose.csv`.
### Class: Status
A `Status` object contains all information about a Pokemon’s [status conditions](https://bulbapedia.bulbagarden.net/wiki/Status_condition). Status conditions is a rather complicated topic, so even with this class being written, there are still a great number of improvements need to be made.

When creating a `Status` object, one can use the status id defined in the `csv` file, or simply use the name of the status. One can also pass a `lasting_round` parameter into the instantiation, which represents *how long* the status is going to last. If this parameter is not provided, it is assumed that the status lasts forever (unless something forces it to end, such as using an item).

Some properties are:
- `Status.start`, `Status.stop`, `Status.remaining_round` are the starting round number, the stopping round number, and the remaining round number of the status respectively. Note that ‘round’ and ‘turn’ are interchangeable.
- `Status.volatile` is an array of boolean values representing if each status in the object is a [volatile status](https://bulbapedia.bulbagarden.net/wiki/Status_condition#Volatile_status) or not. We need to distinguish between volatile and non-volatile statuses because a Pokemon can have many of the former, and can only have one of the latter at the same time.

One notable thing about `Status` is that it is **addible**. For example:
```python
>>> burn = Status('burn')
>>> confused = Status('confused')
>>> combined = burn + confused
>>> combined.name
['burn', 'confused']
```
When adding two non-volatile statuses together, because they can’t stack, the newer one gets to replace the older one.

One can also iterate through all the statuses, by using
```python
>>> [x for x in some_status]
```
### Class: Trainer
A `Trainer` object is like a player in the game, who has some Pokemons in the [party](https://bulbapedia.bulbagarden.net/wiki/Party).

One can use `Trainer.party(n)` to call the n-th `Pokemon` object (see below) in the party, and also set the n-th `Pokemon` by using `Trainer.set_pokemon(pos, pokemon)`.

Another *very* important `Trainer`’s property is `Trainer.events`. Many moves’ effects are dependent upon the past damage, stats changes, etc., which is why this project is not as easy as I thought. It seems that there is no easy way to solve this, other than recording *everything* happened.
### Class: Pokemon
One can create (summon?) a Pokemon by using the `Pokemon` class, using either the Pokemon’s national ID  or its name, written in lower cases, with `-` among words. Some main properties of the `Pokemon` class are:
* `Pokemon.stats` is the calculated [stats](https://bulbapedia.bulbagarden.net/wiki/Statistic) (hp, attack, defense, special-attack, special-defense, and speed) based on various factors, such as the Pokemon’s level,[individual values](https://bulbapedia.bulbagarden.net/wiki/Individual_values), and natures.
Usage:
```python
>>> Pokemon(123).stats
>>> Pokemon(123).stats.specialAttack
```
- `Pokemon.current` and `Pokemon.stage` describe the *in-battle* stats of the Pokemon. `Pokemon.current` is the calculated stats after taking the [stage](https://bulbapedia.bulbagarden.net/wiki/Statistic#Stat_modifiers) changes into account. The usage is the same as `Pokemon.stats`.
- `Pokemon.moves` is a `list` of moves learned by the Pokemon. Each item in the list is a `Move` object. One can customize the moves.
- `Pokemon.status` is a `Status` object. The `Status` class currently needs a lot of testing.
- `Pokemon.trainer` calls a `Trainer` object that the Pokemon belongs to. If none is assigned, it will return `None`.