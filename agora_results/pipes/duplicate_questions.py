# -*- coding:utf-8 -*-

import json
import copy
import shutil
import glob
import os
from agora_results.pipes.base import Pipe
from agora_results.pipes import PipeReturnvalue
from jsonschema import validate

class duplicate_questions(Pipe):

    
    @staticmethod
    def check_config(config):
        '''
        Implement this method to check that the input data is valid. It should
        be as strict as possible. By default, config is checked to be empty.
        '''

        '''
        TO DO: Aqui usar 'json_scheme' para comprobar que la configuración de config.json para este pipe es correcta.
        Los propiedades que puede recibir son:
        @data_list, 
        @duplications=[] 

        En caso contrario lanzar una excepción.
        '''
        schema = {"type":"object", "properties":{"modifications":{"type":"array"}}, "required":["data_list"]};
 
        validate(config, schema);
        
        if len(config) == 0:
            raise Exception("Pipe duplicate_questions is not correctly configured.")
        
        return True 
        
    
    @staticmethod
    def execute(data, config):
        '''
        Executes the pipe. Should return a PipeReturnValue. "data" is the value
        that one pipe passes to the other, and config is the specific config of
        a pipe.

        '''
        duplicate_questions.duplicate_questions(data_list=data, **config)
        
        return PipeReturnvalue.CONTINUE
    
    @staticmethod
    def duplicate_questions(data_list, duplications=[]):
        '''
        This function receives a list of questions that need to be duplicated
        and applies them in order.
    
        For example if the input "data_list" contains two questions:
    
        [<question_0>, <question_1>]
    
        And the "duplications" parameter is:
    
        [{"source_election_index": 0, "base_question_index": 0, "duplicated_question_indexes": [1]}]
    
        This means that the first question remains as is, but it is duplicated and
        the duplicated question is inserted in position 1 of the list, so in the
        end the resulting data_list is:
    
        [<question_0>, <question_0_duplicated>, <question_1>]
    
        Optionally, a duplication parameter item can also have a
        "dest_election_index" option indicating what's the destination election.
        '''
    
        def read_config(data):
            questions_path = os.path.join(data['extract_dir'], "questions_json")
            with open(questions_path, 'r', encoding="utf-8") as f:
                return json.loads(f.read())
    
        def write_config(data, config):
            questions_path = os.path.join(data['extract_dir'], "questions_json")
            with open(questions_path, 'w', encoding="utf-8") as f:
                f.write(json.dumps(config))
    
        def do_action(func, dir_path, orig_glob, orig_replace, dest_replace):
            orig_q_path = os.path.join(dir_path, orig_glob)
            orig_q_path = glob.glob(orig_q_path)[0]
            orig_q_id = orig_q_path.split('/')[-1]
            dest_q_id = orig_q_id.replace(orig_replace, dest_replace)
            dest_q_path = os.path.join(dir_path, dest_q_id)
            func(orig_q_path, dest_q_path)
    
        for dupl in duplications:
            orig_q = dupl["base_question_index"]
            orig_el = dupl["source_election_index"]
            dest_el = dupl.get("dest_election_index", dupl["source_election_index"])
            data = data_list[orig_el]
            data_dest = data_list[dest_el]
            dir_path = data_dest['extract_dir']
            qjson = read_config(data)
            qjson_dest = read_config(data_dest)
    
            for dest_q in dupl["duplicated_question_indexes"]:
                copyq = copy.deepcopy(qjson[orig_q])
                copyq['source_question_index'] = orig_q
                copyq['source_election_index'] = orig_el
                qjson_dest.insert(dest_q, copyq)
                # +1 to the indexes of the directory of the next questions
                for i in reversed(range(dest_q, len(qjson_dest) - 1)):
                    do_action(os.rename, dir_path, "%d-*" % i, "%d-" % i, "%d-" % (i + 1))
                # duplicate question dir
                do_action(shutil.copytree, dir_path, "%d-*" % orig_q, "%d-" % orig_q, "%d-" % dest_q)
            write_config(data_dest, qjson_dest)
