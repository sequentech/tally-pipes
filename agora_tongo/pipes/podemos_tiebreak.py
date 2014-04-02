# -*- coding:utf-8 -*-

import json
from itertools import groupby, chain

def podemos_tiebreak(data):
    '''
    Breaks ties in the second round using the first round, and viceversa
    '''
    question0 = data['result']['counts'][0]
    question1 = data['result']['counts'][1]

    if 'ties' not in question1:
        return

    # ties might also appear in question0! check that
    def mapper(g):
        lg = list(g)
        return dict(
            data=lg,
            names=list(map(lambda a: a['value'], lg))
        )
    question0_ties = [mapper(g)
                      for k, g in groupby(question0['answers'],
                    key=lambda a: a['total_count'])]

    for tie in question1['ties']:
        if len(tie) > 1:
            for cand in tie:
                # find in which question0_tie is each candidate of this tie
                # group
                #
                # the ideal situation is that each candidate of this tie group
                # is in a different tie group in question0; that would break
                # the whole tie
                cand_name = cand['value']
                t = [t['data'] for t in question0_ties if cand_name in t['names']][0]
                cand['tie_break'] = t[0]['total_count']

            tie[:] = sorted(tie, key=lambda cand2: cand2['tie_break'])

            # find if there's still subties
            subties = [list(g) for k, g in groupby(tie,
                key=lambda winner: winner['tie_break'])]

            if len(subties) != len(tie):
                for subtie in subties:
                    if len(subtie) == 1:
                        continue
                    print("- unresolved tie:")
                    for cand2 in subtie:
                        print("   - %s (Q1 votes: %d, Q2 votes: %d)" % (
                            cand2['value'], cand2['tie_break'], cand2['total_count']))
                    print("")

    question1['answers'] = list(chain.from_iterable(question1['ties']))
    winners = question1['answers'][:question1['num_seats']]
    winners = [winner['value'] for winner in winners]
    question1['winners'] = winners
