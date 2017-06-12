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
# Desborda 3 is a modification/generalization of desborda 2.
# Basically, it's like Desborda 2, but without minorities corrections.

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


def podemos_desborda3(data_list, women_names=None, question_indexes=None):
    '''
    Desborda 2 is a modification/generalization of desborda. 
    Desborda is defined here:
    http://pabloechenique.info/wp-content/uploads/2016/12/DesBorda-sistema-Echenique.pdf
    It is assumed that the desborda2 method in agora-tally has been already applied

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
    data = data_list[0]
    for qindex, question in enumerate(data['results']['questions']):
        if women_names is None:
            women_names_question = __get_women_names_from_question(question)
        else:
            women_names_question = copy.deepcopy(women_names)

        if "desborda3" != question['tally_type'] \
            or len(question['answers']) < question['num_winners']:
            continue

        if question_indexes is not None and qindex not in question_indexes:
            continue

        # calculate women indexes
        women_indexes = [ index
            for index, answer in enumerate(question['answers'])
            if answer['text'] in women_names_question ]
        
        
        # remove elements from index_list preserving order
        def remove_elements_from_list(index_list, elements):
            elements_set = set(elements)
            out_set = set()
            out = []
            for el in index_list:
                if el not in out_set and el not in elements_set:
                    out.append(el)
                    out_set.add(el)
            return out
        
        # include elements from index_list preserving order
        def include_elements_from_list(index_list, elements):
            elements_set = set(elements)
            out_set = set()
            out = []
            for el in index_list:
                if el not in out_set and el in elements_set:
                    out.append(el)
                    out_set.add(el)
            return out

        def get_women_indexes(people_indexes_list):
            '''
            filters the list of indexes of candidates returning only women
            '''
            return include_elements_from_list(people_indexes_list,women_indexes)
            

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


        def get_zipped_parity(
            mixed_list,
            max_people,
            with_break=False,
            no_sort = False):
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
            men_index_list = remove_elements_from_list(
                mixed_list,
                women_index_list)
            if no_sort:
                women_index_list_sorted = copy.deepcopy(women_index_list)
                men_index_list_sorted = copy.deepcopy(men_index_list)
            else:
                women_index_list_sorted = get_list_by_points(women_index_list)
                men_index_list_sorted = get_list_by_points(men_index_list)

            zipped_parity = []
            for a, b in zip_longest(     \
                women_index_list_sorted, \
               men_index_list_sorted):
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
        question['totals']['valid_points'] = total_points

        women_1st_round = get_women_indexes(winners_index_1stround)
        num_women_1st_round = len(women_1st_round)
        num_men_1st_round = len(winners_index_1stround) - num_women_1st_round
        # the final winners
        final_list = copy.deepcopy(winners_index_1stround)

        # if there are more men, do second round
        if num_men_1st_round > num_women_1st_round:
            winners_index_2ndround = get_zipped_parity(
                allcands_index_1stround_sorted, 
                question['num_winners'],
                True,
                True)
            final_list = copy.deepcopy(winners_index_2ndround)

        # sort final winners by points
        sorted_final_list = get_list_by_points(final_list)

        # set the winner_position
        for aindex, answer in enumerate(question['answers']):
            if aindex in sorted_final_list:
                answer['winner_position'] = sorted_final_list.index(aindex)
            else:
                answer['winner_position'] = None
