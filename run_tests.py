#! /bin/python3

import logging
import sys
import unittest
import os

from tests.unit_tests import GameTableTests, PROTO_GAME_TABLE
from tests.test_data import GameTableTestData

VERBOSITY = 2
logger = logging.getLogger()


def config():
    """
    Configure unit_tests module with usual options.

    """

    # Configure logging
    logger.setLevel(level=logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    if '--new-test-data' in sys.argv:
        logger.info('Creating new test data...')
        test_data = GameTableTestData()
        if os.path.exists(test_data.TEST_DATA_CSV):
            os.rename(test_data.TEST_DATA_CSV, test_data.TEST_DATA_CSV + '.old')

        game_table = PROTO_GAME_TABLE(minimax=True)
        game_table.construct()
        with open(test_data.TEST_DATA_CSV, 'w') as test_data_csv:
            test_data_csv.write(str(game_table))

        GameTableTests.TEST_DATA = GameTableTestData()


def test_suite():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(GameTableTests)
    return suite


if __name__ == '__main__':
    config()
    unittest.TextTestRunner(verbosity=VERBOSITY).run(test_suite())
