# -*- coding:utf-8 -*-

from collections import defaultdict
from agora_results.pipes.base import Pipe
from agora_results.pipes import PipeReturnvalue
from jsonschema import validate

class team_count_weight_correction(Pipe):
    
    @staticmethod
    def check_config(config):
        '''
        Implement this method to check that the input data is valid. It should
        be as strict as possible. By default, config is checked to be empty.
        '''

        '''
        TO DO: Aqui usar 'json_scheme' para comprobar que la configuración de config.json para este pipe es correcta.
        Los propiedades que puede recibir son:''] 
        @original_count_weight: 
        @team_count_weight: 
        @question_indexes : [List() o '']
        


        En caso contrario lanzar una excepción.
        '''
        
        if len(config) == 0:
            raise Exception("Pipe apply_modifications is not correctly configured.")
        
        return True 
        
    @staticmethod
    def execute(data, config):
        '''
        Executes the pipe. Should return a PipeReturnValue. "data" is the value
        that one pipe passes to the other, and config is the specific config of
        a pipe.
        '''
        team_count_weight_correction.team_count_weight_correction(data_list=data, **config)
        
        return PipeReturnvalue.CONTINUE

    @staticmethod
    def team_count_weight_correction(data_list, original_count_weight, team_count_weight, question_indexes):
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
