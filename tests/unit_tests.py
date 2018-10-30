"""
Unit tests for Game Theory Tools.

BSD 3-Clause License

Copyright (c) 2018 Jerrad M. Genson
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

import unittest
import logging
from functools import partial

from sympy import Rational

from gametable import GameTable
from tests.test_data import GameTableTestData


class GameTableTests(unittest.TestCase):
    """ Unit tests for `gametable.GameTable`. """

    TEST_DATA = GameTableTestData()

    @staticmethod
    def default_payoff(my_price, their_price):
        """
        A default payoff function that has no dominant strategies when it is
        used symmetrically.
        """
        
        per_item_profit = my_price - GameTableTests.TEST_DATA.FIXED_COSTS
        sales = GameTableTests.TEST_DATA.BASE_SALES + (their_price - my_price) * 10
        total_profit = sales * per_item_profit
        
        return total_profit

    def setUp(self):
        self.game_table = PROTO_GAME_TABLE()
        self.game_table.construct()

    def test_construct(self):
        """ Test `gametable.GameTable.construct` """

        self.assertEqual(self.game_table.player1_payoffs, self.TEST_DATA.P1_EXPECTED_PAYOFFS)
        self.assertEqual(self.game_table.player2_payoffs, self.TEST_DATA.P2_EXPECTED_PAYOFFS)
        
    def test_getitem(self):
        """ Test `gametable.GameTable.__getitem__` """
        
        # Outer loop is iterating over game table rows.
        for p1_price in self.TEST_DATA.PRICES:
            # Inner loops is iterating over game table columns.
            for p2_price in self.TEST_DATA.PRICES:
                p1_payoff, p2_payoff = self.game_table[p1_price, p2_price]
                self.assertEqual(p1_payoff, self.TEST_DATA.P1_EXPECTED_PAYOFFS[p1_price, p2_price])
                self.assertEqual(p2_payoff, self.TEST_DATA.P2_EXPECTED_PAYOFFS[p2_price, p1_price])
                
    def test_str(self):
        """ Test `gametable.GameTable.__str__` """

        game_table = PROTO_GAME_TABLE(minimax=True)
        game_table.construct()
        self.assertEqual(str(game_table).strip(), self.TEST_DATA.expected_game_table_str.strip())
        
    def test_find_dominants_no_dominants(self):
        """ Test `gametable.GameTable._find_dominants` on a case with no
            dominant strategies.
            
        """
        
        self.assertEqual(self.game_table.player1_dominants, self.TEST_DATA.P1_EXPECTED_DOMINANTS)
        self.assertEqual(self.game_table.player2_dominants, self.TEST_DATA.P2_EXPECTED_DOMINANTS)

    def test_find_dominants_one_dominant(self):
        """ Test `gametable.GameTable._find_dominants` on a case with one
            dominant strategy per player.

        """

        def calc_player1_payoff(my_price, their_price):
            if my_price == 10:
                return 2

            else:
                return 1

        def calc_player2_payoff(my_price, their_price):
            if my_price == 9:
                return 2

            else:
                return 1

        game_table = GameTable(calc_player1_payoff=calc_player1_payoff,
                               calc_player2_payoff=calc_player2_payoff,
                               choices=range(0, 11))

        game_table.construct()
        self.assertEqual(game_table.player1_dominants, [10])
        self.assertEqual(game_table.player2_dominants, [9])

    def test_find_dominants_multiple_dominants(self):
        """ Test `gametable.GameTable._find_dominants` on a case with multiple
            dominant strategies per player.

        """

        player1_dominants = [2, 5]
        player2_dominants = [1, 3, 6]
        def calc_player1_payoff(my_price, their_price):
            if my_price in player1_dominants:
                return 2

            else:
                return 1

        def calc_player2_payoff(my_price, their_price):
            if my_price in player2_dominants:
                return 2

            else:
                return 1

        game_table = GameTable(calc_player1_payoff=calc_player1_payoff,
                               calc_player2_payoff=calc_player2_payoff,
                               choices=range(0, 11))

        game_table.construct()
        self.assertEqual(game_table.player1_dominants, player1_dominants)
        self.assertEqual(game_table.player2_dominants, player2_dominants)

    def test_find_dominated_multiple_dominated(self):
        """ Test `gametable.GameTable._find_dominants` on a case with multiple
            dominated strategies per player.

        """

        player1_dominated = [1, 3, 4, 6]
        player2_dominated = [2, 4, 5]
        def calc_player1_payoff(my_price, their_price):
            if my_price in player1_dominated:
                return 1

            else:
                return 2

        def calc_player2_payoff(my_price, their_price):
            if my_price in player2_dominated:
                return 1

            else:
                return 2

        game_table = GameTable(calc_player1_payoff=calc_player1_payoff,
                               calc_player2_payoff=calc_player2_payoff,
                               choices=range(0, 11))
        
        game_table.construct()
        self.assertEqual(game_table.player1_dominated, player1_dominated)
        self.assertEqual(game_table.player2_dominated, player2_dominated)
        
    def test_iter(self):
        """ Test iterating over a `GameTable` instance. """
        
        for row_number, row in enumerate(self.game_table):
            for column_number, record in enumerate(row):
                record_number = (row_number + 1) * (column_number + 1)
                if record_number == 1:
                    self.assertEqual(record.player1_choice, 31)
                    self.assertEqual(record.player2_choice, 31)
                    self.assertAlmostEqual(record.player1_payoff, 100.0)
                    self.assertAlmostEqual(record.player2_payoff, 100.0)
                    self.assertEqual(record.row, 0)
                    self.assertEqual(record.column, 0)
                    
                elif record_number == 363:
                    self.assertEqual(record.player1_choice, 43)
                    self.assertEqual(record.player2_choice, 58)
                    self.assertAlmostEqual(record.player1_payoff, 3250.0)
                    self.assertAlmostEqual(record.player2_payoff, -1400.0)
                    self.assertEqual(record.row, 12)
                    self.assertEqual(record.column, 27)
                    
                elif record_number == 784:
                    self.assertEqual(record.player1_choice, 58)
                    self.assertEqual(record.player2_choice, 58)
                    self.assertAlmostEqual(record.player1_payoff, 2800.0)
                    self.assertAlmostEqual(record.player2_payoff, 2800.0)
                    self.assertEqual(record.row, 27)
                    self.assertEqual(record.column, 27)
                
        self.assertEqual(record_number, 784)
        self.assertEqual(record.row, 27)
        self.assertEqual(record.column, 27)
        self.assertEqual(record.player1_name, 'Player 1')
        self.assertEqual(record.player2_name, 'Player 2')

    def test_minimax_rock_paper_scissors(self):
        """
        Test GameTable._find_minimax on a simple game of rock, paper, scissors.

        """

        target_mixing_ratios = (Rational(1, 3),) * 3
        choices = ('rock', 'paper', 'scissors')
        def calc_payoff(my_choice, their_choice):
            my_index = choices.index(my_choice)
            their_index = choices.index(their_choice)
            if my_choice == their_choice:
                return 0

            elif my_index in (their_index + 1, their_index - 2):
                return 1

            else:
                return -1

        game_table = GameTable(calc_player1_payoff=calc_payoff,
                               calc_player2_payoff=calc_payoff,
                               choices=choices,
                               minimax=True)

        game_table.construct()
        self.assertEqual(game_table.player1_mixing_ratios, target_mixing_ratios)
        self.assertEqual(game_table.player2_mixing_ratios, target_mixing_ratios)


PROTO_GAME_TABLE = partial(GameTable,
                           player1_name='Player 1',
                           player2_name='Player 2',
                           calc_player1_payoff=GameTableTests.default_payoff,
                           calc_player2_payoff=GameTableTests.default_payoff,
                           choices=GameTableTests.TEST_DATA.PRICES)
