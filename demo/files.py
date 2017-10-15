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


mug.run(debug=True)
