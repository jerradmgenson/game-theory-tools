"""
Defines `GameTable`, an implementation of the classic game table structure
used by game theorists to represent the payoffs in a two-player game.

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

import re
import logging

import numpy as np
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class GameTable:
    """
    A traditional game table structure used in game theory to represent the
    payoff values for a two player game across a given domain. Currently
    limited to two players.
    
    @Note
      If any of the optional arguments to the constructor aren't given at
      instantiation, they must be assigned to the instance prior to calling
      its `construct` method. 
    
    @Options
      player1_name: Player 1's name as a str.
      player2_name: Player 2's name as a str.
      calc_player1_payoff: A function with two parameters: player 1's current
                           choice and player 2's current choice. Calculates the
                           value of player 1's payoff and returns it.
      calc_player2_payoff: A function with two parameters: player 2's current
                           choice and player 1's current choice. Calculates the
                           value of player 2's payoff and returns it.
      choices: A collection of all possible player choices.
      
    """
    
    def __init__(self, player1_name='Player 1', player2_name='Player 2',
                 calc_player1_payoff=None, calc_player2_payoff=None,
                 choices=None):

        self.player1_name = player1_name
        self.player2_name = player2_name
        self.calc_player1_payoff = calc_player1_payoff
        self.calc_player2_payoff = calc_player2_payoff
        self.choices = choices
        self.player1_payoffs = {}
        self.player2_payoffs = {}

        self.player1_dominants = []
        self.player2_dominants = []
        self.player1_dominated = []
        self.player2_dominated = []
        
    def __iter__(self):
        return RowIterator(self)

    def _find_dominants(self, player_name, dominated=False):
        """
        Find the dominant choices for player 1.
        
        @Args
          player_name: The name of the player whose dominants to find.

        @Optional
          dominated: Set to True to find dominated choices instead of dominants.
          
        @Returns
          A list of dominant choices for player 1.
          
        """
        
        player = 'player1' if player_name == self.player1_name else 'player2'
        logger.debug('Finding {} strategies for {}.'.format('dominated' if dominated else 'dominant', player))
        if dominated:
            cmp = lambda x, y: x > y

        else:
            cmp = lambda x, y: x < y
        
        # The player's dominant values across the entire game domain.
        global_dominants = []
        # Outer loop corresponds to a row.        
        for row in self:
            # The player's dominant values only across this row.
            local_dominants = []
            # Inner loop corresponds to a column. 
            for record in row:
                player_payoff = getattr(record, player + '_payoff')
                player_choice = getattr(record, player + '_choice')
                if local_dominants:
                    # One or more local dominants already exist. Check payoff
                    # of previous dominants.
                    if cmp(past_payoff, player_payoff):
                        # Current payoff is greater than previous payoff.
                        # Replace previous dominant(s) with current dominant.
                        local_dominants = [player_choice]

                    elif past_payoff == player_payoff:
                        # Current payoff is equal to previous payoff.
                        # Append current dominant to the list.
                        # If current payoff is less than previous payoff, then
                        # we just ignore it and move on.
                        local_dominants.append(player_choice)

                else:
                    # No previous local dominant exists. The current choice is
                    # a local dominant by default.
                    local_dominants = [player_choice]

                past_payoff = player_payoff
                logging.debug('local_dominants: {}'.format(local_dominants))
                    
            if record.row == 0:
                # Local dominants are always global dominants on 1st row_number.
                global_dominants = local_dominants

            else:
                # Find the new global dominants by taking the intersection of
                # the current local dominants and the old global dominants.
                global_dominants = list(set(local_dominants) & set(global_dominants))            

        logging.debug('global_dominants: {}'.format(global_dominants))
        return global_dominants

    def construct(self, choices=None):
        """
        Construct a game table from the given configuration.
        
        @Optional
          choices: A collection of all possible player choices.
          
        @Returns
          None
          
        """
        
        if not choices:
            # Custom choices were not supplied in the method call.
            # Use the default configuration for the instance.
            choices = self.choices

        # Reinitialize payoff dicts to ensure data consistency.
        self.player1_payoffs = {}
        self.players2_payoffs = {}
        for player1_choice in choices:
            for player2_choice in choices:
                self.player1_payoffs[player1_choice, player2_choice] = self.calc_player1_payoff(player1_choice,
                                                                                                player2_choice)

                self.player2_payoffs[player2_choice, player1_choice] = self.calc_player2_payoff(player2_choice,
                                                                                                player1_choice)

        self.player1_dominants = self._find_dominants(self.player1_name)
        self.player2_dominants = self._find_dominants(self.player2_name)

    def index(self, player1_choice, player2_choice):
        """
        Return the payoff pair for the given players' choices.
        Used by __getitems__ so object can use the index syntax.
        
        @Args
          player1_choice: A specific choice for player 1.
          player2_choice: A specific choice for player2.
          
        @Returns
          The payoff pair that corresponds to the given players' choices.
          
        """
        
        return (self.player1_payoffs[player1_choice, player2_choice],
                self.player2_payoffs[player2_choice, player1_choice])

    def __getitem__(self, player_choices):
        return self.index(player_choices[0], player_choices[1])

    def __str__(self):
        # Table legend.
        str_rep = ';Vertical axis: {0};Horizontal axis: {1};Payoff pairs: {0}, {1}\n\n'.format(self.player1_name, 
                                                                                               self.player2_name)
        # Column heading for all choices.
        heading = ';'
        for choice in self.choices:
            heading += str(choice) + ';'

        str_rep += heading
        for row in self:
            for record in row:
                if record.column == 0:
                    # Row heading for current row only. 
                    str_rep += '\n{};'.format(record.player1_choice)

                str_rep += '{}, {};'.format(round(record.player1_payoff),
                                            round(record.player2_payoff))

        # Add dominant strategies to table string.
        str_rep += '\n\n{}\'s Dominant Strategies;'.format(self.player1_name)
        if self.player1_dominants:            
            player1_dominants = '{}\n'.format(self.player1_dominants)
            
            # Remove Python's list syntax from string. 
            str_rep += re.sub('[\[\]]', '', player1_dominants)

        else:
            str_rep += 'None\n'

        str_rep += '{}\'s Dominant Strategies;'.format(self.player2_name)
        if self.player2_dominants:            
            player2_dominants = '{}\n\n'.format(self.player2_dominants)
            str_rep += re.sub('[\[\]]', '', player2_dominants)

        else:
            str_rep += 'None\n'

        return str_rep

    def line_graph(self, player1_choice=None, player2_choice=None, output=None):
        """ Display a line graph of the GameTable payoff data. """
        
        if not self.player1_payoffs:
            raise GameTableError('GameTable.line_graph called before GameTable.construct')
        
        fig = plt.figure()
        axis = fig.add_subplot(211)
        axis.set_ylabel('payoff')
        axis.set_xlabel('choice')
        player1_payoffs = np.array([self[x, player2_choice or x][0] for x in self.choices])
        player2_payoffs = np.array([self[player1_choice or y, y][1] for y in self.choices])
        choices = np.array(self.choices)
        player1_line, = axis.plot(choices, player1_payoffs, color='blue')
        player2_line, = axis.plot(choices, player2_payoffs, color='red')
        plt.legend((player1_line, player2_line), (self.player1_name, self.player2_name))
        if not output:
            plt.show()
            
        else:
            fig.savefig(output)

    
class RowIterator:
    """
    An iterator for `GameTable` that provides for multiple simultaneous
    iterations over a `GableTable` instance without corrupting its data.
    This is the iterator returned by calling `GameTable.__iter__`. 
    
    Args
      game_table: The instance of `GameTable` to iterate over.
    
    """
    
    def __init__(self, game_table):
        self.game_table = game_table
        self.current_row = -1
        
    def __iter__(self):
        return ColumnIterator(self.game_table, self.current_row)
        
    def __next__(self):
        self.current_row += 1
        if self.current_row == len(self.game_table.choices):
            raise StopIteration
        
        return self
    
    
class ColumnIterator:
    """
    An iterator for `GameTable` that provides for multiple simultaneous
    iterations over a `GableTable` instance without corrupting its data.
    This is the iterator returned by calling `RowIterator.__iter__`.
    
    Args
      game_table: The instance of `GameTable` to iterate over.
      row: The number of the current `GameTable` instance row.
    
    """ 
    
    def __init__(self, game_table, row):
        self.game_table = game_table
        self.current_row = row
        self.current_column = -1        
        self.player1_choice = game_table.choices[row]
        self.player2_choices = iter(game_table.choices)
        
    def __next__(self):            
        # Iterate over table columns (player 2's choices) until we reach
        # the end of the current row.
        player2_choice = next(self.player2_choices)
        self.current_column += 1
            
        return TableRecord(self.game_table, 
                           self.player1_choice, 
                           player2_choice, 
                           self.current_row, 
                           self.current_column)
        
        
class TableRecord:
    """
    Represents a single record of a `GameTable` instance, this is what gets
    returned by calling `TableIterator.__next__`.
    
    Args
      game_table: The `GameTable` instance this table record belongs to.
      player1_choice: Player1's choice for this `GameTable` record.
      player2_choice: Player2's choice for this `GameTable` record.
      row: The row number of this `GameTable` record.
      column: The column number of this `GameTable` record.
      
    Attributes
      player1_name
      player2_name
      player1_choice
      player2_choice
      player1_payoff
      player2_payoff
      row
      column
      
    
    """
    
    def __init__(self, game_table, player1_choice, player2_choice, row, column):
        
        self.player1_name = game_table.player1_name
        self.player2_name = game_table.player2_name
        self.player1_payoff = game_table.calc_player1_payoff(player1_choice, 
                                                             player2_choice)
        
        self.player2_payoff = game_table.calc_player2_payoff(player2_choice, 
                                                             player1_choice)
        
        self.player1_choice = player1_choice
        self.player2_choice = player2_choice
        self.row = row
        self.column = column


class GameTableError(Exception):
    """
    An exception that gets raised when an error occurs with a GameTable instance.

    """
