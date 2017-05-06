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
from math import *

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


def podemos_desborda2(data_list, women_names, question_indexes=None):
    '''
    Definition of this system: 
    http://pabloechenique.info/wp-content/uploads/2016/12/DesBorda-sistema-Echenique.pdf
    It is assumed that the desborda method in agora-tally has been already applied
    '''
    data = data_list[0]
    for qindex, question in enumerate(data['results']['questions']):
        if women_names == None:
            women_names = __get_women_names_from_question(question)

        if "desborda2" != question['tally_type'] or len(question['answers']) < question['num_winners']:
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
            return list( set(people_indexes_list) & set(women_indexes) )

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

        def get_minorities(minorities_list, number):
            '''
            '''
            normal_order_list = get_list_by_points(minorities_list)
            max_men_allowed = int(floor(number/2))
            round_1_list = normal_order_list[:number]
            women_round_1 = get_women_indexes(round_1_list)
            num_men_round_1 = len(round_1_list) - len(women_round_1)
            if num_men_round_1 > max_men_allowed:
                return get_zipped_parity(minorities_list, number, True)
            else:
                return round_1_list


        def get_zipped_parity(mixed_list, max_people, with_break=False, no_sort = False):
            '''
            returns a list composed of the indexes of mixed_list ordered by
            points, but in a zipped way (female, male, female, male...)

            mixed_list is a list of indexes to array question['answers']

            The returned list will have at most max_people elements

            If with_break=False and there are more male than female (or
            viceversa), the remaining people will be of the same sex (ie fmfmmm)

            If with_break=True and for example the number of females is less
            than max_people/2, then the returned list will have a length lower
            than max_people, in order to preserve parity strictly.
            '''
            women_index_list = get_women_indexes(mixed_list)
            men_index_list = list( set(mixed_list) - set(women_index_list) )
            women_index_list_sorted = get_list_by_points(women_index_list)
            men_index_list_sorted = get_list_by_points(men_index_list)
            if no_sort:
                women_index_list_sorted = copy.deepcopy(women_index_list)
                men_index_list_sorted = copy.deepcopy(men_index_list)

            zipped_parity = []
            for a, b in zip_longest(women_index_list_sorted, men_index_list_sorted):
                has_None = False
                if a is None:
                    has_None = True
                else:
                    zipped_parity.append(a)
                    if len(zipped_parity) >= max_people:
                        break
                if b is None:
                    has_None = True
                else:
                    zipped_parity.append(b)
                    if len(zipped_parity) >= max_people:
                        break
                if with_break and has_None:
                    break
            return zipped_parity

        # first round:
        # array of indexes (list of indexes to question['answers']) 
        # of all candidates for first round
        allcands_index_1stround = range(len(question['answers']))
        # same array, sorted by points (and text)
        allcands_index_1stround_sorted = get_list_by_points(allcands_index_1stround)
        # same array but only the winners, which are the first (num_winners) with higher score
        # winners on 1st round 
        winners_index_1stround = allcands_index_1stround_sorted[:question['num_winners']]

        categories = dict()

        # total points on the whole first round
        total_points = 0
        # get info (winners, candidates, points) by category
        for index, answer in enumerate(question['answers']):
            # category
            category_name = answer['category']
            # add category
            if category_name not in categories:
                categories[category_name] = dict(
                    candidates_index = [],       # list of indexes of the candidates from this category
                    winners_index_1stround = [], # winners in the first round
                    points_category = 0)
            category = categories[category_name]
            # add answer index to category
            category['candidates_index'].append(index)
            # add points to category
            category['points_category'] += answer['total_count']
            # add total points
            total_points += answer['total_count']
            # add to number of winners
            if index in winners_index_1stround:
                category['winners_index_1stround'].append(index)


        ########################################################################
        
        # list of indexes of winners chosen by the minority rules
        minorities_winners_indexes = []
        # number of 'normal' winners on rounds 2 and 3
        # which is question['num_winners'] minus the number of winners chosen by
        # the minority rules
        num_winners_23_rounds = question['num_winners']

        if question['num_winners'] > 29:
            # number of points for the 15% of total points trigger
            percent_15_limit = total_points * 0.15
            # number of points for the 10% of total points trigger
            percent_10_limit = total_points * 0.10
            # number of points for the 5% of total points trigger
            percent_5_limit = total_points * 0.05

            # mark minorities corrections
            for category_name, category in categories.items():
                # check 15%
                if len(category['winners_index_1stround']) < 3 and category['points_category'] >= percent_15_limit:
                    this_category_minority_winners = get_minorities(category['candidates_index'], 3)
                    minorities_winners_indexes += this_category_minority_winners
                    # normally len(this_category_minority_winners) will be 4, but it
                    # can be less if this category has less than 2 men or less than
                    # 2 women
                    num_winners_23_rounds -= len(this_category_minority_winners)
                # check 10%
                if len(category['winners_index_1stround']) < 2 and category['points_category'] >= percent_10_limit:
                    this_category_minority_winners = get_minorities(category['candidates_index'], 2)
                    minorities_winners_indexes += this_category_minority_winners
                    # normally len(this_category_minority_winners) will be 4, but it
                    # can be less if this category has less than 2 men or less than
                    # 2 women
                    num_winners_23_rounds -= len(this_category_minority_winners)
                # check 5%
                if len(category['winners_index_1stround']) < 1 and category['points_category'] >= percent_5_limit:
                    this_category_minority_winners = get_list_by_points(category['candidates_index'])[:1]
                    minorities_winners_indexes += this_category_minority_winners
                    # normally len(this_category_minority_winners) will be 4, but it
                    # can be less if this category has less than 2 men or less than
                    # 2 women
                    num_winners_23_rounds -= len(this_category_minority_winners)
        else:
            # number of points for the 15% of total points trigger
            percent_20_limit = total_points * 0.20
            # number of points for the 10% of total points trigger
            percent_10_limit = total_points * 0.10
            # mark minorities corrections
            for category_name, category in categories.items():
                # check 15%
                if len(category['winners_index_1stround']) < 2 and category['points_category'] >= percent_20_limit:
                    this_category_minority_winners = get_minorities(category['candidates_index'], 2)
                    minorities_winners_indexes += this_category_minority_winners
                    # normally len(this_category_minority_winners) will be 4, but it
                    # can be less if this category has less than 2 men or less than
                    # 2 women
                    num_winners_23_rounds -= len(this_category_minority_winners)
                # check 10%
                if len(category['winners_index_1stround']) < 1 and category['points_category'] >= percent_10_limit:
                    this_category_minority_winners = get_list_by_points(category['candidates_index'])[:1]
                    minorities_winners_indexes += this_category_minority_winners
                    # normally len(this_category_minority_winners) will be 4, but it
                    # can be less if this category has less than 2 men or less than
                    # 2 women
                    num_winners_23_rounds -= len(this_category_minority_winners)

        # exclude winners chosen by the minority rules for calculating winners
        # by normal rules on the second round
        no_minorities_index_2ndround  = list( set(allcands_index_1stround) - set(minorities_winners_indexes) )
        no_minorities_index_2ndround_sorted = get_list_by_points(no_minorities_index_2ndround)
        # normal (not minorities) winners on the second round
        winners_index_2ndround =
            minorities_winners_indexes +
            no_minorities_index_2ndround_sorted[:num_winners_23_rounds]
        women_2nd_round = get_women_indexes(winners_index_2ndround)
        num_women_2nd_round = len(women_2nd_round)
        num_men_2nd_round = len(winners_index_2ndround) - num_women_2nd_round
        # the final winners
        final_list = copy.deepcopy(winners_index_2ndround)

        # if there are more men, do third round
        if num_men_2nd_round > num_women_2nd_round:
            # third round: zipped, but with_break=False so that we get exactly
            # num_winners_23_rounds winners even if this means not having
            # strict parity because we need 62 winners in the end!
            allcands_sorted_index_3rdround =
                minorities_winners_indexes +
                no_minorities_index_2ndround_sorted

            winners_index_3rdround = get_zipped_parity(
                allcands_sorted_index_3rdround, 
                question['num_winners'],
                no_sort = True)
            final_list = copy.deepcopy(winners_index_3rdround)

        # set the winner_position
        for aindex, answer in enumerate(question['answers']):
            if aindex in final_list:
                answer['winner_position'] = final_list.index(aindex)
            else:
                answer['winner_position'] = None
