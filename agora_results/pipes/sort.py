# -*- coding:utf-8 -*-

import json
from itertools import groupby, chain
from operator import itemgetter
from jsonschema import validate
from agora_results.pipes.base import Pipe
from agora_results.pipes import PipeReturnvalue


class sort_non_iterative(Pipe):

    _MAX = 999999999
    
    @staticmethod
    def check_config(config):
        '''
        Implement this method to check that the input data is valid. It should
        be as strict as possible. By default, config is checked to be empty.
        '''

        '''
        TO DO: Aqui usar 'json_scheme' para comprobar que la configuración de config.json para este pipe es correcta.
        Los propiedades que puede recibir son:
            @question_indexes : [List() o '']
            @withdrawals: [List() o '']
            @ties_sorting=[List() o '']
        En caso contrario lanzar una excepción.
        '''
        schema = {"type":"object","properties":{"question_indexes":{"type":"array"},"withdrawals":{"type":"array"},"ties_sorting":{"type":"array"}},"required":["question_indexes"]};
        
        validate(config, schema);
        
        if len(config) == 0:
            raise Exception("Pipe do_tallies is not correctly configured.")
        
        return True 
    
    @staticmethod
    def execute(data, config):
        '''
        Executes the pipe. Should return a PipeReturnValue. "data" is the value
        that one pipe passes to the other, and config is the specific config of
        a pipe.
        '''
        sort_non_iterative.sort_non_iterative(data_list=data, **config)
        
        return PipeReturnvalue.CONTINUE
     
    @staticmethod        
    def sort_non_iterative(data_list, question_indexes=[], withdrawals=[], ties_sorting=[], help=""):
            '''
            Sort non iterative questions of the first tally  by total_count
        
            - question_indexes are the questions this is applied to
            - withdrawals is a list of answer items that have been withdrawed.
            - ties_sorting is a list of answer items in order
        
            An answer items follows this format:
            {"question_index": 0, "answer_text": "Foo", "answer_id": 0}
            '''
            data = data_list[0]
        
            # append already listed withdrawals
            if 'withdrawals' in data:
                withdrawals = withdrawals + data['withdrawals']
        
            for q_num, question in enumerate(data['results']['questions']):
                # filter first
                if question['tally_type'] not in ["plurality-at-large", "borda", "borda-nauru", "pairwise-beta", "cup"] or\
                    q_num not in question_indexes:
                    continue
        
                # apply removals
                q_removed = []
                if "removed-candidates" in data:
                    q_removed = [
                        removed['answer_id']
                        for removed in data["removed-candidates"]
                        if removed['question_index'] == q_num]
                    question['answers'][:] = [
                        answer
                        for answer in question['answers']
                        if answer['id'] not in q_removed]
        
                q_withdrawals = list(filter(lambda w: w['question_index'] == q_num, withdrawals))
                q_withdrawals_ids = list(map(lambda w: w['answer_id'], q_withdrawals))
                q_ties_sorting = list(filter(lambda w: w['question_index'] == q_num, ties_sorting))
        
                # add default tie sort
                for answer in question['answers']:
                    answer['tie_sort']  = 0
        
                # add tie sort index to each answer
                for i, item in enumerate(q_ties_sorting):
                    item2 = question['answers'][item['answer_id']]
        
                    # first do some checks
                    assert item2['id'] == item['answer_id']
                    assert item2['text'] == item['answer_text']
                    # reverse numbering, to be compatible with total_count sorting
                    item2['tie_sort'] = len(q_ties_sorting) - i
        
        
                # sanity check withdrawals
                for item in q_withdrawals:
                    if item['answer_id'] in q_removed:
                        continue
        
                    item2 = None
                    for item_find in question['answers']:
                        if item_find['id'] == item['answer_id']:
                            item2 = item_find
                            break
        
                    # first do some checks
                    assert item2 is not None
                    assert item2['text'] == item['answer_text']
        
                # first sort by id, to have a stable sort
                question['answers'] = sorted(question['answers'], key=itemgetter('id'))
        
                # then sort by total_count, resolving ties too
                question['answers'] = sorted(question['answers'], reverse=True,
                    key=itemgetter('total_count', 'tie_sort'))
        
                # mark winners
                i = 0
                for answer in question['answers']:
                    if answer['id'] in q_withdrawals_ids or i >= question['num_winners']:
                        answer['winner_position'] = sort_non_iterative._MAX
                    else:
                        answer['winner_position'] = i
                        i += 1
        
                # final sort based on winners
                question['answers'] = sorted(
                    question['answers'],
                    key=itemgetter('winner_position'))
        
                # remove temp data
                for answer in question['answers']:
                    del answer['tie_sort']
                    if answer['winner_position'] is sort_non_iterative._MAX:
                        answer['winner_position'] = None
