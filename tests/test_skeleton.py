# -*- coding: utf-8 -*-

import pytest
from puppy_hunter.skeleton import fib

__author__ = "Chris Brodt"
__copyright__ = "Chris Brodt"
__license__ = "mit"


def test_fib():
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13
    with pytest.raises(AssertionError):
        fib(-10)
