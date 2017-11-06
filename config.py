#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 11:08:19 2017

@author: Kip
"""
import os
import sys

file_path = os.path.dirname(os.path.abspath(__file__))
root_path = file_path.replace('/mechanisms', '')
core_path = file_path + '/core'
data_path = file_path + '/data/csv/'


from mechanisms.core.helpers import which_version

VERSION_GROUP_ID, REGION_ID, VERSION_ID = which_version('platinum')
