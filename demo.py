#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 10:14:22 2017

@author: Kip
"""

import os
import sys

pkg_path = os.path.dirname(os.path.abspath(__file__))

if pkg_path not in sys.path:
    sys.path.append(pkg_path)

print(pkg_path)


def demo():
    from core.helpers import which_version
    print(which_version(VERSION_GROUP_ID=9))


if __name__ == '__main__':
    demo()
