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


def podemos_desborda(data_list, women_names=None, question_indexes=None):
    '''
    Definition of this system: 
    http://pabloechenique.info/wp-content/uploads/2016/12/DesBorda-sistema-Echenique.pdf
    It is assumed that the desborda method in agora-tally has been already applied
    '''
    data = data_list[0]
    for qindex, question in enumerate(data['results']['questions']):
        if women_names is None:
            women_names_question = __get_women_names_from_question(question)
        else:
            women_names_question = copy.deepcopy(women_names)

        if "desborda" != question['tally_type'] or len(question['answers']) < 62 or question['num_winners'] != 62:
            continue

        if question_indexes is not None and qindex not in question_indexes:
            continue

        # calculate women indexes
        women_indexes = [ index
            for index, answer in enumerate(question['answers'])
            if answer['text'] in women_names_question ]

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

        def get_zipped_parity(mixed_list, max_people, with_break=False):
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
        # same array but only the winners, which are the first 62 with higher score
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

        # number of points for the 15% of total points trigger
        percent_15_limit = total_points * 0.15
        # number of points for the 5% of total points trigger
        percent_5_limit = total_points * 0.05
        # number of 'normal' winners on rounds 2 and 3
        # which is 62 minus the number of winners chosen by the minority rules
        num_winners_23_rounds = question['num_winners']

        # list of indexes of winners chosen by the minority rules
        minorities_winners_indexes = []
        # index of all candidates (also losers) from groups that have at least
        # one winner 
        minorities_candidates_indexes = []
        # mark minorities corrections
        for category_name, category in categories.items():
            # check 15%
            if len(category['winners_index_1stround']) < 4 and category['points_category'] >= percent_15_limit:
                this_category_minority_winners = get_zipped_parity(category['candidates_index'], 4, True)
                minorities_winners_indexes += this_category_minority_winners
                minorities_candidates_indexes += category['candidates_index']
                # normally len(this_category_minority_winners) will be 4, but it
                # can be less if this category has less than 2 men or less than
                # 2 women
                num_winners_23_rounds -= len(this_category_minority_winners)
            # check 5%
            elif len(category['winners_index_1stround']) < 2 and category['points_category'] >= percent_5_limit:
                this_category_minority_winners = get_zipped_parity(category['candidates_index'], 2, True)
                minorities_winners_indexes += this_category_minority_winners
                minorities_candidates_indexes += category['candidates_index']
                # normally len(this_category_minority_winners) will be 4, but it
                # can be less if this category has less than 2 men or less than
                # 2 women
                num_winners_23_rounds -= len(this_category_minority_winners)

        # exclude winners chosen by the minority rules for calculating winners
        # by normal rules on the second round
        no_minorities_index_2ndround  = list( set(allcands_index_1stround) - set(minorities_candidates_indexes) )
        no_minorities_index_2ndround_sorted = get_list_by_points(no_minorities_index_2ndround)
        # normal (not minorities) winners on the second round
        winners_index_2ndround = no_minorities_index_2ndround_sorted[:num_winners_23_rounds]
        women_2nd_round = get_women_indexes(winners_index_2ndround)
        num_women_2nd_round = len(women_2nd_round)
        normal_winners = copy.deepcopy(winners_index_2ndround)
        # if there are more men, do third round
        if num_winners_23_rounds - num_women_2nd_round > num_women_2nd_round:
            # third round: zipped, but with_break=False so that we get exactly
            # num_winners_23_rounds winners even if this means not having
            # strict parity because we need 62 winners in the end!
            winners_index_3rdround = get_zipped_parity(
                no_minorities_index_2ndround, 
                num_winners_23_rounds)
            normal_winners = copy.deepcopy(winners_index_3rdround)
        # sort
        minorities_winners_sorted = get_list_by_points(minorities_winners_indexes)
        normal_winners_sorted = get_list_by_points(normal_winners)
        # add normal winners and minorities winners
        # the order of final_list is stable/reproducible: it has first the 
        # minorities (sorted), and then the normal winners, also sorted
        final_list = minorities_winners_sorted + normal_winners_sorted
        # set the winner_position
        for aindex, answer in enumerate(question['answers']):
            if aindex in final_list:
                answer['winner_position'] = final_list.index(aindex)
            else:
                answer['winner_position'] = None
