# -*- coding:utf-8 -*-

import json
import copy
import shutil
import glob
import os

def duplicate_questions(data_list, duplications=[], help="this-parameter-is-ignored"):
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
        data = data_list[orig_el]
        dir_path = data['extract_dir']
        qjson = read_config(data)
        for dest_q in dupl["duplicated_question_indexes"]:
            copyq = copy.deepcopy(qjson[orig_q])
            copyq['source_question_index'] = orig_q
            qjson.insert(dest_q, copyq)
            # +1 to the indexes of the directory of the next questions
            for i in reversed(range(dest_q, len(qjson) - 1)):
                do_action(os.rename, dir_path, "%d-*" % i, "%d-" % i, "%d-" % (i + 1))
            # duplicate question dir
            do_action(shutil.copytree, dir_path, "%d-*" % orig_q, "%d-" % orig_q, "%d-" % dest_q)
        write_config(data, qjson)
