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

import re
import os
import json

def apply_modifications(data_list, modifications=[], help="this-parameter-is-ignored"):
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
