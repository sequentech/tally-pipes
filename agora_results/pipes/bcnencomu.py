# -*- coding:utf-8 -*-

from collections import defaultdict
from agora_results.pipes.base import Pipe
from agora_results.pipes import PipeReturnvalue

def team_count_weight_correction(data_list, original_count_weight, team_count_weight, question_indexes, help=""):
    data = data_list[0]
    team_points = defaultdict(int)
    team_names = defaultdict(list)

    for question_index in question_indexes:
        for answer in data['results']['questions'][question_index]['answers']:
            team_points[answer['category']] += answer['total_count']
            team_names[answer['category']].append(answer['text'])

    for question_index in question_indexes:
        for answer in data['results']['questions'][question_index]['answers']:
            answer['total_count'] = (
                answer['total_count']*original_count_weight
                +
                team_points[answer['category']]*team_count_weight)
