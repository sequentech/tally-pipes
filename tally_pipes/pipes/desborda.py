# -*- coding:utf-8 -*-

# This file is part of tally-pipes.
# Copyright (C) 2017  Sequent Tech Inc <legal@sequentech.io>

# tally-pipes is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License.

# tally-pipes  is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with tally-pipes.  If not, see <http://www.gnu.org/licenses/>. 

# Definition of this system: 
# http://pabloechenique.info/wp-content/uploads/2016/12/DesBorda-sistema-Echenique.pdf

import copy
from itertools import zip_longest
from .desborda_base import DesbordaBase

class Desborda(DesbordaBase):
    def __init__(self):
        pass

    def name(self):
        return 'desborda'

    def get_zipped_parity(self, a, b):
        zipped = []
        for a, b in zip_longest(a, b):
            if a is not None:
                zipped.append(a)
            if b is not None:
                zipped.append(b)
        return zipped

    def get_min_num_winners_for_team(self, category, question):
        total_points = question['totals']['valid_points']
        # number of points for the 20% of total points trigger
        percent_20_limit = total_points * 0.20
        # number of points for the 15% of total points trigger
        percent_15_limit = total_points * 0.15
        # number of points for the 10% of total points trigger
        percent_10_limit = total_points * 0.10
        # number of points for the 5% of total points trigger
        percent_5_limit = total_points * 0.05

        num_winners = question['num_winners']
        # TODO: En el reglamento pone estrictamente mayor
        if category['points_category'] > percent_15_limit:
           return 4
        elif category['points_category'] > percent_5_limit:
           return 2

        return 0

    def insert_min_team_winners(self, min_num_winners_for_team, category, a_sure_winners, b_unsure, question, women_indexes):
        ordered_team_candidates = \
            self.get_list_by_points(category['candidates_index'], question)
        minority_winners = []
        if category['is_minority']: # apply parity rules
            team_women, team_men = self.split_women_men(ordered_team_candidates, women_indexes)
            zipped_team = self.get_zipped_parity(team_women, team_men)
            if 2 == min_num_winners_for_team:
                minority_winners.extend(zipped_team[:2])
            elif 4 == min_num_winners_for_team:
                minority_winners.extend(zipped_team[:4])
        else:
            minority_winners = \
                ordered_team_candidates[:min_num_winners_for_team]
        b = [j for j in b_unsure if j not in minority_winners]
        a = a_sure_winners + minority_winners
        return a, b

def podemos_desborda(data_list, women_names=None, question_indexes=None):
    '''
    Definition of this system: 
    http://pabloechenique.info/wp-content/uploads/2016/12/DesBorda-sistema-Echenique.pdf
    It is assumed that the desborda method in tally-methods has been already applied
    '''
    desborda = Desborda()
    desborda.desborda(data_list, women_names, question_indexes)
