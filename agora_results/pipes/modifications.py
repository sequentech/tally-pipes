# -*- coding:utf-8 -*-

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

        else:
            raise Exception("unrecognized-action %s" % modif['action'])

    write_config(data, qjson)
