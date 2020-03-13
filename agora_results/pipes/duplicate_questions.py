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
            "duplicated_question_indexes": [1]
        }
    ]

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

    def do_action(func, orig_path, dest_path, orig_glob, orig_replace, dest_replace):
        orig_q_path = os.path.join(orig_path, orig_glob)
        orig_q_path = glob.glob(orig_q_path)[0]
        orig_q_id = orig_q_path.split('/')[-1]
        dest_q_id = orig_q_id.replace(orig_replace, dest_replace)
        dest_q_path = os.path.join(dest_path, dest_q_id)
        func(orig_q_path, dest_q_path)

    for dupl in duplications:
        orig_q = dupl["base_question_index"]
        orig_el = dupl["source_election_index"]
        dest_el = dupl.get("dest_election_index", dupl["source_election_index"])
        orig_data = data_list[orig_el]
        dest_data = data_list[dest_el]
        dest_path = dest_data['extract_dir']
        orig_path = orig_data['extract_dir']
        orig_qjson = read_config(orig_data)
        qjson_dest = read_config(dest_data)

        for dest_q in dupl["duplicated_question_indexes"]:
            copyq = copy.deepcopy(orig_qjson[orig_q])
            copyq['source_question_index'] = orig_q
            copyq['source_election_index'] = orig_el
            qjson_dest.insert(dest_q, copyq)
            # +1 to the indexes of the directory of the next questions
            for i in reversed(range(dest_q, len(qjson_dest) - 1)):
                # NOTE: we use orig_path twice because we are just renaming, it
                # is ON PURPOSE
                do_action(
                    os.rename,
                    orig_path,
                    orig_path,
                    "%d-*" % i,
                    "%d-" % i,
                    "%d-" % (i + 1)
                )

            # duplicate question dir
            do_action(
                shutil.copytree,
                orig_path,
                dest_path,
                "%d-*" % orig_q,
                "%d-" % orig_q,
                "%d-" % dest_q
            )
        write_config(dest_data, qjson_dest)
