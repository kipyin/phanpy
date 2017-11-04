#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 10:10:45 2017

@author: Kip
"""

def clock():
    time = 1
    yield time
    time += 1

x = clock()
print(x.next())
print(x.next())
