# -*- coding:utf-8 -*-

from itertools import zip_longest
import sys

__BIGGEST_COUNT=1**10

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

def proportion_rounded(data_list, women_names, proportions,
                       add_missing_from_unbalanced_sex=False,
                       question_indexes=None,
                       phantom_precalc_list=[]):
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
        max_samesex = round(num_winners*(proportions[1]/total))

        if question['tally_type'] not in ["plurality-at-large"] or len(question['answers']) < 2 or question['num_winners'] < 2:
            continue

        for answer, i in zip(question['answers'], range(len(question['answers']))):
            answer['winner_position'] = None

        def filter_women(l, women_names):
          return [a for a in l if a['text'] in women_names]
        def filter_men(l, women_names):
          return [a for a in l if a['text'] not in women_names]

        women = filter_women(question['answers'], women_names)
        men = filter_men(question['answers'], women_names)
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

        base_winners = question['answers'][:num_winners]
        base_women_winners = filter_women(base_winners, women_names)
        base_men_winners = filter_men(base_winners, women_names)

        winners = base_women_winners + base_men_winners
        if len(base_women_winners) > max_samesex:
            n_diff =len(base_women_winners) - max_samesex
            winners = base_women_winners[:max_samesex] + men[:num_winners - max_samesex]
            print("too many women, len(base_women_winners)(%d) > max_samesex(%d)" % (len(base_women_winners), max_samesex), file=sys.stderr)
            if len(winners) < num_winners and add_missing_from_unbalanced_sex:
                winners += base_women_winners[max_samesex:num_winners - max_samesex - len(men) + 1]

        elif len(base_men_winners) > max_samesex:
            n_diff =len(base_men_winners) - max_samesex
            winners = base_men_winners[:max_samesex] + women[:num_winners - max_samesex]
            print("too many men, len(base_men_winners)(%d) > max_samesex(%d)" % (len(base_men_winners), max_samesex), file=sys.stderr)
            if len(winners) < num_winners and add_missing_from_unbalanced_sex:
                winners += base_men_winners[max_samesex:num_winners - max_samesex - len(women) + 1]


        if len(phantom_precalc_list) > 0:
            winners = [w for w in winners if 'is_phantom' not in w]
            question['answers'] = [a for a in question['answers'] if 'is_phantom' not in a]

        winners = sorted(winners, reverse=True, key=lambda a: a['total_count'])


        for answer, i in zip(winners, range(len(winners))):
            answer['winner_position'] = i

def parity_zip_non_iterative(data_list, women_names, question_indexes=None):
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
    WOMAN_FLAG = 44565676 # any thing, but not a string

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
                women.insert(0, WOMAN_FLAG)
        elif len(men) > 0 and men[0]['text'] == question['answers'][0]['text']:
            women.insert(0, WOMAN_FLAG)

        for woman, man in zip_longest(women, men):
            if woman is not None:
                answers_sorted.append(woman)
            if man is not None:
                answers_sorted.append(man)

        if answers_sorted[0] == WOMAN_FLAG:
            answers_sorted.pop(0)

        answers_sorted = answers_sorted + withdrawals

        for answer, i in zip(answers_sorted, range(len(answers_sorted))):
            if i < question['num_winners']:
                answer['winner_position'] = i
                lastq_is_woman = (answer['text'] in women_names)
            else:
                answer['winner_position'] = None

        question['answers'] = answers_sorted

def reorder_winners(data_list, question_index, winners_positions=[]):
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
