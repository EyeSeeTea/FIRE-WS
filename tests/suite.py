import fire
import os
import unittest

def get_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests/fire_tests', pattern='test_*.py')
    return test_suite

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(get_test_suite())
