#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''# Activate these codes when import fails.
import os
import sys

file_path = os.path.dirname(os.path.abspath(__file__))
root_path = file_path.replace('/mechanisms', '')

sys.path.append(root_path) if root_path not in sys.path else None
'''
from functools import reduce

import numpy as np
from np.random import binomial, uniform

from mechanisms.core.helpers import efficacy
from mechanisms.data.tables import move_natural_gift

# XXX: consider merging all classes to one file.
from mechanisms.core.item import Item
from mechanisms.core.pokemon import Trainer, Pokemon
from mechanisms.core.move import Move
from mechanisms.core.status import Status


def order_of_attack(p1, p1_move, p2, p2_move):
    """Determines the order of attack.

    # XXX: need to take effects into account, e.g.
    trick-room, quick-claw.
    """

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

    return f1, m1, f2, m2


def can_select_a_move(f, m):
    """If the Pokémon is able to **select** a move, return True.
    """
    if 'recharge' in f.status:
        # `f` cannot make a move after using a move requiring
        # recharging.
        return False
    else:
        return True


def can_use_the_selected_move(f, m):
    """If the Pokémon is able to **use** a selected move, return True.

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

    statuses = f.status

    if f.order == 2 and 'flinch' in statuses:
        # A Pokémon can only flinch if it is hit by another Pokémon's
        # move before using its move.
        return True

    elif 'paralysis' in statuses:
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

    if 'taking-aim' in f2.status:
        # If the target has been aimed at in the previous turn, the
        # attacker's move will not miss. 'taking-aim' should be have a
        # life time of 1.
        # Moves that induce 'taking-aim' status are 'mind-reader' and
        # 'lock-on'.
        return 1

    elif f2.status.semi_invulnerable:
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
            return 0

    if np.isnan(m1.accuracy):
        # I haven't found any cases where the accuracy is nan and still
        # has a chance to miss.
        # XXX: an exhaustive check on this.
        return 1

    else:
        # If the move's accuracy is not nan, use the regular hit rate
        # formula P = move's accuracy * user's accuracy / opponent's
        # evasion.
        p = m1.accuracy/100. * f1.stage_factor.accuracy/f2.stage_factor.evasion
        return binomial(1., p)


def critical(f1, m1):
    """Returns 2 if a hit is critical else 1 (Gen.II ~ Gen.V).

    # XXX: moves exempt from critical hit calculation?
    """
    f1.stage.critical += m1.crit_rate

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
    if m1.type_id in f1.types:
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


def regular_damage(f1, m1, f2, m2):
    """Retuns the damage for all moves deals regular damage.
    """
    global turn

    effect = m1.effect_id

    critical_modifier = critical(f1, m1)
    type_modifier = efficacy(m1.type_id, f2.types)
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

    if effect == 155:
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

        if 'stockpile' in f1.flags.keys():
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
            m1.type_id = __subset["type_id"].values[0]

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

            f1.item.fling(f2)
            # Item().fling(target) activates the fling_effect to
            # the given `target`.
            # XXX: this method is incomplete. See item.py

            if f1.item.fling_power:
                power = f1.item.fling_power
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
            m1.type_id = m2.type_id
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

        stats_in_interest = ['attack', 'defense', 'specialAttack',
                             'specialDefense', 'speed']

        __e_s = f1.trainer.events.opponent.stats.loc[:turn, stats_in_interest]
        __e_s = __e_s[__e_s > 0]

        __e_o = f2.trainer.events.self.stats.loc[:turn, stats_in_interest]
        __e_o = __e_o[__e_o > 0]

        total_increase = (__e_s.sum().sum()
                          + __e_o.sum().sum())

        power = np.clip(a=total_increase * 20 + 60,
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

    return (2 + (2 * (f1.level/5 + 1) * power * A/D) // 50) * modifiers


def deals_direct_damage(m1):
    """An indicator function returns True if `m1` deals direct damage.
    """
    # XXX: incomplete
    # list_of_moves_with_dd = (some_kind_of_list)
    # return m1 in list_of_moves_with_dd
    return True


def direct_damage(f1, m1, f2, m2):
    """Calculates the damage for moves deal direct damage.
    """
    effect = m1.effect_id

    def immuned(damage):
        """A simple filter for damage that takes typ-immunity into
        account.
        """
        return 0 if efficacy(m1.type_id, f2.types) == 0 else damage

    if effect == 27:
        # User waits for two turns.
        # On the second turn, the user inflicts twice the damage it
        # accumulated on the last Pokémon to hit it.  Damage inflicted
        # is [typeless]{mechanic:typeless}.
        #
        # This move cannot be selected by []{move:sleep-talk}.
        # XXX: group moves with `charge` flag into a new function.
        pass

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
        return f1.level * np.random.randint(5, 15)/10.

    elif effect == 90:
        # Targets the last opposing Pokémon to hit the user with a
        # physical move this turn.
        # Inflicts twice the damage that move did to the user.
        # If there is no eligible target, this move will fail.
        # Type immunity applies, but other type effects are ignored.

        if f1.order == 2:
            received_damage = f2.trainer.events.opponent.damage[turn].values
            if received_damage.any() and m2.damage_class_id == 2:
                return immuned(received_damage * 2)
        else:
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
            received_damage = f2.trainer.events.opponent.damage[turn].values
            if received_damage.any() and m2.damage_class_id == 3:
                return immuned(received_damage * 2)
        else:
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

        for pokemon in f1.trainer.party():
            if pokemon.status.volatile.all():
                damage += regular_damage(pokemon, m, f2, m2)
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
            received_damage = f2.trainer.events.opponent.damage[turn].values
            if (received_damage.any() and m2.damage_class_id != 1):
                return immuned(received_damage * 1.5)
        else:
            return 0.

    elif effect == 321:
        # Inflicts damage equal to the user's remaining
        # [HP]{mechanic:hp}.  User faints.

        damage = f1.current.hp
        f1.current.hp = 0
        f1.trainer.events.self.damage[turn] = f1.current.hp

        return damage

    else:
        # All cases up to Gen.5 should be covered.
        raise ValueError("{}'s effect is not covered!"
                         " (effect id {})".format(m1.name, m1.effect_id))


def attack(f1, m1, f2):
    """f1 uses m1 to attack f2.

    Given f1 is mobile. Given f1 attacks first.

    Moves with different meta-categories have different behaviors.
    There are 14 different meta-categories according to veekun.com.

    Chekcing order:
        direct damage
        other damage
    """

    if hit_indicator(f1, m1, f2):
        # Determine if the move is hit or not.
        if m1.meta_category_id in [0, 4, 6, 7, 8]:
            # For all moves that deal damage
            #
            # if (the hit deals direct damage):
            #   damage = direct_damage(f1, m1, f2)
            # else:
            #   m1.power = power(f1, m1, f2)
            #   damage = (regular_damage_calculation)
            pass


def test():

    turn = 1
    red = Trainer('Red')
    green = Trainer('Green')

    p1 = red.party(np.random.choice([1, 2, 3]))
    p2 = green.party(np.random.choice([1, 2, 3]))

    m1 = p1.moves[np.random.choice(np.arange(1, 5))]
    m2 = p2.moves[np.random.choice(np.arange(1, 5))]

    print(order_of_attack(p1, m1, p2, m2))
    print(can_use_the_selected_move(p1, m1))
    print(can_select_a_move(p2, m2))


test()
