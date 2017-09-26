import fire
import os
import unittest

def setup():
    root_dir = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(root_dir, "fire-ws.test.conf")
    fire.init(config_path)

def get_test_suite():
    setup()
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests/fire_tests', pattern='test_*.py')
    return test_suite

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(get_test_suite())
