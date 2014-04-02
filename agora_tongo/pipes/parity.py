# -*- coding:utf-8 -*-

from itertools import zip_longest

def parity_zip_approval(data, women_names):
    '''
    Given a list of women names, sort the winners creating two lists, women and
    men, and then zip the list one man, one woman, one man, one woman.

    NOTE: it assumes the list of answers is already sorted.
    '''

    for question in data['result']['counts']:
        if "APPROVAL" not in question['a']:
            continue
        women = [a for a in question['answers'] if a['value'] in women_names]
        men = [a for a in question['answers'] if a['value'] not in women_names]
        num_winners = question['num_seats']

        if len(women) == 0:
            question['winners'] = [a['value'] for a in men[:num_winners]]
            return

        # first is a women
        answers_sorted = []
        if women[0]['value'] == question['answers'][0]['value']:
            for woman, man in zip_longest(women, men):
                if woman is not None:
                    answers_sorted.append(woman)
                if man is not None:
                    answers_sorted.append(man)
        else:
            for man, woman in zip_longest(men, women):
                if man is not None:
                    answers_sorted.append(man)
                if woman is not None:
                    answers_sorted.append(woman)
        question['answers'] = answers_sorted

        question['winners'] = [a['value'] for a in answers_sorted[:num_winners]]
