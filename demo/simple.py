#!/usr/bin/env python
# -*- coding: utf-8 -*-

import travelmug

mug = travelmug.TravelMug()


@mug.add(print_name='Addition of integers')
def addition(number_1, number_2):
    """Add 2 integers"""
    return int(number_1) + int(number_2)


@mug.add
def fail(number_1, number_2):
    """Will always fail"""
    raise ValueError("I can't succeed")


@mug.add
@mug.argspec('number_1', print_name='a')
@mug.argspec('number_1', type_=int)
@mug.argspec('number_2', print_name='b', type_=int)
def mul(number_1, number_2):
    """Return a * b"""
    return number_1 * number_2


@mug.add
def divide(number_1, number_2):
    """Return number 1 / number 2

    Do NOT divide by 0."""
    return int(number_1) / float(number_2)


mug.run(debug=True)
