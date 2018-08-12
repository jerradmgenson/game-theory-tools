'''
Created on Aug 12, 2018

@author: jgenson
'''
import unittest

from gametable import GameTable
from test_data import GameTableTestData


class GameTableTests(unittest.TestCase):
    
    def __init__(self, *args, **kwargs):
        self.test_data = GameTableTestData()
        super(GameTableTests, self).__init__(*args, **kwargs)
    
    def calc_payoff(self, my_price, their_price):
        per_item_profit = my_price - self.test_data.FIXED_COSTS
        sales = self.test_data.BASE_SALES + (their_price - my_price) * 10
        total_profit = sales * per_item_profit
        
        return total_profit

    def setUp(self):
        self.game_table = GameTable()
        self.game_table.player1_name = 'Player 1'
        self.game_table.player2_name = 'Player 2'
        self.game_table.calc_player1_payoff = self.calc_payoff
        self.game_table.calc_player2_payoff = self.calc_payoff
        self.game_table.choices = self.test_data.PRICES 

    def test_construct(self):
        self.game_table.construct()
        self.assertEqual(self.game_table.player1_payoffs, self.test_data.P1_EXPECTED_PAYOFFS)
        self.assertEqual(self.game_table.player2_payoffs, self.test_data.P2_EXPECTED_PAYOFFS)
        self.assertTrue(self.game_table.player1_dominants)
        self.assertTrue(self.game_table.player2_dominants)
        
    def test_getitem(self):
        self.game_table.construct()
        for p1_price in self.test_data.PRICES:
            for p2_price in self.test_data.PRICES:
                p1_payoff, p2_payoff = self.game_table[p1_price, p2_price]
                self.assertEqual(p1_payoff, self.test_data.P1_EXPECTED_PAYOFFS[p1_price, p2_price])
                self.assertEqual(p2_payoff, self.test_data.P2_EXPECTED_PAYOFFS[p2_price, p1_price])
                
    def test_str(self):
        self.game_table.construct()
        fd = open('test_data.csv', 'w')
        fd.write(str(self.game_table))
        fd.close()        
        self.assertEqual(str(self.game_table), self.test_data.expected_game_table_str)
        
    def test_find_dominants(self):
        self.game_table.construct()
        self.assertEqual(self.game_table.player1_dominants, self.test_data.P1_EXPECTED_DOMINANTS)
        self.assertEqual(self.game_table.player2_dominants, self.test_data.P2_EXPECTED_DOMINANTS)


if __name__ == "__main__":
    unittest.main()