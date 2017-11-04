# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 04:22:57 2017

@author: Kip
"""

import pandas as pd

with open('./csv/move_meta_ailments.csv') as csv_file:
    ailments = pd.read_csv(csv_file)

global clock
clock = 1


class Status():

    def __init__(self, status_id, lasting_time=None):

        self.id = status_id
        self.start = clock
        if not lasting_time:
            self.stop = self.start + lasting_time
        self.name = ailments[ailments["id"] == self.id]["identifier"].values[0]

    def __add__(self, other):
        pass

    @property
    def current_round(self):
        return clock

    @property
    def remaining_round(self):
        return self.stop - self.current_round

    @property
    def is_volatile(self):
        return self.id not in range(0, 6)


