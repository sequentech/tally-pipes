# -*- coding:utf-8 -*-

import json
from itertools import groupby, chain

def sort_plurality_at_large(data_list, withdrawals=[]):
    '''
    Sort plurality_at_large questions of the first tally  by total_count
    '''
    data = data_list[0]
    for question in data['results']['questions']:
        if question['tally_type'] not in ["plurality-at-large"]:
            continue
        question['answers'] = sorted(question['answers'], reverse=True,
            key=lambda a: a['total_count'])