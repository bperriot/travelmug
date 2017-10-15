#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib

import travelmug

mug = travelmug.TravelMug()


@mug.add
def addition(number_1, number_2):
    """Add 2 integers"""
    return int(number_1) + int(number_2)


@mug.add
@mug.argspec('input_file', type_='file')
def sha256(input_file):
    """Return the sha256 hash of a file"""
    return hashlib.sha256(input_file.read()).hexdigest()


@mug.add
@mug.argspec('n', type_=int)
@mug.retspec(download=True)
def square(n):
    """Return the square of integers from 1 to n"""
    return '\n'.join(["%d,%d" % (i, i**2) for i in xrange(1, n + 1)])


@mug.add
@mug.argspec('input_file', type_='file')
@mug.retspec(download=True)
def capitalize(input_file):
    """Return the file with all its letter in uppercase"""
    return input_file.read().upper()


mug.run(debug=True)
