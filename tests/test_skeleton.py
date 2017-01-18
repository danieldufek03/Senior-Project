#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from antikythera.skeleton import fib

__author__ = "Derek Goddeau"
__copyright__ = "Derek Goddeau"
__license__ = "gpl3"


def test_fib():
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13
    with pytest.raises(AssertionError):
        fib(-10)
