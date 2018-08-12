"""
BSD 3-Clause License

Copyright (c) 2018, Jerrad Genson
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
        global_dominants = []
        local_dominants = []
        for p2_choice in self.choices:
            for p1_choice in self.choices:
                payoff = p1_payoffs[(p1_choice, p2_choice)]
                if local_dominants:
                    past_payoff = p1_payoffs[(local_dominants[0], p2_choice)]
                    if past_payoff < payoff:
                        local_dominants = [p1_choice]

                    elif past_payoff == payoff:
                        local_dominants.append(p1_choice)

                else:
                    local_dominants = [p1_choice]

            if global_dominants:
                for choice in global_dominants:
                    if choice not in local_dominants:
                        global_dominants.remove(choice)

                for choice in local_dominants:
                    if choice not in global_dominants:
                        local_dominants.remove(choice)

            global_dominants.extend(local_dominants)

        return global_dominants

    def construct(self, choices=None):
        if choices:
            self.choices = choices

        self.player1_payoffs = {}
        self.players2_payoffs = {}
        for player1_choice in self.choices:
            for player2_choice in self.choices:
                self.player1_payoffs[(player1_choice, player2_choice)] = self.calc_player1_payoff(player1_choice,
                                                                                                  player2_choice)

                self.player2_payoffs[(player2_choice, player1_choice)] = self.calc_player2_payoff(player2_choice,
                                                                                                  player1_choice)

        self.player1_dominants = self._find_dominants(self.player1_payoffs,
                                                      self.player2_payoffs)

        self.player2_dominants = self._find_dominants(self.player2_payoffs,
                                                      self.player1_payoffs)

    def index(self, player1_choice, player2_choice):
        return (self.player1_payoffs[(player1_choice, player2_choice)],
                self.player2_payoffs[(player2_choice, player1_choice)])

    def __getitem__(self, player_choices):
        return self.index(player_choices[0], player_choices[1])

    def __str__(self):
        str_rep = ';({}, {})\n\n'.format(self.player1_name, self.player2_name)
        heading = ';'
        for scenario in self.choices:
            heading += str(scenario) + ';'

        str_rep += heading
        for player2_choice in self.choices:
            str_rep += '\n{};'.format(player2_choice)
            for player1_choice in self.choices:
                p1_payoff, p2_payoff = self.index(player1_choice, player2_choice)
                str_rep += '({}, {});'.format(round(p1_payoff), round(p2_payoff))

        if self.player1_dominants:
            str_rep += '\n\n{}\'s Dominant Strategies\n'.format(self.player1_name)
            player1_dominants = '{}\n'.format(self.player1_dominants)
            str_rep += re.sub('[\[\]]', '', player1_dominants)

        else:
            str_rep += 'None\n'

        if self.player2_dominants:
            str_rep += '\n{}\'s Dominant Strategies\n'.format(self.player2_name)
            player2_dominants = '{}\n\n'.format(self.player2_dominants)
            str_rep += re.sub('[\[\]]', '', player2_dominants)

        else:
            str_rep += 'None\n'

        return str_rep
