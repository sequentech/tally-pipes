# -*- coding:utf-8 -*-

# This file is part of agora-results.
# Copyright (C) 2017  Agora Voting SL <agora@agoravoting.com>

# agora-results is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License.

# agora-results  is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with agora-results.  If not, see <http://www.gnu.org/licenses/>.

import math

def minimum_ballots_percent_policy(data, qindex, question, withdraw_info):
    min_percent = withdraw_info['min_percent'] / 100.0
    # minimum number of ballots for a candidate not to be withdrawn
    min_ballots = math.ceil( min_percent * data['totals']['valid_votes'] )
    removed_candidates = [ 
        {"answer_id": aindex, "question_index", qindex}
        for aindex, answer in data['answers']
        if answer['total_count'] < min_ballots ]
    if len(removed_candidates) > 0:
        if "removed-candidates" not in data:
            data["removed-candidates"] = []
        data["removed-candidates"] += removed_candidates

def withdraw_candidates(data_list, questions):
    withdraw_set = {}
    for q in questions:
        withdraw_set[q['question_index']] = q

    data = data_list[0]
    for qindex, question in enumerate(data['results']['questions']): 
        if qindex not in withdraw_set:
            continue
        withdraw_info = withdraw_set[qindex]
        if 'minimum-ballots-percent' == withdraw_info['policy']:
            minimum_ballots_percent_policy(data, qindex, question, withdraw_info)