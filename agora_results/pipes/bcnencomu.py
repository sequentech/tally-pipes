# -*- coding:utf-8 -*-

from collections import defaultdict

def team_count_weight_correction(data_list, original_count_weight, team_count_weight, question_index, help=""):
    data = data_list[0]
    team_points = defaultdict(int)

    for answer in data['results']['questions'][question_index]['answers']:
        team_points[answer['category']] += answer['total_count']

    for answer in data['results']['questions'][question_index]['answers']:
        answer['total_count'] = (
            answer['total_count']*original_count_weight
            +
            team_points[answer['category']]*team_count_weight)
