# -*- coding:utf-8 -*-

def sort_approval(data):
    '''
    Sort approval questions by total_count
    '''
    for question in data['result']['counts']:
        if "APPROVAL" not in question['a']:
            continue
        question['answers'] = sorted(question['answers'],
                                     key=lambda a: a['total_count'])
