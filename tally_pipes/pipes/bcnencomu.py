# -*- coding:utf-8 -*-

# This file is part of tally-pipes.
# Copyright (C) 2014-2016  Sequent Tech Inc <legal@sequentech.io>

# tally-pipes is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License.

# tally-pipes  is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with tally-pipes.  If not, see <http://www.gnu.org/licenses/>.

from collections import defaultdict

def team_count_weight_correction(data_list, original_count_weight, team_count_weight, question_indexes, help=""):
    data = data_list[0]
    team_points = defaultdict(int)
    team_names = defaultdict(list)

    for question_index in question_indexes:
        for answer in data['results']['questions'][question_index]['answers']:
            team_points[answer['category']] += answer['total_count']
            team_names[answer['category']].append(answer['text'])

    for question_index in question_indexes:
        for answer in data['results']['questions'][question_index]['answers']:
            answer['total_count'] = (
                answer['total_count']*original_count_weight
                +
                team_points[answer['category']]*team_count_weight)
