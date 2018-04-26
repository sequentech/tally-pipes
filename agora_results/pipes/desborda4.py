# -*- coding:utf-8 -*-

# This file is part of agora-results.
# Copyright (C) 2018  Agora Voting SL <agora@agoravoting.com>

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
# Desborda 4 is a modification of desborda 2.
# It is assumed that the desborda2 method in agora-tally has been already applied
#
# The algorithm is:
# A. Elección del/de la cabeza de lista. Para ello, se presentarán candidaturas
# unipersonales y resultará elegida la que más votos obtenga. Cada votante sólo podrá
# votar a una de las candidaturas.
# B. Elección del resto de la papeleta. Para ello, se utilizará el llamado sistema DesBorda:
# - Se podrán presentar listas ordenadas y abiertas de longitud máxima 25 y longitud
# mínima 9, también se podrán presentar candidaturas individuales.
# - Cada persona podrá emitir 25 votos (a personas de diferentes listas si así lo desea) y
# estableciendo un orden de prioridad, de manera que el voto valdrá más cuanto más alta
# coloque el/la votante a la persona candidata en su papeleta.
# - La puntuación que se adjudicará a cada candidato/a será decreciente según el orden
# de votación empezando en 25 + 7 = 32 puntos y bajando de un punto en un punto para
# los/as candidatos/as siguientes que seleccione el/la votante. Así, la primera persona
# seleccionada por el/la votante obtendrá 32 puntos, la siguiente 31, la siguiente 30... y así
# sucesivamente.
# Los/as candidatos/as que conformarán finalmente la papeleta (exceptuando el/la cabeza
# de lista) se calculan siguiendo estos pasos en orden:
# 1. Se ordenan según el total de puntos que haya obtenido cada uno/a.
# 2. A toda lista que haya obtenido más de un 5% de los puntos agregados, se le garantiza
# un escaño entre los 25 primeros (siempre sin contar al/a la cabeza de lista). A toda lista
# que haya obtenido más de un 10% de los votos agregados, se le garantizan 2 escaños
# entre los 25 primeros y, a toda lista que haya obtenido más de un 15%, se le garantizan
# 3. Se sustituyen, en los últimos puestos del primer tramo de 25, los/as candidatos/as
# necesarios para cumplir estas cuotas y sólo en caso de no cumplirse. Esto se hace
# buscando que el sexo de la persona introducida no provoque que correspondan 2
# hombres al caso de 2 escaños, ni más de 1 hombre al caso de 3 escaños. Las personas
# introducidas al final del primer tramo de 25 se ordenan según el total de puntos que
# hayan obtenido.
# 3. La ordenación del resto de la papeleta de 128 puestos se deja como está.
# 4. Sobre el ordenamiento así producido, se aplica un criterio correctivo de género por el
# cual el resultado se ordenará en cremallera, salvo cuando pudiera perjudicar a las
# mujeres . Para evaluar si la cremallera pudiera perjudicar a las mujeres se seguirá el
# siguiente criterio: en cada tramo de cinco personas se evaluará si se mantiene una
# cremallera estricta o se posibilita —porque las mujeres hubieran obtenido más votos que
# los hombres— una colocación natural en función del número de votos obtenido, en cuyo
# caso podría haber varias mujeres seguidas en dicho tramo con el límite de un 60% de
# mujeres por tramo, es decir, hasta tres mujeres en cada tramo de cinco,
# independientemente de su colocación en dicho tramo.
#
# La visión general es:
# 1. Cálculo de puntos por candidato (agora-tally)
# 2. Ordenado por puntos de candidatos (agora-tally)
# 3. Cálculo de puntos por equipos
# 4. Reserva de puntos a los equipos minoritarios en los últimos puestos de los
#    primeros 25 (lista A).
# 5. Unión de la lista A y B en una conjunta C
# 6. Aplicación de cremallera, teniendo en cuenta la pregunta del cabeza de lista
# 7. Aplicación de paridad 5 a 5 mejorando la posición de las mujeres por
#    puntuación si procede.


import copy
from itertools import zip_longest
from operator import itemgetter
from math import *
from .desborda_base import DesbordaBase

class Desborda4(DesbordaBase):
    def __init__(self):
        pass

    def name(self):
        return 'desborda4'

    def get_sorted_categories(self, question):
        categories = []
        for name, category in self.get_categories(question).items():
            category['name'] = name
            categories.append(category)

        for category in categories:
            category['candidates'] = [
                question['answers'][i]
                for i in category['candidates_index']
            ]
        return sorted(
            categories,
            key = lambda cat: cat['points_category'],
            reverse = True)

    def get_list_by_points(self, candidates):
        '''
        sorts the list of candidates by points, and when they are
        the same, by text
        '''
        # first sort by name
        sorted_by_name = sorted(
            candidates,
            key = lambda j: j['text'])
        # reverse sort by points
        sorted_by_points = sorted(
            sorted_by_name,
            key = lambda j: j['total_count'],
            reverse = True)
        return sorted_by_points

    def split_women_men(self, candidates_list, women_indexes):
        '''
        filters the list of candidates returning
        the list of women, and the list of men
        '''
        women_index_list = [
            candidate
            for candidate in candidates_list
            if candidate['id'] in women_indexes
        ]
        men_index_list = [
            candidate
            for candidate in candidates_list
            if candidate['id'] not in women_indexes
        ]
        return women_index_list, men_index_list

    def get_min_num_winners_for_team(self, category, question):
        total_points = question['totals']['valid_points']
        # number of points for the 15% of total points trigger
        percent_15_limit = total_points * 0.15
        # number of points for the 10% of total points trigger
        percent_10_limit = total_points * 0.10
        # number of points for the 5% of total points trigger
        percent_5_limit = total_points * 0.05

        num_winners = question['num_winners']
        if category['points_category'] > percent_15_limit:
            return 3
        elif category['points_category'] > percent_10_limit:
            return 2
        elif category['points_category'] > percent_5_limit:
            return 1

    def insert_min_team_winners(self, min_num_winners_for_team, category,
        a_list, minority_winners, b_list, question,
        women_indexes):
        '''
        inserts into a minority list the winners that are not in a_list but are
        minority winners
        '''
        ordered_team_candidates = \
            self.get_list_by_points(category['candidates'])
        total_women, total_men = self.split_women_men(ordered_team_candidates, women_indexes)

        # if it's 1 minority winner, then just get the first
        if 1 == min_num_winners_for_team:
            minority_winners.append(ordered_team_candidates[0])
        else:
            if 2 == min_num_winners_for_team:
                assert(len(total_men) > 0)
                assert(len(total_women) > 0)

                # add one man and one woman, sorted by points
                cat_minority = [total_men[0], total_women[0]]

            elif 3 == min_num_winners_for_team:
                assert(len(total_men) > 0)
                assert(len(total_women) > 1)

                # add one man and two women, sorted by points
                cat_minority = [total_men[0], total_women[0], total_women[1]]

            cat_minority_sorted = sorted(
                cat_minority,
                key = lambda j: j['total_count'],
                reverse = True)
            minority_winners.extend(cat_minority_sorted)

        b_list = [j for j in b_list if j not in minority_winners]
        b_list = a_list[len(a_list) - len(minority_winners):] + b_list
        a_list = [j for j in a_list if j not in minority_winners]
        a_list = a_list[:len(a_list) - len(minority_winners)]
        return a_list, minority_winners, b_list

    def set_minority_winners_info(self, winners_for_team):
        for w in winners_for_team:
             w['winner_type'] = 'minority winner'

    def move_minority_losers(self, category, a_list, minority_winners,
        b_list):
        cat_losers = [
            team_member
            for team_member in category['candidates']
            if team_member not in minority_winners
        ]
        a_list = [j for j in a_list if j not in cat_losers]
        b_list = [j for j in b_list if j not in category['candidates']]
        b_list = b_list + cat_losers
        return a_list, b_list

    def get_num_winners(self, category, l):
        return len([
            candidate
            for candidate in l
            if candidate in category['candidates']
        ])

    def reserve_minorities(self, a_list, minority_winners, b_list, categories,
        question, women_indexes):
        # calculate number of first winners for each category
        for category in categories:
            category['num_first_winners'] = self.get_num_winners(category, a_list)

        # reserve minorities
        for category in categories:
            # calculate how many first winners should this category have
            min_num_winners_for_team = self.get_min_num_winners_for_team(
                category, question)

            # check if the category has that enough first winners
            if category['num_first_winners'] >= min_num_winners_for_team:
                continue

            # when a category doesn't have the required number of winners, then
            # mark the required minority winners
            category['is_minority'] = True
            a_list, minority_winners, b_list = \
                self.insert_min_team_winners(min_num_winners_for_team, category,
                    a_list, minority_winners, b_list, question, women_indexes)
            self.set_minority_winners_info(minority_winners)
            a_list, b_list = \
                self.move_minority_losers(category, a_list,
                    minority_winners, b_list)
        return a_list, minority_winners, b_list

    def remove_first_question_winner(self, question, first_question):
        first_question_winner_name = [ candidate['text']
          for candidate in first_question['answers']
          if candidate['winner_position'] == 0
        ]
        assert(len(first_question_winner_name) > 0)

        winner = [ candidate
          for candidate in question['answers']
          if candidate['text'] == first_question_winner_name[0]
        ]
        if len(winner) == 0:
            return None
        else:
            question['answers'].remove(winner[0])
            return winner[0]

    def desborda(self, data_list, question_index=None,
        first_winner_question_index=None):
        # first some sanity checks
        data = data_list[0]
        assert(question_index is not None and isinstance(question_index, int))
        assert(question_index < len(data['results']['questions']))

        assert(first_winner_question_index is not None and isinstance(first_winner_question_index, int))
        assert(first_winner_question_index < len(data['results']['questions']))
        assert(first_winner_question_index != question_index)

        # some initializations
        question = data['results']['questions'][question_index]
        first_question = data['results']['questions'][first_winner_question_index]
        women_indexes = self.get_women_indexes(None, question)
        num_candidates = len(question['answers'])

        removed_first_question_winner = self.remove_first_question_winner(question, first_question)

        assert(num_candidates >= 25)
        # sort answers by total points
        question['answers'] = sorted(
            question['answers'],
            reverse=True,
            key=itemgetter('total_count')
        )
        num_winners = question['num_winners']
        a_list = question['answers'][:25]
        minority_winners = []
        b_list = question['answers'][25:]

        # calculate categories
        categories = self.get_sorted_categories(question)
        a_list, minority_winners, b_list = self.reserve_minorities(a_list,
            minority_winners, b_list, categories, question, women_indexes)

        # TEST mark winners
        winner_pos = 0
        final_list = a_list + minority_winners + b_list
        for winner_pos, winner in enumerate(final_list):
            if winner_pos < num_winners:
                winner['winner_position'] =  winner_pos
            else:
                winner['winner_position'] =  None

        # final sort based on winners
        sorted_winners = sorted(
            [
                answer
                for answer in question['answers']
                if answer['winner_position'] is not None
            ],
            key=itemgetter('winner_position')
        )
        losers = [
            answer
            for answer in question['answers']
            if answer['winner_position'] is None
        ]

        # Add the removed first question winner
        if removed_first_question_winner is not None:
            losers.append(removed_first_question_winner)
            removed_first_question_winner['winner_position'] = None

        sorted_losers = sorted(
            losers,
            reverse=True,
            key=itemgetter('total_count')
        )
        question['answers'] = sorted_winners + sorted_losers

def podemos_desborda4(data_list, question_index=None,
    first_winner_question_index=None):
    desborda4 = Desborda4()
    desborda4.desborda(data_list, question_index, first_winner_question_index)
