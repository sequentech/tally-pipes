# -*- coding:utf-8 -*-

from itertools import zip_longest
import sys

__BIGGEST_COUNT=1**10
__WOMAN_FLAG = 445656761191

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

def __is_woman(candidate, women_names):
    '''
    Returns whether the candidate is a woman
    '''
    return candidate['text'] in women_names

def __filter_women(l, women_names, is_woman):
    return [a for a in l if is_woman(a, women_names)]

def __filter_men(l, women_names, is_woman):
    return [a for a in l if not is_woman(a, women_names)]

def __get_zip_group(l, l_men, l_women, zip_size, women_names):
    '''
    returns a list of the next group of size zip_size in parity zip order
    '''
    # create a shallow copy of the input lists, so that we don't modify
    # them. we of course asume the lists are in order
    l_men2 = list(l_men)
    l_women2 = list(l_women)

    # sanity check
    assert(len(l_men) + len(l_women) >= zip_size)

    ret_list = [l[0]]
    prev_is_woman = __is_woman(ret_list[0], women_names)
    if prev_is_woman:
        l_women2 = l_women2[1:]
    else:
        l_men2 = l_men2[1:]
    prev_is_woman = prev_is_woman and len(l_men2) > 0

    # add the remaning members in zip order when possible
    for i in range(1, zip_size):
      if prev_is_woman or len(l_women2) == 0:
          ret_list.append(l_men2.pop(0))
          prev_is_woman = False
      else:
          ret_list.append(l_women2.pop(0))
          prev_is_woman = True

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
                          url="https://agoravoting.com/api/gender/" + phantom[-1])],
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

def parity_zip_non_iterative(data_list, women_names, question_indexes=None, help=""):
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

    for qindex, question in enumerate(data['results']['questions']):
        if women_names == None:
            women_names = __get_women_names_from_question(question)
        if question_indexes is not None and qindex not in question_indexes:
            continue

        if question['tally_type'] not in ["plurality-at-large", "borda", "borda-nauru", "pairwise-beta"] or len(question['answers']) == 0:
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

    0.Partimos de la lista ordenada por voto en bruto (L), así como de la
    lista ordenada de mujeres (Lm) y la lista ordenada de hombres (Lh), que
    pueden extraerse a partir de la lista L si se tiene el parámetro 'sexo' de
    los elementos de L. Asimismo generamos una lista vacía Ld, que será la
    lista definitiva corregida.

    0.1.Definimos una función que extraiga un tramo -lista de 5- en cremallera,
    empezando por el primer elemento de L (L[0]), siguiendo por el primer
    elemento de Lm si L[0] es un hombre o por el primer elemento de Lh si L[0]
    es mujer;continuando por el segundo elemento de Lh si L[0] es un hombre o
    por el segundo elemento de Lm si L[0] es mujer, y así sucesivamente.
    Llamaremos a esta función tramo_cremallera(L,Lm,Lh).

    0.2.Definimos una segunda función que extraiga un tramo -lista de 5- de L
    en su orden natural, pero que respete la proporción 60/40 que exige la
    LOREG, el tramo debe contener por tanto 2 mujeres, 2 hombres y un quinto
    elemento que puede ser tanto una mujer como un hombre. Para ello podemos
    sacar a los dos hombres y las dos mujeres más votadas y en último lugar al
    elemento más votado de la lista restante y luego reordenar el tramo por
    número de votos, o utilizar cualquier otro procedimiento análogo.
    Llamaremos a esta función tramo_loreg (L,Lm,Lh).

    0.3.Definimos una función que evalúe un tramo -lista de 5- y devuelva un
    booleano. Si en el tramo en cuestión alguna mujer ocupa un puesto inferior
    a un hombre teniendo ésta un mayor número de votos que él, entonces la
    función devolverá FALSE; en cualquier otro caso devolverá TRUE. Llamaremos
    a la función check (tramo).

    1.Extraemos el tramo cremallera de los puestos iniciales de la lista,
    utilizando tramo_cremallera(L,Lm,Lh).

    2.Aplicamos la función check sobre el tramo resultante de (1):

    2a.Si la función devuelve TRUE, entonces nos quedamos con el tramo
    resultante de (1).

    2b.Si la función devuelve FALSE, entonces extraemos un nuevo tramo de L,
    utilizando tramo_loreg (L,Lm,Lh) y desechamos el tramo anterior.

    3.Añadimos el tramo en cuestión a Ld y borramos los elementos del tramo de
    L, Lm y Lh.

    4.Volvemos a (1) a no ser que L tenga menos de 5 elementos.

    5.Ordenamos en cremallera los elementos restantes de L y los añadimos al
    final de Ld.
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

    # check the question has an allowed tally type
    allowed_tally_types = ["plurality-at-large", "borda", "borda-nauru",
        "pairwise-beta"]
    # group size is calculated summing the proportions, as we asume this can be
    # done
    group_size = sum(proportions)

    for q_index, question in enumerate(data_list[0]['results']['questions']):
        if q_index not in question_indexes:
            continue

        if question['tally_type'] not in allowed_tally_types:
            raise Exception("invalid tally_type")
        women_names = __get_women_names_from_question(question)

        # lists of remaining candidates, women and men:
        candidates = list(question['answers'])
        women = __filter_women(candidates, women_names, __is_woman)
        men = __filter_men(candidates, women_names, __is_woman)

        # the number of groups to create equals to the number of iterations of
        # the main loop
        num_groups = int(question['num_winners'] / group_size)
        final_group_size = question['num_winners'] % group_size

        # main loop
        winners_l = []
        for i in range(num_groups):
            # use either a zip group or a proportional group, depending on the check
            group = __get_zip_group(candidates, men, women, group_size, women_names)
            if not parity_check(group, women_names):
                group = __get_proportional_group(candidates, men, women, proportions)

            # some checks
            assert(len(group) == group_size)
            assert(len([a for a in group if a in winners_l]) == 0)

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