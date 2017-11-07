#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 14:22:39 2017

@author: Kip
"""

# """Activate these codes when import fails."""
# import os
# import sys
#
# file_path = os.path.dirname(os.path.abspath(__file__))
# root_path = file_path.replace('/mechanisms', '')
#
# sys.path.append(root_path) if root_path not in sys.path else None


import numpy as np
from numpy.random import binomial, uniform

from mechanisms.core.helpers import efficacy
from mechanisms.data.tables import move_natural_gift

from mechanisms.core.pokemon import Trainer


def order_of_attack(p1, p1_move, p2, p2_move):
    """Determines the order of attack.

    # TODO: need to take effects into account, e.g.
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


def can_select_a_move(f, m):
    """If the Pokémon is able to **select** a move, return True.
    """
    if 'recharge' not in f.status:
        # `f` cannot make a move after using a move requiring
        # recharging.
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

    if 'taking-aim' in f2.status.name:
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
        # TODO: an exhaustive check on this.
        return 1

    else:
        # If the move's accuracy is not nan, use the regular hit rate
        # formula P = move's accuracy * user's accuracy / opponent's
        # evasion.
        p = m1.accuracy/100. * f1.stage_facotr.accuracy/f2.stage_factor.evasion
        return binomial(1., p)


def critical_indicator(f1, m1, f2):
    """Returns 2 if a hit is critical else 1 (Gen.II ~ Gen.V).

    # TODO: moves exempt from critical hit calculation?
    """
    pass


def power(f1, m1, f2):
    """Retuns the power for all damaging moves.
    """
    effect = m1.effect_id

    if effect == 100:
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
            return 200

        elif q < 0.1042:
            return 150

        elif q < 0.2083:
            return 100

        elif q < 0.3542:
            return 80

        elif q < 0.6875:
            return 40

        else:
            return 20

    elif effect == 122:
        # Inflicts [regular damage]{mechanic:regular-damage}.
        # Power increases with [happiness]{mechanic:happiness},
        # given by `happiness * 2 / 5`, to a maximum of 102.
        # Power bottoms out at 1.

        return np.clip(a=f1.happiness * 2./5.,
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
        #
        # On average, this move inflicts {mechanic:regular-damage}
        # with 52 power and heals the target for 1/20 its max
        # {mechanic:hp}.

        # Using the Bayesian rule to calculate the probabilities.
        # Inflicts damage 80% of the time, and heals the target 20% of
        # the time.

        inflict_damage = binomial(1, .8)

        if inflict_damage:
            # Given the move inflicts damage, there are .4/.8 chance to
            # have 40 power, .3/.8 chance to have 80 power, and .1/.8
            # chance to have 120 power.

            q = uniform(0, 1)

            if q < .125:
                return 120

            elif q < .5:
                return 80

            else:
                return 40

        else:
            return -.25 * f2.stats.hp

    elif effect == 124:
        # Inflicts {mechanic:regular-damage}.
        # Power increases inversely with {mechanic:happiness}, given by
        # `(255 - happiness) * 2 / 5`, to a maximum of 102.
        # Power bottoms out at 1.

        return np.clip(a=(255-f1.happiness) * 2./5.,
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
            return 10

        elif q < .15:
            return 30

        elif q < .35:
            return 50

        elif q < .65:
            return 70

        elif q < .85:
            return 90

        elif q < .95:
            return 110

        else:
            return 150

    elif effect == 162:
        # Inflicts [regular damage]{mechanic:regular-damage}.
        # Power is equal to 100 times the amount of energy stored by
        # []{move:stockpile}.
        # Ignores the random factor in the damage formula.
        # Stored energy is consumed, and the user's {mechanic:defense}
        # and [Special Defense]{mechanic:special-defense} are reset to
        # what they would be if []{move:stockpile} had not been used.
        # If the user has no energy stored, this move will
        # {mechanic:fail}.
        # XXX: pass
        pass

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
            return 20

        elif w <= 25:
            return 40

        elif w <= 50:
            return 60

        elif w <= 100:
            return 80

        elif w <= 200:
            return 100

        else:
            return 120

    elif effect == 220:
        # Inflicts [regular damage]{mechanic:regular-damage}.
        # Power increases with the target's current {mechanic:speed}
        # compared to the user, given by
        # `1 + 25 * target Speed / user Speed`, capped at 150.

        return np.clip(a=(1 + 25. * f2.current.speed/f1.current.speed),
                       a_max=150,
                       a_min=0)

    elif effect == 223:
        # Inflicts [regular damage]{mechanic:regular-damage}.
        # Power and type are determined by the user's held berry.
        # The berry is consumed.  If the user is not holding a berry,
        # this move will [fail]{mechanic:fail}.

        # Relevant info is stored in
        # `data/csv/custom/move_natural_gift.csv`.

        __cond = move_natural_gift["item_id"] == f1.item.id
        __subset = move_natural_gift[__cond]
        m1.type_id = __subset["type_id"].values[0]

        return __subset["power"].values[0]

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

            if f1.item.fling_power:
                return f1.item.fling_power
        else:
            return 0

    elif effect == 236:
        # Inflicts [regular damage]{mechanic:regular-damage}.
        # Power is determined by the [PP]{mechanic:pp} remaining for
        # this move, after its [PP]{mechanic:pp} cost is deducted.
        # Ignores {mechanic:accuracy} and {mechanic:evasion} modifiers.
        #
        # PP remaining | Power
        # ------------ | ----:
        # 4 or more    |    40
        # 3            |    50
        # 2            |    60
        # 1            |    80
        # 0            |   200
        #
        # If this move is activated by another move, the activating
        # move's [PP]{mechanic:pp} is used to calculate power.

        pp = m1.pp - 1

        if pp >= 4:
            return 40

        elif pp == 3:
            return 50

        elif pp == 2:
            return 60

        elif pp == 1:
            return 80

        else:
            return 200

    elif effect == 238:
        # Inflicts [regular damage]{mechanic:regular-damage}.
        # Power directly relates to the target's relative remaining
        # [HP]{mechanic:hp}, given by
        # `1 + 120 * current HP / max HP`,
        # to a maximum of 121.

        return np.clip(a=(1. + 120. * f1.current.hp/f1.stats.hp),
                       a_max=121,
                       a_min=0)

    elif effect == 246:
        # Inflicts [regular damage]{mechanic:regular-damage}.
        # Power starts at 60 and is increased by 20 for every
        # [stage]{mechanic:stage} any of the target's stats has been
        # raised, capping at 200.  [Accuracy]{mechanic:accuracy} and
        # [evasion]{mechanic:evasion} modifiers do not increase this
        # move's power.

        # Counting only stat increases. Need the event log
        # XXX: event log for stat increases.
        pass

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
            return 40

        elif r <= 3:
            return 60

        elif r <= 4:
            return 80

        elif r <= 5:
            return 100

        else:
            return 120

    else:
        # All cases up to Gen.5 should be covered.
        raise ValueError("{}'s effect is not covered!"
                         " (effect id {})".format(m1.name, m1.effect_id))


def direct_damage(f1, m1, f2):
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
        # XXX: event log
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
        # XXX; event log
        pass

    elif effect == 131:
        # Inflicts exactly 20 damage.
        # TODO: type-immunity?
        return 20

    elif effect == 145:
        # Targets the last opposing Pokémon to hit the user with a
        # [special]{mechanic:special} move this turn.
        # Inflicts twice the damage that move did to the user.
        # If there is no eligible target, this move will
        # [fail]{mechanic:fail}.
        # Type immunity applies, but other type effects are ignored.
        # XXX: event-log. Similar to effect 90.
        pass

    elif effect == 155:
        # Inflicts {mechanic:typeless} {mechanic:regular-damage}.
        # Every Pokémon in the user's party, excepting those that have
        # fainted or have a {mechanic:major-status-effect}, attacks the
        # target.
        # Calculated stats are ignored; the base stats for the target
        # and assorted attackers are used instead.
        # The random factor in the damage formula is not used.
        # []{type:dark} Pokémon still get [STAB]{mechanic:stab}.
        # XXX: event-log.

        pass

    elif effect == 190:
        # Inflicts exactly enough damage to lower the target's
        # {mechanic:hp} to equal the user's.  If the target's HP is not
        # higher than the user's, this move has no effect.
        # Type immunity applies, but other type effects are ignored.
        # This effect counts as damage for moves that respond to damage.
        return np.clip(a=f2.current.hp - f1.current.hp,
                       a_min=0,
                       a_max=f2.current.hp)

    elif effect == 228:
        # Targets the last opposing Pokémon to hit the user with a
        # damaging move this turn.
        # Inflicts 1.5× the damage that move did to the user.
        # If there is no eligible target, this move will fail.
        # Type immunity applies, but other type effects are ignored.
        # XXX: event-log.

        pass

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
        # XXX: event-log

        pass

    elif effect == 321:
        # Inflicts damage equal to the user's remaining
        # [HP]{mechanic:hp}.  User faints.

        damage = f1.current.hp
        f1.current.hp = 0

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

    # Determine if the move is hit or not.
    modifier_hit = hit_indicator(f1, m1, f2)

    if m1.meta_category_id in [0, 4, 6, 7, 8]:
        # For all moves that deal damage
        pass

satoshi = Trainer()
print(satoshi, satoshi.id, satoshi.name, satoshi.party)