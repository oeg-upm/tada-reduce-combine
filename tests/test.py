from __future__ import print_function
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# added this to import app.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from combine_tests import CombineTest
import unittest

combine_cases = unittest.TestLoader().loadTestsFromTestCase(CombineTest)
suite = unittest.TestSuite([combine_cases])
result = unittest.TextTestRunner().run(suite)
sys.exit(not result.wasSuccessful())
