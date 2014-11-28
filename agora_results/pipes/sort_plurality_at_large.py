# -*- coding:utf-8 -*-

import json
from itertools import groupby, chain

def sort_plurality_at_large(data_list, withdrawals=[], show_ties=True):
    '''
    Sort plurality_at_large questions by total_count
    '''
    data = data_list[0]
    for question in data['result']['counts']:
        if "APPROVAL" not in question['a']:
            continue
        question['answers'] = sorted(question['answers'], reverse=True,
            key=lambda a: a['total_count'])

        # find ties
        ties = [list(g) for k, g in groupby(question['answers'],
            key=lambda a: a['total_count'])]

        if len(list(chain.from_iterable(ties))) != len(ties):
            question['ties'] = ties

        if show_ties:
            for tie in ties:
                if len(tie) > 1:
                    print("\n- tie:")
                    for cand in tie:
                        print("   - %s (Q2 votes: %d)" % (
                            cand['value'], cand['total_count']))

        possible_winners = [a['value'] for a in question['answers']
            if a['value'] not in withdrawals]

        # winners without withdrawals
        question['winners'] = possible_winners[:question['num_seats']]
