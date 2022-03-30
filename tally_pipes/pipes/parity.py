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

from itertools import zip_longest
from operator import itemgetter
import sys

__BIGGEST_COUNT=1**10
__WOMAN_FLAG = 445656761191


__NON_ITERATIVE_TYPES = [
    "cumulative",
    "plurality-at-large",
    "borda",
    "borda-nauru",
    "pairwise-beta",
    "desborda",
    "desborda2",
    "desborda3"
]

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
            if url['url'] == 'https://sequentech.io/api/gender/M':
                women_names.append(answer['text'])
                break
    return women_names

def __is_woman(candidate, women_names):
    '''
    Returns whether the candidate is a woman
    '''
    return candidate['text'] in women_names

def __filter_women(l, women_names, is_woman):
    return [a for a in l if is_woman(a, women_names)]

def __filter_men(l, women_names, is_woman):
    return [a for a in l if not is_woman(a, women_names)]

def __get_zip_group(group, women_names, is_woman):
    '''
    reorders a group in zip sex order, putting first the first person of the
    most numerous sex in the group
    '''
    # create a shallow copy of the input lists, so that we don't modify
    # them. we of course asume the lists are in order
    men = __filter_women(group, women_names, is_woman)
    women = __filter_women(group, women_names, is_woman)

    first = women
    second = men
    if len(men) > len(women):
      first = men
      second = women

    ret_list = []
    for a, b in zip_longest(first, second):
        if a is not None:
            ret_list.append(a)
        if b is not None:
            ret_list.append(b)

    return ret_list

def __get_proportional_group(l, l_men, l_women, proportions):
    '''
    returns a list of zip_size size of candidates where the proportions
    of each sex is between the number provided.

    asumes the lists are in order and proportions normalized.
    '''
    # create a shallow copy of the input lists, so that we don't modify
    # them. we of course asume the lists are in order
    l_men2 = list(l_men)
    l_women2 = list(l_women)

    min_split = min(proportions)
    max_diff = max(proportions) - min(proportions)
    ret_list = l_men2[:min_split] + l_women2[:min_split]

    # remove the used elements from the sublists
    l_men2 = [a for a in l_men2 if a not in ret_list]
    l_women2 = [a for a in l_women2 if a not in ret_list]
    candidates = [a for a in l if a not in ret_list]

    # add remaining candidates
    candidates = sorted(candidates, reverse=True, key=itemgetter('total_count'))

    ret_list = ret_list + candidates[:max_diff]
    return sorted(ret_list, reverse=True, key=itemgetter('total_count'))

def proportion_rounded(data_list, women_names, proportions,
                       add_missing_from_unbalanced_sex=False,
                       question_indexes=None,
                       phantom_precalc_list=[], help=""):
    '''
    Given a list of woman names, returns a list of winners where the proportions
    of each sex is between the number provided.

    Use phantom_precalc_list to add at the begning of the list of winners on
    computation time a list of candidates with specific sexes. For example, use
    ['H', 'M'] to add a Man first and a Women in second place during
    computation. It's a phantom list because it's only used for computation
    purposes: the phantom elements will never be shown on the results.

    NOTE: it assumes the list of answers is already sorted.
    '''
    data = data_list[0]
    total = sum(proportions)
    proportions.sort()

    for qindex, question in enumerate(data['results']['questions']):
        if women_names == None:
            women_names = __get_women_names_from_question(question)

        if question_indexes is not None and qindex not in question_indexes:
            continue

        num_winners = question['num_winners']

        if question['tally_type'] not in ["plurality-at-large"] or len(question['answers']) < 2 or question['num_winners'] < 2:
            continue

        for answer, i in zip(question['answers'], range(len(question['answers']))):
            answer['winner_position'] = None

        def filter_women(l, women_names):
          return [a for a in l if a['text'] in women_names]
        def filter_men(l, women_names):
          return [a for a in l if a['text'] not in women_names]

        num_winners = question['num_winners']

        # add the elements from phantom_precalc_list
        if len(phantom_precalc_list) > 0:
            num_winners += len(phantom_precalc_list)
            women_names.append("___WOMAN_PHANTOM_M")

            def mapped(el):
                if el == 'H':
                    return "___MAN_PHANTOM_H" # last char used later in url
                else:
                    return "___WOMAN_PHANTOM_M"

            phantom_l = [mapped(el) for el in phantom_precalc_list]

            for i, phantom in enumerate(phantom_l):
                question['answers'].insert(
                  i,
                  dict(
                      text=phantom,
                      is_phantom=True,
                      urls=[dict(
                          title="Gender",
                          url="https://sequentech.io/api/gender/" + phantom[-1])],
                      total_count=__BIGGEST_COUNT - i))

        women = filter_women(question['answers'], women_names)
        men = filter_men(question['answers'], women_names)
        max_samesex = round(num_winners*(proportions[1]/total))
        base_winners = question['answers'][:num_winners]
        base_women_winners = filter_women(base_winners, women_names)
        base_men_winners = filter_men(base_winners, women_names)

        winners = base_women_winners + base_men_winners
        if len(base_women_winners) > max_samesex:
            n_diff =len(base_women_winners) - max_samesex
            winners = base_women_winners[:max_samesex] + men[:num_winners - max_samesex]
            if len(winners) < num_winners and add_missing_from_unbalanced_sex:
                winners += base_women_winners[max_samesex:num_winners - max_samesex - len(men) + 1]

        elif len(base_men_winners) > max_samesex:
            n_diff =len(base_men_winners) - max_samesex
            winners = base_men_winners[:max_samesex] + women[:num_winners - max_samesex]
            if len(winners) < num_winners and add_missing_from_unbalanced_sex:
                winners += base_men_winners[max_samesex:num_winners - max_samesex - len(women) + 1]

        if len(phantom_precalc_list) > 0:
            winners = [w for w in winners if 'is_phantom' not in w]
            question['answers'] = [a for a in question['answers'] if 'is_phantom' not in a]

        winners = sorted(winners, reverse=True, key=lambda a: a['total_count'])


        for answer, i in zip(winners, range(len(winners))):
            answer['winner_position'] = i

def parity_zip_non_iterative(data_list, women_names=None, question_indexes=None, help=""):
    '''
    Given a list of women names, sort the winners creating two lists, women and
    men, and then zip the list one man, one woman, one man, one woman.

    if question_indexes is set, then the zip is applied to that list of
    questions. If not, then it's applied to all the non-iterative questions .

    When zip is applied to multiple questions, it's applied as if all the
    winners were in a single question. This means that if the previous question
    last winner is a women, next question first winner will be a man and so on.

    NOTE: it assumes the list of answers is already sorted.
    '''
    data = data_list[0]
    lastq_is_woman = None
    women_names = []

    for qindex, question in enumerate(data['results']['questions']):
        women_names = list(set(women_names + __get_women_names_from_question(question)))
        if question_indexes is not None and qindex not in question_indexes:
            continue

        if question['tally_type'] not in __NON_ITERATIVE_TYPES or len(question['answers']) == 0:
            continue

        withdrawal_names = [w["answer_text"] for w in data.get("withdrawals", [])
                            if w['question_index'] == qindex]
        withdrawals = [a for a in question['answers'] if a['text'] in withdrawal_names]
        women = [a for a in question['answers']
          if a['text'] in women_names and a['text'] not in withdrawal_names]
        men = [a for a in question['answers']
          if a['text'] not in women_names and a['text'] not in withdrawal_names]
        num_winners = question['num_winners']

        answers_sorted = []

        # check if first should be a man, add FLAG to the first item of the list
        # then remove it when processing is done
        if lastq_is_woman is not None:
            if lastq_is_woman == True:
                women.insert(0, __WOMAN_FLAG)
        elif len(men) > 0 and men[0]['text'] == question['answers'][0]['text']:
            women.insert(0, __WOMAN_FLAG)

        for woman, man in zip_longest(women, men):
            if woman is not None:
                answers_sorted.append(woman)
            if man is not None:
                answers_sorted.append(man)

        if answers_sorted[0] == __WOMAN_FLAG:
            answers_sorted.pop(0)

        answers_sorted = answers_sorted + withdrawals

        for answer, i in zip(answers_sorted, range(len(answers_sorted))):
            if i < question['num_winners']:
                answer['winner_position'] = i
                lastq_is_woman = (answer['text'] in women_names)
            else:
                answer['winner_position'] = None

        question['answers'] = answers_sorted

def reorder_winners(data_list, question_index, winners_positions=[], help=""):
    '''
    Generic function to set winners based on external criteria
    '''
    data = data_list[0]

    def get_winner_position(answer):
        pos = None
        for position in winners_positions:
            if position['text'] == answer['text'] and\
                position['id'] == answer['id']:
                return position['winner_position']
        return None

    for question in data['results']['questions'][question_index]:
        for answer in question['answers']:
            answer['winner_position'] = get_winner_position(answer, qid)


def podemos_parity2_loreg_zip_non_iterative(
    data_list,
    question_index,
    proportions=[3,2],
    first_pair_proportions=[2,2],
    help=""):
    '''
    Asume que:
     - la paridad viene explícita en la pregunta en forma de urls de tipo
       "Gender".
     - el tamaño de cada grupo es igual a la suma de las proporciones

    Implementa este algoritmo:

    Se coge un grupo de 5, se mira mujer a mujer si se puede ordenar a las
    mujeres por puntos para mejorar su posición, en cuyo caso se hace.
    '''

    data = data_list[0]
    women_names = []
    assert(len(data_list[0]['results']['questions']) > question_index)
    question = data_list[0]['results']['questions'][question_index]

    group_size = sum(proportions)
    init_group_size = sum(first_pair_proportions)
    assert(len(question['answers']) >= init_group_size)

    if question['tally_type'] not in __NON_ITERATIVE_TYPES:
        raise Exception("invalid tally_type")
    women_names = __get_women_names_from_question(question)

    # lists of candidates, women and men:
    candidates = list(question['answers'])
    women = __filter_women(candidates, women_names, __is_woman)
    men = __filter_men(candidates, women_names, __is_woman)

    def process_group(group):
        '''
        Creates subgroups in which there's only one woman and it's sorted by
        points if it benefits the woman.
        '''
        woman_indexes = [
            i
            for i, c in enumerate(group)
            if __is_woman(c, women_names)
        ]
        if len(woman_indexes) == 0:
            return group

        final_group = []

        last_woman_final_index = -1
        last_woman_index = -1

        for woman_index in woman_indexes:
            subgroup = final_group[last_woman_final_index+1:] + group[last_woman_index+1:woman_index+1]
            assert(len(subgroup) > 0)
            woman_subgroup_index = len(subgroup) - 1
            woman = subgroup[-1]
            sorted_subgroup = sorted(subgroup, reverse=True,
                key=itemgetter('total_count'))

            if sorted_subgroup.index(woman) < woman_subgroup_index:
                final_group = final_group[:last_woman_final_index+1] + sorted_subgroup
            else:
                final_group = final_group[:last_woman_final_index+1] + subgroup

            last_woman_final_index = final_group.index(woman)
            last_woman_index = woman_index

        # add final group of men if any, those don't
        # need reordering
        final_group.extend(group[woman_indexes[-1]+1:])

        return final_group

    final_list = [] + process_group(candidates[:init_group_size])
    num_winners = question['num_winners']
    next_group = []
    for candidate in candidates[init_group_size:num_winners]:
        next_group.append(candidate)
        if len(next_group) == group_size:
            final_group = process_group(next_group)
            next_group = []
            final_list.extend(final_group)

    final_list.extend(process_group(next_group))
    final_list.extend(candidates[num_winners:])
    question['answers'] = final_list

    # set winners
    for i, candidate in enumerate(question['answers']):
        if i < num_winners:
            candidate['winner_position'] = i
        else:
            candidate['winner_position'] = None

def podemos_parity_loreg_zip_non_iterative(data_list, question_indexes,
                                           proportions=[3,2], help=""):
    '''
    Asume que:
     - la paridad viene explícita en la pregunta en forma de urls de tipo
       "Gender".
     - la lista de candidatos ha sido previamente ordenada según el número de
       votos en orden decreciente.
     - el tamaño de cada grupo es igual a la suma de las proporciones

    Implementa este algoritmo:

    Previo: El mínimo de hombres y mujeres por grupo es 2. El de mujeres sube a
    3 si en el grupo anterior había 3 hombres.

    1. Se coge un grupo de 5, se mira si hay menos mujeres u hombres de los que
    debería y se arregla si hace falta (se añaden mujeres u hombres por el final
    hasta alcanzar el mínimo).

    2. Se aplica cremallera en el grupo resultante (HMHMH o MHMHM según el
    número de mujeres y hombres).

    3. En el primer grupo, si al aplicar cremallera en el paso 2 se redujese el
    número de mujeres, se deja el grupo como estaba al aplicar el paso 1.
    '''
    def parity_check(group, women_names):
        '''
        Evals a sorted list of candidates and returns a boolean. If inside the
        group there is any woman that is in a latter position than a man and
        the woman has a bigger score, return False. Returns True otherwise.

        Asumes the group is sorted in descending score, although it might have
        some parity corrections.
        '''
        prev_man = None
        for cand in group:
            if not __is_woman(cand, women_names):
                prev_man = cand
                continue

            if not prev_man:
                continue

            # it's a woman and there's a previous man, then check the score
            if prev_man['total_count'] < cand['total_count']:
                return False

        return True

    # group size is calculated summing the proportions, as we asume this can be
    # done
    group_size = sum(proportions)

    for q_index, question in enumerate(data_list[0]['results']['questions']):
        if q_index not in question_indexes:
            continue

        if question['tally_type'] not in __NON_ITERATIVE_TYPES:
            raise Exception("invalid tally_type")
        women_names = __get_women_names_from_question(question)

        # lists of remaining candidates, women and men:
        candidates = list(question['answers'])
        women = __filter_women(candidates, women_names, __is_woman)
        men = __filter_men(candidates, women_names, __is_woman)

        # the number of groups to create equals to the number of iterations of
        # the main loop
        num_groups = int(question['num_winners'] / group_size)

        # main loop
        winners_l = []
        for i in range(num_groups):
            corrected_group = __get_proportional_group(
                candidates, men, women, proportions)
            zip_group = __get_zip_group(corrected_group, women_names,
                __is_woman)

            # update winners list, candidates, women and men
            winners_l = winners_l + group
            candidates = [cand for cand in candidates if cand not in winners_l]
            women = __filter_women(candidates, women_names, __is_woman)
            men = __filter_men(candidates, women_names, __is_woman)

        # apply final group if need be, as a zip list
        if final_group_size > 0:
            group = __get_zip_group(candidates, men, women, final_group_size, women_names)
            winners_l = winners_l + group

        # finally, set the winner_index to the candidates based on the winners_l
        # ordered items
        for cand in question['answers']:
            cand['winner_position'] = None
        for i, cand in enumerate(winners_l):
            cand['winner_position'] = i

if __name__ == '__main__':
    '''
    executes some unittests on podemos_parity_loreg_zip_non_iterative.
    '''
    def generate_test_data(sexes):
        '''
        Given a string of sexes in order (for example "HHHMMH"), generates a test
        election data to be used with podemos_parity_loreg_zip_non_iterative.
        '''
        q = {
          "tally_type": "plurality-at-large",
          "num_winners": len(sexes),
          "answers": [
            {
              "total_count": len(sexes) + 1 - i,
              "text": "cand #%d" % i,
              "id": i,
              "urls": [
                {
                  "title": "Gender",
                  "url": "https://sequentech.io/api/gender/" + sex
                }
              ]
            }
            for i, sex in enumerate(sexes)
          ]
        }

        return {
          "results": {
            "questions": [q]
          }
        }

    def get_output_sexes(data):
        '''
        Given a question similar to the one outputed from
        podemos_parity_loreg_zip_non_iterative, returns the sexes string from the
        results.
        '''
        q = data['results']['questions'][0]
        return "".join([
            a['urls'][0]['url'][-1]
            for a in sorted(q['answers'], key=itemgetter('winner_position'))])

    def print_groups(sexes, group_size=5):
        '''
        separate groups with a point
        '''
        ret = ""
        for i, sex in enumerate(sexes[::-1]):
            if i % group_size == 4:
                ret = ret + sex + "."
            else:
                ret = ret + sex

        return ret

    test_data = [
      ["MHHMM", "MHMHMM"]
    ]

    for initial_sex_order, expected_results_order in test_data:
        data = generate_test_data(initial_sex_order)
        podemos_parity_loreg_zip_non_iterative([data], [0])
        output = get_output_sexes(data)
        if output != expected_results_order:
            print("failed test_data: input(%s) -> expected(%s) but got(%s)" % (
                print_groups(initial_sex_order),
                print_groups(expected_results_order),
                print_groups(output)))
