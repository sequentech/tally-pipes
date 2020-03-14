# -*- coding:utf-8 -*-

# This file is part of agora-results.
# Copyright (C) 2014-2016  Agora Voting SL <agora@agoravoting.com>

# agora-results is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License.

# agora-results  is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with agora-results.  If not, see <http://www.gnu.org/licenses/>.

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

    [
        {
            "source_election_index": 0,
            "base_question_index": 0,
            "duplicated_question_indexes": [1],
            "zero_plaintexts": false
        }
    ]

    This means that the first question remains as is, but it is duplicated and
    the duplicated question is inserted in position 1 of the list, so in the
    end the resulting data_list is:

    [<question_0>, <question_0_duplicated>, <question_1>]

    Optionally, a duplication parameter item can also have a
    "dest_election_index" option indicating what's the destination election.
    '''
    elections_by_id = dict()
    for dindex, data in enumerate(data_list):
        if 'id' not in data:
            data['id'] = dindex
    
        elections_by_id[data['id']] = data

    def read_config(data):
        questions_path = os.path.join(data['extract_dir'], "questions_json")
        with open(questions_path, 'r', encoding="utf-8") as f:
            return json.loads(f.read())

    def write_config(data, config):
        questions_path = os.path.join(data['extract_dir'], "questions_json")
        with open(questions_path, 'w', encoding="utf-8") as f:
            f.write(json.dumps(config))

    def do_action(
        func,
        orig_path,
        dest_path,
        orig_glob,
        orig_replace,
        dest_replace
    ):
        orig_q_path = os.path.join(orig_path, orig_glob)
        orig_q_path = glob.glob(orig_q_path)[0]
        orig_q_id = orig_q_path.split('/')[-1]
        dest_q_id = orig_q_id.replace(orig_replace, dest_replace)
        dest_q_path = os.path.join(dest_path, dest_q_id)
        func(orig_q_path, dest_q_path)

    for dupl in duplications:
        orig_q_index = dupl["base_question_index"]
        orig_el_index = dupl["source_election_index"]
        dest_el_index = dupl.get("dest_election_index", orig_el_index)
        zero_plaintexts = dupl.get("zero_plaintexts", False)

        orig_data = elections_by_id[orig_el_index]
        dest_data = elections_by_id[dest_el_index]
        dest_path = dest_data['extract_dir']
        orig_path = orig_data['extract_dir']
        orig_qjson = read_config(orig_data)
        qjson_dest = read_config(dest_data)

        for dest_q_index in dupl["duplicated_question_indexes"]:
            copy_q = copy.deepcopy(orig_qjson[orig_q_index])
            copy_q['source_question_index'] = orig_q_index
            copy_q['source_election_index'] = orig_el_index
            qjson_dest.insert(dest_q_index, copy_q)
            # +1 to the indexes of the directory of the next questions
            for i in reversed(range(dest_q_index, len(qjson_dest) - 1)):
                # NOTE: we use orig_path twice because we are just renaming, it
                # is ON PURPOSE
                do_action(
                    func=os.rename,
                    orig_path=orig_path,
                    dest_path=orig_path,
                    orig_glob="%d-*" % i,
                    orig_replace="%d-" % i,
                    dest_replace="%d-" % (i + 1)
                )

            # duplicate question dir
            do_action(
                func=shutil.copytree,
                orig_path=orig_path,
                dest_path=dest_path,
                orig_glob="%d-*" % orig_q_index,
                orig_replace="%d-" % orig_q_index,
                dest_replace="%d-" % dest_q_index
            )

            # empty plaintexts if needed
            if zero_plaintexts:
                plaintexts_glob = os.path.join(
                    dest_path, 
                    "%d-*" % dest_q_index,
                    "plaintexts_json"
                )
                plaintexts_path = glob.glob(plaintexts_glob)[0]
                os.unlink(plaintexts_path)
                open(plaintexts_path, 'a').close()
                
        write_config(dest_data, qjson_dest)
