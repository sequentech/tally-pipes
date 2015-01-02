# -*- coding:utf-8 -*-

from itertools import zip_longest
import sys

def proportion_rounded(data_list, women_names, proportions):
    '''
    Given a list of woman names, returns a list of winners where the proportions
    of each sex is between the number provided.

    NOTE: it assumes the list of answers is already sorted.
    '''
    data = data_list[0]
    total = sum(proportions)
    proportions.sort()
    for question in data['results']['questions']:
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

        base_winners = question['answers'][:num_winners]
        base_women_winners = filter_women(base_winners, women_names)
        base_men_winners = filter_men(base_winners, women_names)

        winners = base_women_winners + base_men_winners
        if len(base_women_winners) > max_samesex:
            n_diff =len(base_women_winners) - max_samesex
            winners = base_women_winners[:max_samesex] + men[:num_winners - max_samesex]
            print("too many women, len(base_women_winners)(%d) > max_samesex(%d)" % (len(base_women_winners), max_samesex), file=sys.stderr)
        elif len(base_men_winners) > max_samesex:
            n_diff =len(base_men_winners) - max_samesex
            winners = base_men_winners[:max_samesex] + women[:num_winners - max_samesex]
            print("too many men, len(base_men_winners)(%d) > max_samesex(%d)" % (len(base_men_winners), max_samesex), file=sys.stderr)

        winners = sorted(winners, reverse=True, key=lambda a: a['total_count'])

        for answer, i in zip(winners, range(len(winners))):
            answer['winner_position'] = i

def parity_zip_plurality_at_large(data_list, women_names):
    '''
    Given a list of women names, sort the winners creating two lists, women and
    men, and then zip the list one man, one woman, one man, one woman.

    NOTE: it assumes the list of answers is already sorted.
    '''
    data = data_list[0]
    for question in data['results']['questions']:
        if "plurality-at-large" not in question['tally_type'] or len(question['answers']) == 0:
            continue

        women = [a for a in question['answers'] if a['text'] in women_names]
        men = [a for a in question['answers'] if a['text'] not in women_names]
        num_winners = question['num_winners']

        answers_sorted = []

        # check if first should be a man, add FLAG to the first item of the list
        # then remove it when processing is done
        if men[0]['text'] == question['answers'][0]['text']:
            women.insert(0, "FLAG")

        for woman, man in zip_longest(women, men):
            if woman is not None:
                answers_sorted.append(woman)
            if man is not None:
                answers_sorted.append(man)

        if answers_sorted[0] == "FLAG":
            answers_sorted.pop(0)

        for answer, i in zip(answers_sorted, range(len(answers_sorted))):
            if i < question['num_winners']:
                answer['winner_position'] = i
            else:
                answer['winner_position'] = None

        question['answers'] = answers_sorted
