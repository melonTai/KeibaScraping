import unittest
import doctest
from scrapenetkeiba import page

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(page))
    return tests