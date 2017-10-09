#!/usr/bin/env python
# -*- coding: utf-8 -*-

import travelmug

mug = travelmug.TravelMug()


@mug.add
def addition(number_1, number_2):
    """Add 2 integers"""
    return int(number_1) + int(number_2)


@mug.add
def sub(number_1, number_2):
    """Return number_1 - number_2"""
    return int(number_1) - int(number_2)


mug.run(debug=True)
