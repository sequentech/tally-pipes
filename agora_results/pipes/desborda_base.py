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

class DesbordaBase(object):
    def __init__(self):
        pass

    def name(self):
        return 'desborda_base'

    def get_min_num_winners_for_team(self, category, question):
        # TODO: Implement this
        pass

    def insert_min_team_winners(self, min_num_winners_for_team, category, a_sure_winners, b_unsure, question, women_indexes):
        # TODO: Implement this
        pass

    def __get_women_names_from_question(self, question):
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

    def get_list_by_points(self, candidate_indexes, question):
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

    def get_all_candidates(self, num_candidates, question):
        return self.get_list_by_points(range( num_candidates ), question)

    def get_categories(self, question):
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

    def get_winners_for_team(self, category, a_sure_winners, b_unsure, num_winners):
        ab = a_sure_winners + b_unsure
        present_winners = ab[:num_winners]
        team_winners = [
            team_member
            for team_member in category['candidates_index']
            if team_member in present_winners
        ]
        return team_winners

    def move_minority_losers(self, category, a_sure_winners, b_unsure, c_sure_losers):
        cat_losers = [
            team_member
            for team_member in category['candidates_index']
            if team_member not in a_sure_winners
        ]
        b = [j for j in b_unsure if j not in cat_losers]
        c = c_sure_losers + cat_losers
        return b, c

    def split_women_men(self, candidates_index_list, women_indexes):
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

    def is_woman(self, index, women_indexes):
        return index in women_indexes

    def fix_parity(self, num_winners, a_sure_winners, b_unsure, women_indexes):
        max_men = int(floor(num_winners / 2))
        a_women, a_men = self.split_women_men(a_sure_winners, women_indexes)
        num_men = len(a_men)
        
        new_b = []
        for candidate in b_unsure:
            if self.is_woman(candidate, women_indexes):
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

    def join_lists(self, a, b, c):
        l = a.copy()
        l.extend(b)
        l.extend(c)
        return l

    def set_winners_positions(self, winners, question):
        # set the winner_position
        for aindex, answer in enumerate(question['answers']):
            if aindex in winners:
                answer['winner_position'] = winners.index(aindex)
            else:
                answer['winner_position'] = None

    def desborda(self, data_list, women_names=None, question_indexes=None):
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
                women_names_question = self.__get_women_names_from_question(question)
            else:
                women_names_question = copy.deepcopy(women_names)

            if self.name() != question['tally_type'] \
                or len(question['answers']) < question['num_winners']:
                continue

            if question_indexes is not None and qindex not in question_indexes:
                continue

            # calculate women indexes
            women_indexes = [ index
                for index, answer in enumerate(question['answers'])
                if answer['text'] in women_names_question ]

            num_candidates = len(question['answers'])
            num_winners = question['num_winners']
            a_sure_winners = []
            b_unsure = self.get_all_candidates(num_candidates, question)
            c_sure_losers = []

            categories = self.get_categories(question)

            for category_name, category in categories.items():
                min_num_winners_for_team = \
                    self.get_min_num_winners_for_team(category, question)
                winners_for_team = \
                    self.get_winners_for_team(
                        category,
                        a_sure_winners,
                        b_unsure,
                        num_winners)
                if len(winners_for_team) < min_num_winners_for_team:
                    category['is_minority'] = True
                a_sure_winners, b_unsure = \
                    self.insert_min_team_winners(
                        min_num_winners_for_team, 
                        category,
                        a_sure_winners,
                        b_unsure,
                        question,
                        women_indexes)
                if category['is_minority']:
                    b_unsure, c_sure_losers = \
                        self.move_minority_losers(
                            category,
                            a_sure_winners,
                            b_unsure,
                            c_sure_losers)

            b_unsure, fixed = self.fix_parity(num_winners, a_sure_winners, b_unsure, women_indexes)
            if not fixed:
                # mark as not parity-fixed
                question['parity_fixed'] = False
            full_list = self.join_lists(a_sure_winners, b_unsure, c_sure_losers)
            final_winners = \
                self.get_list_by_points(full_list[:num_winners], question)
            final_losers = \
                self.get_list_by_points(full_list[: num_candidates - num_winners], question)
            self.set_winners_positions(final_winners, question)
