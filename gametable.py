"""
BSD 3-Clause License

Copyright (c) 2018 Jerrad Genson
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
    
    def __init__(self, player1_name=None, player2_name=None,
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

    def _find_dominants(self, p1_payoffs, p2_payoffs):
        """
        Find the dominant choices for player 1.
        
        @Args
          p1_payoffs: Payoff dict for player 1.
          p2_payoffs: Payoff dict for player 2.
          
        @Returns
          A list of dominant choices for player 1.
          
        """        
        
        # The player's dominant values across the entire game domain.
        global_dominants = []
        # Outer loop corresponds to a row.        
        for iteration, p2_choice in enumerate(self.choices):
            # The player's dominant values only across this row.
            local_dominants = []
            
            # Inner loop corresponds to a column. 
            for p1_choice in self.choices:
                # Get player 1's payoff for the current game table cell.
                payoff = p1_payoffs[p1_choice, p2_choice]
                if local_dominants:
                    # One or more local dominants already exist. Check payoff
                    # of previous dominants.
                    past_payoff = p1_payoffs[local_dominants[0], p2_choice]
                    if past_payoff < payoff:
                        # Current payoff is greater than previous payoff.
                        # Replace previous dominant(s) with current dominant.
                        local_dominants = [p1_choice]

                    elif past_payoff == payoff:
                        # Current payoff is equal to previous payoff.
                        # Append current dominant to the list.
                        # If current payoff is less than previous payoff, then
                        # we just ignore it and move on.
                        local_dominants.append(p1_choice)

                else:
                    # No previous local dominant exists. The current choice is
                    # a local dominant by default.
                    local_dominants = [p1_choice]
                    
            if iteration == 0:
                # Local dominants are always global dominants on 1st iteration.
                global_dominants = local_dominants

            else:
                # Find the new global dominants by taking the intersection of
                # the current local dominants and the old global dominants.
                global_dominants = list(set(local_dominants) & set(global_dominants))

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

        self.player1_payoffs = {}
        self.players2_payoffs = {}
        for player1_choice in choices:
            for player2_choice in choices:
                self.player1_payoffs[player1_choice, player2_choice] = self.calc_player1_payoff(player1_choice,
                                                                                                player2_choice)

                self.player2_payoffs[player2_choice, player1_choice] = self.calc_player2_payoff(player2_choice,
                                                                                                player1_choice)

        self.player1_dominants = self._find_dominants(self.player1_payoffs,
                                                      self.player2_payoffs)

        self.player2_dominants = self._find_dominants(self.player2_payoffs,
                                                      self.player1_payoffs)

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
        
        return (self.player1_payoffs[(player1_choice, player2_choice)],
                self.player2_payoffs[(player2_choice, player1_choice)])

    def __getitem__(self, player_choices):
        return self.index(player_choices[0], player_choices[1])

    def __str__(self):
        str_rep = ';Vertical axis: {0};Horizontal axis: {1};Payoff pairs: {0}, {1}\n\n'.format(self.player1_name, 
                                                                                               self.player2_name)
        
        heading = ';'
        for scenario in self.choices:
            heading += str(scenario) + ';'

        str_rep += heading
        for player1_choice in self.choices:
            str_rep += '\n{};'.format(player1_choice)
            for player2_choice in self.choices:
                p1_payoff, p2_payoff = self.index(player1_choice, player2_choice)
                str_rep += '{}, {};'.format(round(p1_payoff), round(p2_payoff))

        str_rep += '\n\n{}\'s Dominant Strategies;'.format(self.player1_name)
        if self.player1_dominants:            
            player1_dominants = '{}\n'.format(self.player1_dominants)
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
