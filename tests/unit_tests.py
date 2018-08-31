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

from gametable import GameTable
from test_data import GameTableTestData


class GameTableTests(unittest.TestCase):
    """ Unit tests for `gametable.GameTable`. """
    
    def __init__(self, *args, **kwargs):
        # Get static test data from the `test_data` module.
        self.test_data = GameTableTestData()
        super(GameTableTests, self).__init__(*args, **kwargs)
    
    def default_payoff(self, my_price, their_price):
        """
        A default payoff function that has no dominant strategies when it is
        used symmetrically.
        """
        
        per_item_profit = my_price - self.test_data.FIXED_COSTS
        sales = self.test_data.BASE_SALES + (their_price - my_price) * 10
        total_profit = sales * per_item_profit
        
        return total_profit

    def setUp(self):
        self.game_table = GameTable()
        self.game_table.player1_name = 'Player 1'
        self.game_table.player2_name = 'Player 2'
        self.game_table.calc_player1_payoff = self.default_payoff
        self.game_table.calc_player2_payoff = self.default_payoff
        self.game_table.choices = self.test_data.PRICES 

    def test_construct(self):
        """ Test `gametable.GameTable.construct` """
        
        self.game_table.construct()
        self.assertEqual(self.game_table.player1_payoffs, self.test_data.P1_EXPECTED_PAYOFFS)
        self.assertEqual(self.game_table.player2_payoffs, self.test_data.P2_EXPECTED_PAYOFFS)
        
    def test_getitem(self):
        """ Test `gametable.GameTable.__getitem__` """
        
        self.game_table.construct()
        # Outer loop is iterating over game table rows.
        for p1_price in self.test_data.PRICES:
            # Inner loops is iterating over game table columns.
            for p2_price in self.test_data.PRICES:
                p1_payoff, p2_payoff = self.game_table[p1_price, p2_price]
                self.assertEqual(p1_payoff, self.test_data.P1_EXPECTED_PAYOFFS[p1_price, p2_price])
                self.assertEqual(p2_payoff, self.test_data.P2_EXPECTED_PAYOFFS[p2_price, p1_price])
                
    def test_str(self):
        """ Test `gametable.GameTable.__str__` """
        
        self.game_table.construct()        
        self.assertEqual(str(self.game_table), self.test_data.expected_game_table_str)
        
    def test_find_dominants_no_dominants(self):
        """ Test `gametable.GameTable._find_dominants` on a case with no
            dominant strategies.
            
        """
        
        self.game_table.construct()
        self.assertEqual(self.game_table.player1_dominants, self.test_data.P1_EXPECTED_DOMINANTS)
        self.assertEqual(self.game_table.player2_dominants, self.test_data.P2_EXPECTED_DOMINANTS)
        
    def test_iter(self):
        """ Test iterating over a `GameTable` instance. """
        
        self.game_table.construct()
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
        

if __name__ == "__main__":
    unittest.main()
    