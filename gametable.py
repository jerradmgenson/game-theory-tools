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

import numpy as np
import matplotlib.pyplot as plt
import sympy


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
                 choices=None, minimax=False):

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
        self.nash_equilibria = set()
        self.minimax = minimax
        self.player1_mixing_ratios = None
        self.player2_mixing_ratios = None

    def __iter__(self):
        return RowIterator(self)

    def _find_dominants(self, record_collections, cmp=max):
        """
        Common code for player 1 and player 2 find dominants methods.

        """

        # Find the indices of the maximum values in each column.
        max_indices = []
        for record_collection in record_collections:
            max_value = cmp(record_collection)
            max_indices.append([index for index, value in enumerate(record_collection) if value == max_value])

        # Check if any max value indices match across all columns.
        matching_indices = max_indices[0]
        for indices in max_indices[1:]:
            matching_indices = list(set(matching_indices) & set(indices))

        # Return a list of strategies corresponding to the matching indices.
        choices_list = list(self.choices)
        dominant_strategies = [choices_list[index] for index in matching_indices]

        return dominant_strategies

    def _find_player1_dominants(self, dominated=False):
        """
        Find all dominant strategies for player 1.

        Returns
          A list of player 1's dominant strategies (choices).

        """

        # Construct a list of columns of player1 payoff values.
        columns = []
        for row in self:
            for record_number, record in enumerate(row):
                try:
                    columns[record_number].append(record.player1_payoff)

                except IndexError:
                    columns.append([record.player1_payoff])
            
        return self._find_dominants(columns, min if dominated else max)

    def _find_player2_dominants(self, dominated=False):
        """
        Find all dominant strategies for player 2.

        Returns
          A list of player 2's dominant strategies (choices).

        """

        # Construct a list of rows of player 2's payoff values.
        rows = [[record.player2_payoff for record in row] for row in self]
        return self._find_dominants(rows, min if dominated else max)

    def _find_nash_equilibria(self):
        """
        Find any Nash Equilibria that exist in this game table.
        """

        # Separate table records into columns (for player 1) data and
        # rows (for player 2).
        columns = []
        rows = []
        for row in self:
            row_data = []
            for record_number, record in enumerate(row):
                try:
                    columns[record_number].append(record.player1_payoff)

                except IndexError:
                    columns.append([record.player1_payoff])

                row_data.append(record.player2_payoff)

            rows.append(row_data)

        # Iterate over each record in the table and check if it is the maximum
        # payoff for player 1 in the column and the maximum payoff for player 2
        # in the row. If both of these conditions are true, the corresponding
        # player choices represent a Nash Equilibrium.
        equilibria = set()
        for row_number, row in enumerate(self):
            for column_number, record in enumerate(row):
                player1_best = record.player1_payoff == max(columns[column_number])
                player2_best = record.player2_payoff == max(rows[row_number])
                if player1_best and player2_best:
                    equilibria.add((record.player1_choice, record.player2_choice))

        return equilibria

    def _find_minimax(self):
        # For each player's choice, construct an expression that describes their
        # expected payoff based on the other player's choice. The last of the
        # opposing player's choices should be represented in each expression as
        # one minus the sum of the other choice variables so that the equations
        # may later be solved.
        def create_payoff_expressions(player_name):
            if player_name == self.player1_name:
                base_variable = 'x'
                player_number = 1

            elif player_name == self.player2_name:
                base_variable = 'y'
                player_number = 2

            else:
                raise ValueError("`player_name` not '{}' or '{}'.".format(self.player1_name, self.player2_name))

            expressions = []
            variables = []
            for records in self.iterplayer(player_number):
                expression = 0
                for record_number, payoff in enumerate(records):
                    try:
                        variable = variables[record_number]

                    except IndexError:
                        if record_number + 1 < len(self.choices):
                            variable = sympy.symbols(base_variable + str(record_number))

                        else:
                            variable = 1 - sum(variables)

                        variables.append(variable)

                    expression += payoff * variable

                expressions.append(expression)

            return expressions, variables

        player1_expressions, player1_variables = create_payoff_expressions(self.player1_name)
        player2_expressions, player2_variables = create_payoff_expressions(self.player2_name)        

        # For each player, set each of that player's choice equations against
        # as equal to each other and solve the system of equations.
        player1_solutions = sympy.linsolve(player1_expressions, player1_variables)
        player2_solutions = sympy.linsolve(player2_expressions, player2_variables)

        # Return a tuple of sets describing each player's mixing ratios.
        # The first element in the tuple is player 1's ratios and the
        # second element is player 2's ratios. Each tuple element is a set of
        # mixing ratios in the same order as the order of choices in the game
        # table instance.
        return player1_solutions, player2_solutions

    def iterplayer(self, player_number):
        payoffs = getattr(self, 'player{}_payoffs'.format(player_number))
        def iterrecords():
            for my_choice in self.choices:
                yield payoffs[my_choice, their_choice]
            
        for their_choice in self.choices:
            yield iterrecords()

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

        self.player1_dominants = self._find_player1_dominants()
        self.player2_dominants = self._find_player2_dominants()
        self.player1_dominated = self._find_player1_dominants(dominated=True)
        self.player2_dominated = self._find_player2_dominants(dominated=True)
        self.nash_equilibria = self._find_nash_equilibria()
        if self.minimax:    
            p1_mixing_ratios, p2_mixing_rations = self._find_minimax()
            self.player1_mixing_ratios = p1_mixing_ratios
            self.player2_mixing_ratios = p2_mixing_rations

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

        def add_strategies(strategies):
            if strategies:
                str_rep = '{}\n'.format(strategies)

                # Remove Python's list syntax from string.
                str_rep = re.sub('[\[\]]', '', str_rep)

            else:
                str_rep = 'None\n'

            return str_rep

        # Add dominant strategies to table string.
        str_rep += '\n\n{}\'s Dominant Strategies;'.format(self.player1_name)
        str_rep += add_strategies(self.player1_dominants)
        str_rep += '{}\'s Dominant Strategies;'.format(self.player2_name)
        str_rep += add_strategies(self.player2_dominants)
        
        # Add dominated strategies to table string.
        str_rep += '\n\n{}\'s Dominated Strategies;'.format(self.player1_name)
        str_rep += add_strategies(self.player1_dominated)
        str_rep += '{}\'s Dominated Strategies;'.format(self.player2_name)
        str_rep += add_strategies(self.player2_dominated)

        # Add Nash Equilibria to table string.
        for count, equilibrium in enumerate(self.nash_equilibria):
            str_rep += '\n\n' if count == 0 else '\n'
            number = ' #' + str(count + 1) if len(equilibrium) > 1 else ''
            str_rep += 'Nash Equilibrium{};{}'.format(number, equilibrium)

        if self.minimax:
            # Add minimax ratios to table string.
            str_rep += '\n\nPlayer 1 mixing ratios;'
            for ratio in next(iter(self.player1_mixing_ratios)):
                str_rep += '{};'.format(ratio)

            str_rep += '\nPlayer 2 mixing ratios;'
            for ratio in next(iter(self.player2_mixing_ratios)):
                str_rep += '{};'.format(ratio)
        
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
