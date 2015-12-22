# -*- coding:utf-8 -*-

import re
import os
import json
from agora_results.pipes.base import Pipe
from agora_results.pipes import PipeReturnvalue
from jsonschema import validate

class apply_modifications(Pipe):
    
    @staticmethod
    def check_config(config):
        '''
        Implement this method to check that the input data is valid. It should
        be as strict as possible. By default, config is checked to be empty.
        '''

        '''
        TO DO: Aqui usar 'json_scheme' para comprobar que la configuración de config.json para este pipe es correcta.
        Los propiedades que puede recibir son: 
        @modifications=[] 

        En caso contrario lanzar una excepción.
        '''
        schema = {"type":"object","properties":{"modifications":{"type":"array"}},"required":["modifications"]};
 
        validate(config, schema);
        
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
        apply_modifications.apply_modifications(data_list=data, **config)
        
        return PipeReturnvalue.CONTINUE
    @staticmethod
    def apply_modifications(data_list, modifications=[]):
        '''
        Modify questions with different criteria. Example:
        
        [
          {
            "question_index": 0,
            "action": "withdraw-candidates",
            "withdrawal_policy": "match-regexp",
            "regexp": "^(?<!alcaldable:)",
            "field": "category",
            "help": "filter all candidates whose category text does not start with 'alcaldable:'"
          },
          {
            "question_index": 0,
            "action": "modify-tally-type",
            "set-tally-type": "plurality-at-large"
          }
        ]
        '''
        def read_config(data):
            questions_path = os.path.join(data['extract_dir'], "questions_json")
            with open(questions_path, 'r', encoding="utf-8") as f:
                return json.loads(f.read())
        
        def write_config(data, config):
            questions_path = os.path.join(data['extract_dir'], "questions_json")
            with open(questions_path, 'w', encoding="utf-8") as f:
                f.write(json.dumps(config))
        
        data = data_list[0]
        qjson = read_config(data)
        
        for modif in modifications:
            qindex = modif['question_index']
            if modif['action'] == "withdraw-candidates":
                if "withdrawals" not in data:
                    data['withdrawals'] = []
        
                if modif['policy'] == 'not-match':
                    field = modif['field']
                    for answer in qjson[qindex]['answers']:
                        if not re.match(modif['regex'], answer[field]):
                            data['withdrawals'].append(dict(
                                question_index=qindex,
                                answer_id=answer['id'],
                                answer_text=answer['text']))
        
                elif modif['policy'] == 'match':
                    field = modif['field']
                    for answer in qjson[qindex]['answers']:
                        if re.match(modif['regex'], answer[field]):
                            data['withdrawals'].append(dict(
                                question_index=qindex,
                                answer_id=answer['id'],
                                answer_text=answer['text']))
        
                elif modif['policy'] == 'match-url':
                    for answer in qjson[qindex]['answers']:
                        for url in answer['urls']:
                            if url['title'] != modif['title']:
                                continue
                            if re.match(modif['regex'], url['url']):
                                data['withdrawals'].append(dict(
                                    question_index=qindex,
                                    answer_id=answer['id'],
                                    answer_text=answer['text']))
        
                elif modif['policy'] == 'not-match-url':
                    for answer in qjson[qindex]['answers']:
                        match = False
                        for url in answer['urls']:
                            if url['title'] != modif['title']:
                                continue
                            match = match or re.match(modif['regex'], url['url'])
                        if not match:
                            data['withdrawals'].append(dict(
                                question_index=qindex,
                                answer_id=answer['id'],
                                answer_text=answer['text']))
        
                elif modif['policy'] == 'withdraw-winners-by-name-from-other-question':
                    dest_qindex = modif['dest_question_index']
                    for answer in data['results']['questions'][qindex]['answers']:
                        if answer["winner_position"] is None:
                            continue
        
                        answer_text = answer['text']
                        for answer2 in qjson[dest_qindex]['answers']:
                            if answer2["text"] == answer_text:
                                data['withdrawals'].append(dict(
                                    question_index=dest_qindex,
                                    answer_id=answer2['id'],
                                    answer_text=answer2['text']))
                                break
        
            elif modif['action'] == "remove-candidates":
                if "removed-candidates" not in data:
                    data['removed-candidates'] = []
        
                if modif['policy'] == 'not-match':
                    field = modif['field']
                    for answer in qjson[qindex]['answers']:
                        if not re.match(modif['regex'], answer[field]):
                            data['removed-candidates'].append(dict(
                                question_index=qindex,
                                answer_id=answer['id'],
                                answer_text=answer['text']))
        
                elif modif['policy'] == 'match':
                    field = modif['field']
                    for answer in qjson[qindex]['answers']:
                        if re.match(modif['regex'], answer[field]):
                            data['removed-candidates'].append(dict(
                                question_index=qindex,
                                answer_id=answer['id'],
                                answer_text=answer['text']))
        
                elif modif['policy'] == 'match-url':
                    for answer in qjson[qindex]['answers']:
                        for url in answer['urls']:
                            if url['title'] != modif['title']:
                                continue
                            if re.match(modif['regex'], url['url']):
                                data['removed-candidates'].append(dict(
                                    question_index=qindex,
                                    answer_id=answer['id'],
                                    answer_text=answer['text']))
        
                elif modif['policy'] == 'not-match-url':
                    for answer in qjson[qindex]['answers']:
                        match = False
                        for url in answer['urls']:
                            if url['title'] != modif['title']:
                                continue
                            match = match or re.match(modif['regex'], url['url'])
                        if not match:
                            data['removed-candidates'].append(dict(
                                question_index=qindex,
                                answer_id=answer['id'],
                                answer_text=answer['text']))
        
                elif modif['policy'] == 'remove-winners-by-name-from-other-question':
                    dest_qindex = modif['dest_question_index']
                    for answer in data['results']['questions'][qindex]['answers']:
                        if answer["winner_position"] is None:
                            continue
        
                        answer_text = answer['text']
                        for answer2 in qjson[dest_qindex]['answers']:
                            if answer2["text"] == answer_text:
                                data['removed-candidates'].append(dict(
                                    question_index=dest_qindex,
                                    answer_id=answer2['id'],
                                    answer_text=answer2['text']))
                                break
        
            elif modif['action'] == "modify-number-of-winners":
                qjson[qindex]['num_winners'] = modif['num_winners']
        
                if modif['policy'] == 'truncate-max-overload':
                    qjson[qindex]['max'] = qjson[qindex]['num_winners']
                    qjson[qindex]['truncate-max-overload'] = True
        
            elif modif['action'] == "dont-tally-question":
                data['results']['questions'][qindex]['no-tally'] = True
        
            elif modif['action'] == "set-min":
                qjson[qindex]['min'] = modif['min']
        
            elif modif['action'] == "set-title":
                qjson[qindex]['title'] = modif['title']
        
            elif modif['action'] == "set-max":
                qjson[qindex]['max'] = modif['max']
        
            elif modif['action'] == "set-tally-type":
                qjson[qindex]['tally_type'] = modif['tally-type']
        
            else:
                raise Exception("unrecognized-action %s" % modif['action'])
        
        write_config(data, qjson)
