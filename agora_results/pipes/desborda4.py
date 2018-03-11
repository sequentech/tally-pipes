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

        def get_all_candidates():
            return get_list_by_points(range( num_candidates ))

        def get_min_num_winners_for_team():
            
        num_candidates = len(question['answers'])
        num_winners = question['num_winners']
        a_sure_winners = []
        b_unsure = get_all_candidates()
        c_sure_losers = []

        categories = get_categories()

        for category_name, category in categories.items():
            min_num_winners_for_team = get_min_num_winners_for_team(category_name, category)
            winners_for_team = get_winners_for_team(category_name, category)
            if len(winners_for_team) < min_num_winners_for_team:
                category['is_minority'] = True
            insert_min_team_winners(min_num_winners_for_team, category)
            if category['is_minority']:
                move_minority_losers(category)
        fixed = fix_parity(a_sure_winners, b_unsure)
        if not fixed:
           # mark as not parity-fixed
        full_list = join_lists(a_sure_winners, b_unsure, c_sure_losers)
        final_winners = get_list_by_points(full_list[:num_winners])
        final_losers = get_list_by_points(full_list[: num_candidates - num_winners])
        mark_winners_and_losers(final_winners, final_losers)