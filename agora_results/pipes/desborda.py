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

# Definition of this system: 
# http://pabloechenique.info/wp-content/uploads/2016/12/DesBorda-sistema-Echenique.pdf

import copy

#TODO: CHECK THIS
def __get_women_names_from_question(question):
    '''
    Internal: automatically extract women_names from question when they are set
    as Gender urls
    '''
    # calculate the list from Gender urls
    women_names = []
    for answer in question['answers']:
        for url in answer['urls']:
            if url['title'] != 'Gender':
                continue
            if url['url'] == 'https://agoravoting.com/api/gender/M':
                women_names.append(answer['text'])
                break
    return women_names

def podemos_desborda(data_list, women_names):
    data = data_list[0]
    for qindex, question in enumerate(data['results']['questions']):
        if women_names == None:
            women_names = __get_women_names_from_question(question)

        if "desborda" != question['tally_type'] or len(question['answers']) < 62 or question['num_winners'] != 62:
            continue

        # calculate women indexes
        women_indexes =
            [ index
              for index, answer in enumerate(question['answers'])
              if answer['text'] in women_names ]

        def get_women_indexes(people_list):
            return [ person for person in people_list if person in women_indexes ]

        def get_list_by_points(winners):
            # first sort by name
            sorted_winners = sorted(
               winners,
               key = lambda j: question['answers'][j]['text'])
            # reverse sort by points
            sorted_winners = sorted(
               sorted_winners,
               key = lambda j: question['answers'][j]['total_count'],
               reverse = True)
            return sorted_winners

        def get_zipped_parity(mixed_list, max_people):
            women_list = get_women_indexes(mixed_list)
            men_list = [ person for person in mixed_list if person not in women_list]
            max2 = max_people / 2
            sorted_women_list = get_list_by_points(women_list)[:max2]
            sorted_men_list = get_list_by_points(men_list)[:max2]
            zipped_list = []
            for j in range(max2):
                zipped_list.append(sorted_women_list[j])
                zipped_list.append(sorted_men_list[j])
            return zipped_list

        def filter_groups(indexed_list, groups_list):
            return [ j
                     for j in indexed_list
                     if question['answers'][j]['category'] not in groups_list ]

        # first round
        winners_index_complete = range(len(question['answers']))
        winners_index_complete = get_list_by_points(winners_index_complete)
        winners_index_1stround = winners_index_complete[:question['num_winners']]

        groups = dict()

        total_points = 0
        # get grouped options
        for index, answer in enumerate(question['answers']):
            category = answer['category']
            # add category
            if category not in groups:
                groups[category] = dict(
                    indexes = [],          # index of the answers of this category/group
                    winners = [],          # winners in the first round
                    points_group = 0)
            group = groups[category]
            # add answer index to category
            group['indexes'].append(index)
            # add points to group
            group['points_group'] += answer['total_count']
            # add total points
            total_points += answer['total_count']
            # add to number of winners
            if index in winners_index_1stround:
                group['winners'].append(index)

        minorities_15 = []
        minorities_5 = []
        percent_15_limit = total_points * 0.15
        percent_5_limit = total_points * 0.05
        num_winners_23_rounds = question['num_winners']

        minorities_winners = []
        # mark minorities corrections
        for group_name in groups:
            group = groups[group_name]

            # check 15%
            if len(group['winners']) < 4 and group['points_group'] >= percent_15_limit:
                minorities_15.append(group_name)
                minorities_winners += get_zipped_parity(group['indexes'], 4)
                num_winners_23_rounds -= 4
            # check 5%
            elif len(group['winners']) < 2 and group['points_group'] >= percent_5_limit:
                minorities_5.append(group_name)
                minorities_winners += get_zipped_parity(group['indexes'], 2)
                num_winners_23_rounds -= 2

        # exclude minorities for second round
        minorities_groups = minorities_15 + minorities_5
        winners_index_2ndround_complete = filter_groups(
            winners_index_complete,
            minorities_groups)
        winners_index_2ndround_complete = get_list_by_points(winners_index_2ndround_complete)
        # winners on the second round
        winners_index_2ndround = winners_index_2ndround_complete[:num_winners_23_rounds]
        women_2nd_round = get_women_indexes(winners_index_2ndround)
        num_women_2nd_round = len(women_2nd_round)
        final_list = copy.deepcopy(winners_index_2ndround)
        # if there are more men, do third round
        if num_winners_23_rounds - num_women_2nd_round > num_women_2nd_round:
            # third round: zipped
            winners_index_3rdround = get_zipped_parity(
                winners_index_2ndround_complete, 
                num_winners_23_rounds)
            final_list = copy.deepcopy(winners_index_3rdround)
        # add minorities
        final_list += minorities_winners
        # order by points, zipped female/male
        final_list = get_zipped_parity(final_list, len(final_list))
        for aindex, answer in enumerate(question['answers']):
            if aindex in final_list:
                answer['winner_position'] = final_list.index(aindex)
            else:
                answer['winner_position'] = None
