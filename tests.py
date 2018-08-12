'''
Created on Aug 12, 2018

@author: jgenson
'''
import unittest

from gametable import GameTable


class GameTableTests(unittest.TestCase):
    FIXED_COSTS = 30
    BASE_SALES = 100
    
    @staticmethod
    def calc_payoff(my_price, their_price):
        per_item_profit = my_price - GameTableTests.FIXED_COSTS
        sales = GameTableTests.BASE_SALES + (their_price - my_price) * 10
        total_profit = sales * per_item_profit
        
        return total_profit

    def setUp(self):
        self.game_table = GameTable()
        self.game_table.player1_name = 'Player 1'
        self.game_table.player2_name = 'Player 2'
        self.game_table.calc_player1_payoff = self.calc_payoff
        self.game_table.calc_player2_payoff = self.calc_payoff
        self.game_table.choices = range(31, 59) 

    def test_construct(self):
        self.game_table.construct()
        self.assertTrue(self.game_table.player1_payoffs)
        self.assertTrue(self.game_table.player2_payoffs)
        self.assertTrue(self.game_table.player1_dominants)
        self.assertTrue(self.game_table.player2_dominants)


if __name__ == "__main__":
    unittest.main()