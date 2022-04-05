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
# Desborda 2 is a modification/generalization of desborda. 
# Desborda is defined here:
# http://pabloechenique.info/wp-content/uploads/2016/12/DesBorda-sistema-Echenique.pdf
# It is assumed that the desborda2 method in tally-methods has been already applied

# If N is the number of winners, then the maximum points for a candidate per
# ballot will be:

# MAXP=floor(1.3*N)

# If M is the maximum number of candidates a voter can include in a ballot,
# the points that the ballot adds to each candidate will be:

# POINTS=max(1, MAXP - order)

# where 'order' is the preferential order of the candidate in the ballot (for
# example 0 for the first option, and M-1 for the last one).

# The number of female winners can be greater than the number of male winners,
# but if the number of male winners is greater than the female ones, a zipped
# parity algorithm will be applied.

# When the number of winners is more than 29, if a group of candidates has
# more than 5% of all the points, the group will be guaranteed 1 winner
# position. Also in this case, if a group has more than 10% of all the
# points, it will be guaranteed 2 winner positions. Also in this case, if a
# group has more than 15% of all the points, it will be guaranteed 3 winner
# positions. If 2 or 3 candidates win by this mechanism, the maximum number of
# male winners in each case will be one.

# When the number of winners is less or equal than 29, if a group of
# candidates has more than 10% of all the points, the group will be guaranteed 1 winner
# position. Also in this case, if a group has more than 20% of all the
# points, it will be guaranteed 2 winner positions. If 2 candidates win 
# by this mechanism, the maximum number of male winners in each case will be
# one.

import copy
from itertools import zip_longest
from math import *
from .desborda_base import DesbordaBase

##TODO: CHECK THIS
#def __get_women_names_from_question(question):
    #'''
    #Internal: automatically extract women_names from question when they are set
    #as Gender urls
    #'''
    ## calculate the list from Gender urls
    #women_names = []
    #for answer in question['answers']:
        #for url in answer['urls']:
            #if url['title'] != 'Gender':
                #continue
            #if url['url'] == 'https://sequentech.io/api/gender/M':
                #women_names.append(answer['text'])
                #break
    #return women_names

class Desborda2(DesbordaBase):
    def __init__(self):
        pass

    def name(self):
        return 'desborda2'

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
        if question['num_winners'] > 29:
            if category['points_category'] > percent_15_limit:
               return 3
            elif category['points_category'] > percent_10_limit:
               return 2
            elif category['points_category'] > percent_5_limit:
               return 1
        else:
            if category['points_category'] > percent_20_limit:
               return 2
            elif category['points_category'] > percent_10_limit:
               return 1

        return 0

    def insert_min_team_winners(self, min_num_winners_for_team, category, a_sure_winners, b_unsure, question, women_indexes):
        ordered_team_candidates = \
            self.get_list_by_points(category['candidates_index'], question)
        minority_winners = []
        if category['is_minority']: # apply parity rules
            if 1 == min_num_winners_for_team:
                minority_winners.append(ordered_team_candidates[0])
            else:
                prov_min_winners = \
                    ordered_team_candidates[:min_num_winners_for_team]
                prov_women, prov_men = self.split_women_men(prov_min_winners, women_indexes)
                if len(prov_men) <= 1:
                    minority_winners.extend(prov_min_winners)
                else:
                    minority_winners.append(prov_men[0])
                    total_women, total_men = self.split_women_men(ordered_team_candidates, women_indexes)
                    minority_winners.extend(total_women[:min_num_winners_for_team-1])
        else:
            minority_winners = \
                ordered_team_candidates[:min_num_winners_for_team]
        b = [j for j in b_unsure if j not in minority_winners]
        a = a_sure_winners + minority_winners
        return a, b

def podemos_desborda2(data_list, women_names=None, question_indexes=None):
    '''
    Desborda 2 is a modification/generalization of desborda. 
    Desborda is defined here:
    http://pabloechenique.info/wp-content/uploads/2016/12/DesBorda-sistema-Echenique.pdf
    It is assumed that the desborda2 method in tally-methods has been already applied

    If N is the number of winners, then the maximum points for a candidate per
    ballot will be:
    
    MAXP=floor(1.3*N)

    If M is the maximum number of candidates a voter can include in a ballot,
    the points that the ballot adds to each candidate will be:
    
    POINTS=max(1, MAXP - order)
    
    where 'order' is the preferential order of the candidate in the ballot (for
    example 0 for the first option, and M-1 for the last one).
    
    The number of female winners can be greater than the number of male winners,
    but if the number of male winners is greater than the female ones, a zipped
    parity algorithm will be applied.
    
    When the number of winners is more than 29, if a group of candidates has
    more than 5% of all the points, the group will be guaranteed 1 winner
    position. Also in this case, if a group has more than 10% of all the
    points, it will be guaranteed 2 winner positions. Also in this case, if a
    group has more than 15% of all the points, it will be guaranteed 3 winner
    positions. If 2 or 3 candidates win by this mechanism, the maximum number of
    male winners in each case will be one.
    
    When the number of winners is less or equal than 29, if a group of
    candidates has more than 10% of all the points, the group will be guaranteed 1 winner
    position. Also in this case, if a group has more than 20% of all the
    points, it will be guaranteed 2 winner positions. If 2 candidates win 
    by this mechanism, the maximum number of male winners in each case will be
    one.
    '''
    desborda2 = Desborda2()
    desborda2.desborda(data_list, women_names, question_indexes)
