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
           
def podemos_desborda4(data_list, women_names=None, question_indexes=None):
    '''
    Para la votación PODE-17 hay que hacer que en desborda1,2 y 3 se aplique 
    el siguiente algoritmo:
    - Dados N, que es el número de ganadores, y X, que son los puntos que se le
      dan a la primera candidatura de cada papeleta.
    - A cada candidatura de la papeleta se les da (X+1-posicion) puntos. Si el
      número es menor a 1, se le da 1.
    - Se meten en la lista B las candidaturas, ordenadas por puntos 
      descendentes.
    - Se crean las listas A (ganadores asegurados) y C (no ganadores 
      asegurados), vacías.
    - Por cada equipo e:
       - Se calcula M(e), que es el número de escaños mínimo que le toca al
         equipo según su % de puntos.
       - Si el equipo tiene menos de M(e) candidaturas entre los N primeros de
         la lista B, se marca como minoritario.
    - Por cada equipo e:
       - Se mueven a la lista A las M(e) candidaturas con más votos del equipo.
         Si es minoritario, se tiene en cuenta la corrección por paridad al
         elegirlas.
       - Si el equipo es minoritario, se mueven a la lista C el resto de
         candidaturas del equipo.
    - Se corrige paridad de la lista B como indique el reglamento, teniendo en
      cuenta la lista A también, pero sin modificarla.
       - Si no se logra que se cumplan los criterios de paridad, se indica para
         que se corrija manualmente.
    - Se unen las listas A, B y C.
    - Se marcan las primeras N candidaturas como ganadoras y se reordenan por
      puntos descendentes.
    - Se marcan las demás candidaturas como no ganadoras y se reordenan por
      puntos descendentes.
    '''
    data = data_list[0]
    for qindex, question in enumerate(data['results']['questions']):
        if women_names is None:
            women_names_question = __get_women_names_from_question(question)
        else:
            women_names_question = copy.deepcopy(women_names)

        if "desborda4" != question['tally_type'] \
            or len(question['answers']) < question['num_winners']:
            continue

        if question_indexes is not None and qindex not in question_indexes:
            continue

        # calculate women indexes
        women_indexes = [ index
            for index, answer in enumerate(question['answers'])
            if answer['text'] in women_names_question ]

        def get_list_by_points(candidate_indexes):
            '''
            sorts the list of indexes of candidates by points, and when they are
            the same, by text
            '''
            # first sort by name
            sorted_by_name = sorted(
                candidate_indexes,
                key = lambda j: question['answers'][j]['text'])
            # reverse sort by points
            sorted_by_points = sorted(
                sorted_by_name,
                key = lambda j: question['answers'][j]['total_count'],
                reverse = True)
            return sorted_by_points

        def get_all_candidates(num_candidates):
            return get_list_by_points(range( num_candidates ))

        def get_categories():
            # total points on the whole round
            total_points = 0
            cats = dict()
            for index, answer in enumerate(question['answers']):
                cat_name = answer['category']
                if cat_name not in cats:
                    cats[cat_name] = dict(
                        candidates_index = [],  # list of indexes of the candidates from this category
                        is_minority = False,    # whether the category has less winners than it's mandatory
                        points_category = 0)
                cat = cats[cat_name]
                # add answer index to category
                cat['candidates_index'].append(index)
                # add points to category
                cat['points_category'] += answer['total_count']
                # add total points
                total_points += answer['total_count']
            question['totals']['valid_points'] = total_points
            return cats

        def get_winners_for_team(category, a_sure_winners, b_unsure, num_winners):
            ab = a_sure_winners + b_unsure
            present_winners = ab[:num_winners]
            team_winners = [
                team_member
                for team_member in category['candidates_index']
                if team_member in present_winners
            ]
            return team_winners

        def move_minority_losers(category, a_sure_winners, b_unsure, c_sure_losers):
            cat_losers = [
                team_member
                for team_member in category['candidates_index']
                if team_member not in a_sure_winners
            ]
            b = [j for j in b_unsure if j not in cat_losers]
            c = c_sure_losers + cat_losers
            return b, c

        def split_women_men(candidates_index_list, women_indexes):
            '''
            filters the list of indexes of candidates returning
            the list of women, and the list of men
            '''
            women_index_list = [
                candidate
                for candidate in candidates_index_list
                if candidate in women_indexes
            ]
            men_index_list = [
                candidate
                for candidate in candidates_index_list
                if candidate not in women_index_list
            ]
            return women_index_list, men_index_list

        def is_woman(index, women_indexes):
            return index in women_indexes

        def fix_parity(num_winners, a_sure_winners, b_unsure, women_indexes):
            max_men = int(floor(num_winners / 2))
            a_women, a_men = split_women_men(a_sure_winners, women_indexes)
            num_men = len(a_men)
            
            new_b = []
            for candidate in b_unsure:
                if is_woman(candidate, women_indexes):
                    new_b.append(candidate)
                else:
                    if num_men < max_men:
                        num_men += 1
                        new_b.append(candidate)
            remaining = [
                candidate
                for candidate in b_unsure
                if candidate not in new_b
            ]
            new_b.extend(remaining)

            return new_b, True

        def join_lists(a, b, c):
            l = a.copy()
            l.extend(b)
            l.extend(c)
            return l

        def set_winners_positions(winners):
            # set the winner_position
            for aindex, answer in enumerate(question['answers']):
                if aindex in winners:
                    answer['winner_position'] = winners.index(aindex)
                else:
                    answer['winner_position'] = None

        def get_min_num_winners_for_team(category_name, question, desborda_kind):
            total_points = question['totals']['valid_points']
            # number of points for the 20% of total points trigger
            percent_20_limit = total_points * 0.20
            # number of points for the 15% of total points trigger
            percent_15_limit = total_points * 0.15
            # number of points for the 10% of total points trigger
            percent_10_limit = total_points * 0.10
            # number of points for the 5% of total points trigger
            percent_5_limit = total_points * 0.05

            cat = categories[category_name]
            num_winners = question['num_winners']
            if 'desborda2' == desborda_kind:
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
            elif 'desborda' == desborda_kind:
                    if category['points_category'] > percent_15_limit:
                       return 4
                    elif category['points_category'] > percent_5_limit:
                       return 2
            return 0

        def insert_min_team_winners(min_num_winners_for_team, category, a_sure_winners, b_unsure, desborda_kind):
            ordered_team_candidates = \
                get_list_by_points(category['candidates_index'])
            minority_winners = []
            if category['is_minority']: # apply parity rules
                if 'desborda3' == desborda_kind:
                    return
                elif 'desborda2' == desborda_kind:
                    if 1 == min_num_winners_for_team:
                        minority_winners.append(ordered_team_candidates[0])
                    else:
                        prov_min_winners = \
                            ordered_team_candidates[:min_num_winners_for_team]
                        prov_women, prov_men = split_women_men(prov_min_winners)
                        if len(prov_men) <= 1:
                            minority_winners.extend(prov_min_winners)
                        else:
                            minority_winners.append(prov_men[0])
                            minority_winners.extend(prov_women[:min_num_winners_for_team-1])
                elif 'desborda' == desborda_kind:
                    team_women, team_men = split_women_men(ordered_team_candidates)
                    if 2 == min_num_winners_for_team:
                        minority_winners.append(team_women[0])
                        minority_winners.append(team_men[0])
                    elif 4 == min_num_winners_for_team:
                        minority_winners.extend(team_women[:2])
                        minority_winners.extend(team_men[:2])
            else:
                minority_winners = \
                    ordered_team_candidates[:min_num_winners_for_team]
            b = [j for j in b_unsure if j not in minority_winners]
            a = a_sure_winners + minority_winners
            return a, b

        num_candidates = len(question['answers'])
        num_winners = question['num_winners']
        a_sure_winners = []
        b_unsure = get_all_candidates(num_candidates)
        c_sure_losers = []

        categories = get_categories()

        for category_name, category in categories.items():
            min_num_winners_for_team = \
                get_min_num_winners_for_team(category_name, question, 'desborda3')
            winners_for_team = get_winners_for_team(
                category,
                a_sure_winners,
                b_unsure,
                num_winners)
            if len(winners_for_team) < min_num_winners_for_team:
                category['is_minority'] = True
            a_sure_winners, b_unsure = \
                insert_min_team_winners(
                    min_num_winners_for_team, 
                    category,
                    a_sure_winners,
                    b_unsure,
                    'desborda3')
            if category['is_minority']:
                b_unsure, c_sure_losers = \
                    move_minority_losers(
                        category,
                        a_sure_winners,
                        b_unsure,
                        c_sure_losers)

        #import ipdb; ipdb.set_trace()
        b_unsure, fixed = fix_parity(num_winners, a_sure_winners, b_unsure, women_indexes)
        if not fixed:
            # mark as not parity-fixed
            question['parity_fixed'] = False
        full_list = join_lists(a_sure_winners, b_unsure, c_sure_losers)
        final_winners = get_list_by_points(full_list[:num_winners])
        final_losers = \
            get_list_by_points(full_list[: num_candidates - num_winners])
        set_winners_positions(final_winners)
