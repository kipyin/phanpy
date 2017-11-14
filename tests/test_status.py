#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import os, sys

file_path = os.path.dirname(os.path.abspath(__file__))
root_path = file_path.replace('/phanpy/tests', '')
sys.path.append(root_path) if root_path not in sys.path else None

import numpy as np
from phanpy.core.objects import Status


def test_declare_a_status_by_id_from_the_table():
    assert Status(5).name[0] == 'poison'


def test_declare_a_status_with_a_timer():
    assert Status(5, 5).duration[0] == 5


def test_declare_a_status_by_name_from_the_table():
    assert Status('poison').id[0] == 5


def test_declare_a_custom_status():
    trick_room = Status('trick-room', 5)
    assert trick_room.id[0] >= 100000
    assert trick_room.duration[0] == 5
    assert trick_room.volatile[0] == True


def test_status_volatility():
    assert Status(20).volatile[0] == True
    assert Status(0).volatile[0] == False


@pytest.fixture(scope='function')
def setup():
    poison = Status(5)
    burn = Status('burn')
    confused = Status('confused', 5)
    disabled = Status('disabled', 4)
    yield poison, burn, confused, disabled


class TestStatusAddition():

    def test_add_two_non_volatile(self, setup):

        poison, burn, __, __ = setup
        non_volatile = poison + burn  # burn should override poison
        assert non_volatile.name == ['burn']
        # Check if the original ones are mutated or not.
        assert poison.name == ['poison']
        assert burn.name == ['burn']

    def test_add_a_volatile_to_non_volatile(self, setup):

        poison, __, confused, __ = setup
        mixed = poison + confused
        assert sorted(mixed.name) == sorted(['poison', 'confused'])
        assert sorted(mixed.duration) == sorted([float('inf'), 5])

    def test_add_two_volatile_statuses(self, setup):
        __, __, confused, disabled = setup
        volatile = confused + disabled
        assert sorted(volatile.name) == sorted(['confused', 'disabled'])
        assert sorted(volatile.duration) == sorted([5, 4])

    def test_add_a_status_to_a_mixed(self, setup):

        poison, __, confused, disabled = setup
        volatile = confused + disabled
        mixed2 = volatile + poison
        assert sorted(mixed2.name) == sorted(['confused', 'disabled', 'poison'])
        assert sorted(mixed2.volatile) == sorted([True, True, False])

    def test_add_multiple_in_one_line(self, setup):
        __, burn, confused, disabled = setup
        mixed = burn + confused + disabled
        assert sorted(mixed.name) == sorted(['burn', 'confused', 'disabled'])


def test_remove_an_existing_status_by_name(setup):
    poison, __, confused, disabled = setup
    combined = poison + confused + disabled
    combined.remove('poison')
    assert sorted(combined.name) == sorted(['confused', 'disabled'])
    assert sorted(combined.duration) == sorted([5, 4])
    assert sorted(combined.volatile) == sorted([True, True])


def test_remove_an_existing_status_by_id(setup):
    poison, __, confused, disabled = setup
    combined = poison + confused + disabled
    combined.remove(5)
    assert sorted(combined.name) == sorted(['confused', 'disabled'])
    assert sorted(combined.duration) == sorted([5, 4])
    assert sorted(combined.volatile) == sorted([True, True])


def test_remove_the_only_status():
    poison = Status(5)
    poison.remove('poison')
    assert poison.id == np.array([0])
    assert poison.name == np.array(['normal'])
    assert poison.duration == np.array([float('inf')])
    assert poison.volatile == np.array([False])

def test_remove_a_non_existing_status():
    poison = Status(5)
    with pytest.raises(KeyError):
        poison.remove('burn')


def test_reduce_duration_by_1(setup):
    __, burn, confused, disabled = setup
    mixed = burn + confused + disabled
    mixed.reduce()
    assert sorted(mixed.duration) == sorted([float('inf'), 4, 3])

def test_reduce_the_duration_by_1_where_the_duration_was_1():
    burn = Status('burn', 1)
    confused = Status('confused', 5)
    mixed = burn + confused
    mixed.reduce()
    assert mixed.name == ['confused']
    assert mixed.duration == [4]
    assert mixed.volatile == [True]
