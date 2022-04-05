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
# Desborda 3 is a modification/generalization of desborda 2.
# Basically, it's like Desborda 2, but without minorities corrections.

import copy
from itertools import zip_longest
from math import *
from .desborda_base import DesbordaBase

class Desborda3(DesbordaBase):
    def __init__(self):
        pass

    def name(self):
        return 'desborda3'

    def get_min_num_winners_for_team(self, category, question):
        return 0

    def insert_min_team_winners(self, min_num_winners_for_team, category, a_sure_winners, b_unsure, question, women_indexes):
        return a_sure_winners, b_unsure

def podemos_desborda3(data_list, women_names=None, question_indexes=None):
    desborda3 = Desborda3()
    desborda3.desborda(data_list, women_names, question_indexes)
