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
from itertools import zip_longest

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


def podemos_desborda(data_list, women_names, question_indexes=None):
    '''
    Definition of this system: 
    http://pabloechenique.info/wp-content/uploads/2016/12/DesBorda-sistema-Echenique.pdf
    It is assumed that the desborda method in agora-tally has been already applied
    '''
    data = data_list[0]
    for qindex, question in enumerate(data['results']['questions']):
        if women_names == None:
            women_names = __get_women_names_from_question(question)

        if "desborda" != question['tally_type'] or len(question['answers']) < 62 or question['num_winners'] != 62:
            continue

        if question_indexes is not None and qindex not in question_indexes:
            continue

        # calculate women indexes
        women_indexes = [ index
            for index, answer in enumerate(question['answers'])
            if answer['text'] in women_names ]

        def get_women_indexes(people_indexes_list):
            '''
            filters the list of indexes of candidates returning only women
            '''
            return [ person_index for person_index in people_indexes_list if person_index in women_indexes ]

        def get_list_by_points(winners_indexes):
            '''
            sorts the list of indexes of candidates by points, and when they are
            the same, by text
            '''
            # first sort by name
            sorted_winners = sorted(
                winners_indexes,
                key = lambda j: question['answers'][j]['text'])
            # reverse sort by points
            sorted_winners = sorted(
                sorted_winners,
                key = lambda j: question['answers'][j]['total_count'],
                reverse = True)
            return sorted_winners

        def get_zipped_parity(mixed_list, max_people, with_break=False):
            '''
            returns a list composed of the indexes of mixed_list ordered by
            points, but in a zipped way (female, male, female, male...)

            mixed_list is a list of indexes to array question['answers']

            The returned list will have at most max_people elements

            If with_break=False and there are more male than female (or
            viceversa), the remaining people will be of the same sex (ie fmfmmm)

            If with_break=True and for example the number of females are less
            than max_people/2, then the returned list will have a length lower
            than max_people, in order to preserve parity strictly.
            '''
            women_index_list = get_women_indexes(mixed_list)
            men_index_list = list( set(mixed_list) - set(women_list) )
            women_index__list_sorted = get_list_by_points(women_index_list)
            men_index_list_sorted = get_list_by_points(men_index_list)
            zipped_parity = []
            for a, b in zip_longest(women_index__list_sorted, men_index_list_sorted):
                has_None = False
                if a is not None:
                    has_None = True
                    zipped_parity.append(a)
                    if len(zipped_parity) >= max_people:
                        break
                if b is not None:
                    has_None = True
                    zipped_parity.append(b)
                    if len(zipped_parity) >= max_people:
                        break
                if with_break and has_None:
                    break
            return zipped_parity

        # first round
        allcands_index_1stround = range(len(question['answers']))
        allcands_index_1stround_sorted = get_list_by_points(allcands_index_1stround)
        # winners on 1st round (list of indexes to question['answers'])
        winners_index_1stround = allcands_index_1stround_sorted[:question['num_winners']]

        categories = dict()

        total_points = 0
        # get grouped options
        for index, answer in enumerate(question['answers']):
            # category
            category_name = answer['category']
            # add category
            if category_name not in categories:
                categories[category_name] = dict(
                    indexes = [],          # index of the answers of this category
                    winners = [],          # winners in the first round
                    points_group = 0)
            category = categories[category_name]
            # add answer index to category
            category['indexes'].append(index)
            # add points to category
            category['points_group'] += answer['total_count']
            # add total points
            total_points += answer['total_count']
            # add to number of winners
            if index in winners_index_1stround:
                group['winners'].append(index)

        percent_15_limit = total_points * 0.15
        percent_5_limit = total_points * 0.05
        num_winners_23_rounds = question['num_winners']

        minorities_winners_indexes = []
        # mark minorities corrections
        for category_name, category in categories.items():
            # check 15%
            if len(category['winners']) < 4 and category['points_group'] >= percent_15_limit:
                this_group_minority_winners = get_zipped_parity(category['indexes'], 4)
                minorities_winners_indexes += this_group_minority_winners
                num_winners_23_rounds -= len(this_group_minority_winners)
            # check 5%
            elif len(category['winners']) < 2 and category['points_group'] >= percent_5_limit:
                this_group_minority_winners = get_zipped_parity(category['indexes'], 2)
                minorities_winners_indexes += this_group_minority_winners
                num_winners_23_rounds -= len(this_group_minority_winners)

        # winners_index_2ndround_complete
        # exclude winners from minorities for second round
        no_minorities_index_2ndround  = list( set(allcands_index_1stround) - set(minorities_winners_indexes) )
        no_minorities_index_2ndround_sorted = get_list_by_points(no_minorities_index_2ndround)
        # winners on the second round
        winners_index_2ndround = no_minorities_index_2ndround_sorted[:num_winners_23_rounds]
        women_2nd_round = get_women_indexes(winners_index_2ndround)
        num_women_2nd_round = len(women_2nd_round)
        normal_winners = copy.deepcopy(winners_index_2ndround)
        # if there are more men, do third round
        if num_winners_23_rounds - num_women_2nd_round > num_women_2nd_round:
            # third round: zipped
            winners_index_3rdround = get_zipped_parity(
                no_minorities_index_2ndround, 
                num_winners_23_rounds)
            normal_winners = copy.deepcopy(winners_index_3rdround)
        # sort
        minorities_winners_sorted = get_list_by_points(minorities_winners_indexes)
        normal_winners_sorted = get_list_by_points(normal_winners)
        # add normal winners and minorities winners
        final_list = minorities_winners_sorted + normal_winners_sorted
        for aindex, answer in enumerate(question['answers']):
            if aindex in final_list:
                answer['winner_position'] = final_list.index(aindex)
            else:
                answer['winner_position'] = None
